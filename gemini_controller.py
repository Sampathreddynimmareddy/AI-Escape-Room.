
import os
from pathlib import Path
import tomllib
from google import genai


# Load API key from Streamlit secrets or environment variable.
secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
api_key = None

if secrets_path.exists():
    with open(secrets_path, "rb") as file:
        secrets = tomllib.load(file)
    api_key = secrets.get("GEMINI_API_KEY")

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found.")


client = genai.Client(api_key=api_key)
MODEL = "gemini-3.5-flash-lite"


ALLOWED_ACTIONS = {
    "MOVE_TO_CABINET",
    "MOVE_TO_TABLE",
    "MOVE_TO_TERMINAL",
    "MOVE_TO_PANEL",
    "MOVE_TO_EXIT",
    "COLLECT_CHEMICAL",
    "EXAMINE_NOTEBOOK",
    "UNLOCK_TERMINAL",
    "READ_TERMINAL",
    "USE_CONTROL_PANEL",
    "OPEN_EXIT",
    "RESTART_GAME",
    "UNKNOWN",
}


def interpret_command(player_command):

    command = player_command.lower().strip()

    # Prevent negative commands from triggering actions.
    negative_phrases = [
        "don't open",
        "do not open",
        "dont open",
        "never open",
    ]

    if any(phrase in command for phrase in negative_phrases):
        return "UNKNOWN"

    # Directly recognize commands to open the emergency exit.
    open_exit_phrases = [
        "open the emergency exit",
        "open emergency exit",
        "open the exit",
        "open exit",
        "unlock the emergency exit",
        "unlock emergency exit",
        "unlock the exit",
        "unlock exit",
        "escape",
        "let me out",
        "open the door",
    ]

    if any(phrase in command for phrase in open_exit_phrases):
        return "OPEN_EXIT"

    # Directly recognize movement towards the exit.
    move_exit_phrases = [
        "go to the exit",
        "go to exit",
        "move to the exit",
        "move to exit",
        "walk to the exit",
        "walk to exit",
        "approach the exit",
        "approach exit",
        "go near the exit",
    ]

    if any(phrase in command for phrase in move_exit_phrases):
        return "MOVE_TO_EXIT"

    # Ask Gemini to interpret other commands.
    prompt = f"""
You interpret commands for a fictional escape-room game.

Choose exactly one action from:
{', '.join(sorted(ALLOWED_ACTIONS))}

Examples:
- go to the cabinet -> MOVE_TO_CABINET
- go to the research table -> MOVE_TO_TABLE
- go to the computer -> MOVE_TO_TERMINAL
- go to the control panel -> MOVE_TO_PANEL
- go to the exit -> MOVE_TO_EXIT
- collect/search the chemicals -> COLLECT_CHEMICAL
- inspect/use the notebook -> EXAMINE_NOTEBOOK
- unlock the computer -> UNLOCK_TERMINAL
- show terminal clues -> READ_TERMINAL
- use the control panel -> USE_CONTROL_PANEL
- open the emergency exit -> OPEN_EXIT
- restart -> RESTART_GAME

Player command: {player_command}

Return only one action name from the allowed list.
Do not invent actions.
Do not claim that an action succeeded.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        action = (response.text or "").strip().upper()

        # Find a valid action even if Gemini adds extra text.
        for allowed_action in ALLOWED_ACTIONS:
            if allowed_action in action:
                return allowed_action

        return "UNKNOWN"

    except Exception as error:
        print("Gemini interpretation error:", error)
        return "UNKNOWN"


def validate_action(action, game_state):

    movement_actions = {
        "MOVE_TO_CABINET",
        "MOVE_TO_TABLE",
        "MOVE_TO_TERMINAL",
        "MOVE_TO_PANEL",
        "MOVE_TO_EXIT",
    }

    if action in movement_actions:
        return True, "Movement request accepted."

    if action == "COLLECT_CHEMICAL":

        if (
            game_state["near_cabinet"]
            and not game_state.get("cabinet_searched", False)
        ):
            return True, "Chemical collection allowed."

        if game_state.get("cabinet_searched", False):
            return False, "You have already collected the four chemicals."

        return False, "Move close to the cabinet before collecting the chemicals."

    if action == "EXAMINE_NOTEBOOK":

        if not game_state.get("cabinet_searched", False):
            return False, "Search the Chemical Cabinet first."

        if not game_state["near_table"]:
            return False, "Move close to the Research Table first."

        if game_state.get("notebook_failed", False):
            return False, "The notebook message has vanished. Restart the game."

        if game_state["message_revealed"]:
            return False, "The notebook password has already been revealed."

        return True, "Notebook puzzle opened."

    if action == "UNLOCK_TERMINAL":

        if game_state["near_terminal"] and game_state["message_revealed"]:
            return True, "Terminal interaction allowed."

        return False, "Reveal the notebook password and approach the terminal."

    if action == "READ_TERMINAL":

        if game_state["near_terminal"] and game_state["terminal_unlocked"]:
            return True, "Terminal clues available."

        return False, "Unlock the terminal and move close to it first."

    if action == "USE_CONTROL_PANEL":

        if game_state["near_panel"] and game_state["terminal_unlocked"]:
            return True, "Control panel interaction allowed."

        return False, "Unlock the terminal and approach the control panel."

    if action == "OPEN_EXIT":

        if (
            game_state["near_exit"]
            and game_state["code_accepted"]
            and game_state["sequence_accepted"]
        ):
            return True, "Exit interaction allowed."

        return False, "Complete both security challenges and approach the exit."

    if action == "RESTART_GAME":
        return True, "Restart allowed."

    return False, "I could not understand that command. Try rephrasing it."


def game_master_response(
    player_command,
    action,
    outcome,
    game_state
):

    prompt = f"""
You are the calm AI Game Master of a fictional chemical-lab escape room.

Respond in one or two short sentences.
Python has already decided the result. Treat it as authoritative.

Never claim success if the result says failure.
Never reveal passwords, puzzle answers, access codes, or sequences.
Do not invent changes to inventory, puzzles, doors, or player position.

Player command: {player_command}
Action: {action}
Authoritative Python result: {outcome}

Progress:
Cabinet searched: {game_state.get('cabinet_searched')}
Notebook solved: {game_state.get('message_revealed')}
Terminal unlocked: {game_state.get('terminal_unlocked')}
Access code solved: {game_state.get('code_accepted')}
Sequence solved: {game_state.get('sequence_accepted')}

Keep it under 35 words.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        result = (response.text or "").strip()

        return result[:300] if result else outcome

    except Exception as error:
        print("Game Master response error:", error)
        return outcome


if __name__ == "__main__":

    command = input("Enter a game command: ")

    print("Gemini interpreted:", interpret_command(command))




