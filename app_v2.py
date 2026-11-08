
import pygame
import sys

from gemini_controller import (
    interpret_command,
    validate_action,
    game_master_response
)

pygame.init()

# ==================================================
# WINDOW
# ==================================================

WIDTH, HEIGHT = 1000, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Escape Room - Chemical Lab Disaster")
clock = pygame.time.Clock()

# ==================================================
# COLORS AND FONTS
# ==================================================

DARK = (25, 30, 40)
WALL = (65, 75, 90)
FLOOR = (45, 55, 65)
WHITE = (245, 245, 245)
GREEN = (40, 180, 100)
BLUE = (40, 120, 200)
YELLOW = (240, 200, 50)
RED = (200, 60, 60)
PANEL_BG = (35, 43, 55)

font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)
tiny_font = pygame.font.SysFont("Arial", 15)
big_font = pygame.font.SysFont("Arial", 48)

# ==================================================
# PLAYER AND LAB OBJECTS
# ==================================================

player_x = 520
player_y = 400
player_speed = 4
player_size = 30

cabinet_rect = pygame.Rect(370, 150, 120, 150)
table_rect = pygame.Rect(120, 180, 170, 90)
terminal_rect = pygame.Rect(650, 180, 150, 90)
panel_rect = pygame.Rect(650, 370, 130, 80)
exit_rect = pygame.Rect(850, 150, 70, 180)

CHEMICALS = [
    "Lumen-12",
    "Crimson-4",
    "Vitra-6",
    "Nexon-2"
]

# ==================================================
# GAME STATE
# ==================================================

chemical_collected = False
cabinet_searched = False

wrong_chemical_attempts = 0
notebook_failed = False
message_revealed = False

terminal_unlocked = False
terminal_open = False

code_accepted = False
sequence_accepted = False

exit_open = False
game_won = False

inventory = []

message = "Explore the laboratory."

input_mode = None
input_text = ""
input_feedback = ""

command_mode = False
command_text = ""

move_target = None


# ==================================================
# HELPER: DRAW WRAPPED TEXT
# ==================================================

def draw_wrapped_text(surface, text, font_object, color,
                      x, y, max_width, line_spacing=4):

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word

        if font_object.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for line in lines:
        rendered = font_object.render(line, True, color)
        surface.blit(rendered, (x, y))
        y += rendered.get_height() + line_spacing

    return y


# ==================================================
# RESET GAME
# ==================================================

def reset_game():
    global player_x, player_y
    global chemical_collected, cabinet_searched
    global wrong_chemical_attempts, notebook_failed
    global message_revealed
    global terminal_unlocked, terminal_open
    global code_accepted, sequence_accepted
    global exit_open, game_won
    global inventory, message
    global input_mode, input_text, input_feedback
    global command_mode, command_text, move_target

    player_x = 520
    player_y = 400

    chemical_collected = False
    cabinet_searched = False

    wrong_chemical_attempts = 0
    notebook_failed = False
    message_revealed = False

    terminal_unlocked = False
    terminal_open = False

    code_accepted = False
    sequence_accepted = False

    exit_open = False
    game_won = False

    inventory = []

    message = "Explore the laboratory."

    input_mode = None
    input_text = ""
    input_feedback = ""

    command_mode = False
    command_text = ""

    move_target = None


# ==================================================
# GAME STATE FOR GEMINI VALIDATION
# ==================================================

def get_game_state():

    player_rect = pygame.Rect(
        int(player_x),
        int(player_y),
        player_size,
        player_size
    )

    center = pygame.Vector2(player_rect.center)

    return {
        "near_cabinet": center.distance_to(
            pygame.Vector2(cabinet_rect.center)
        ) < 110,

        "near_table": center.distance_to(
            pygame.Vector2(table_rect.center)
        ) < 110,

        "near_terminal": center.distance_to(
            pygame.Vector2(terminal_rect.center)
        ) < 110,

        "near_panel": center.distance_to(
            pygame.Vector2(panel_rect.center)
        ) < 110,

        "near_exit": center.distance_to(
            pygame.Vector2(exit_rect.center)
        ) < 110,

        "chemical_collected": chemical_collected,
        "cabinet_searched": cabinet_searched,
        "wrong_chemical_attempts": wrong_chemical_attempts,
        "notebook_failed": notebook_failed,
        "message_revealed": message_revealed,
        "terminal_unlocked": terminal_unlocked,
        "code_accepted": code_accepted,
        "sequence_accepted": sequence_accepted
    }


# ==================================================
# OPEN NOTEBOOK CHEMICAL SELECTION
# ==================================================

def open_chemical_selection():
    global input_mode, input_text, input_feedback, message

    if not cabinet_searched:
        message = "Search the Chemical Cabinet first."
        return

    if notebook_failed:
        message = "The notebook message has vanished. Press R to restart."
        return

    if message_revealed:
        message = "Password already revealed: ORION-27"
        return

    input_mode = "chemical_selection"
    input_text = ""
    input_feedback = ""

    message = "Choose the correct chemical for the notebook."


# ==================================================
# NORMAL INTERACTION USING E
# ==================================================

def interact_with_object():

    global chemical_collected, cabinet_searched
    global terminal_unlocked, terminal_open
    global code_accepted, sequence_accepted
    global exit_open, game_won
    global inventory, message
    global input_mode, input_text, input_feedback

    player_rect = pygame.Rect(
        int(player_x),
        int(player_y),
        player_size,
        player_size
    )

    player_center = pygame.Vector2(player_rect.center)

    objects = [
        (
            player_center.distance_to(
                pygame.Vector2(cabinet_rect.center)
            ),
            "cabinet"
        ),
        (
            player_center.distance_to(
                pygame.Vector2(table_rect.center)
            ),
            "table"
        ),
        (
            player_center.distance_to(
                pygame.Vector2(terminal_rect.center)
            ),
            "terminal"
        ),
        (
            player_center.distance_to(
                pygame.Vector2(panel_rect.center)
            ),
            "panel"
        ),
        (
            player_center.distance_to(
                pygame.Vector2(exit_rect.center)
            ),
            "exit"
        )
    ]

    nearest_distance, nearest_object = min(objects)

    if nearest_distance >= 110:
        message = "Move closer to an object to interact."
        return

    # CHEMICAL CABINET

    if nearest_object == "cabinet":

        if not cabinet_searched:

            inventory.extend(CHEMICALS)

            chemical_collected = True
            cabinet_searched = True

            message = (
                "You collected four chemicals. "
                "A clue is waiting at the Research Table."
            )

        else:
            message = "You have already collected all four chemicals."

    # RESEARCH TABLE

    elif nearest_object == "table":
        open_chemical_selection()

    # COMPUTER TERMINAL

    elif nearest_object == "terminal":

        if not terminal_unlocked:

            input_mode = "terminal_password"
            input_text = ""
            input_feedback = ""

            message = "Enter the terminal password."

        else:

            terminal_open = not terminal_open

            message = (
                "Terminal clues opened."
                if terminal_open
                else "Terminal clues closed."
            )

    # CONTROL PANEL

    elif nearest_object == "panel":

        if not terminal_unlocked:
            message = "Unlock the Computer Terminal first."

        elif not code_accepted:

            input_mode = "access_code"
            input_text = ""
            input_feedback = ""

            message = "Enter the emergency access code."

        elif not sequence_accepted:

            input_mode = "security_sequence"
            input_text = ""
            input_feedback = ""

            message = "Enter the security sequence."

        else:
            message = "Emergency system activated!"

    # EMERGENCY EXIT

    elif nearest_object == "exit":

        if not code_accepted or not sequence_accepted:
            message = "Emergency system is not fully activated."

        elif not exit_open:

            exit_open = True
            message = "Emergency Exit opened! Escape now."

        else:

            game_won = True
            message = "You escaped successfully!"


# ==================================================
# EXECUTE GEMINI COMMAND
# ==================================================

def execute_game_action(action, player_command=""):

    global chemical_collected, cabinet_searched
    global terminal_unlocked, terminal_open
    global code_accepted, sequence_accepted
    global exit_open, game_won
    global inventory, message
    global input_mode, input_text, input_feedback
    global move_target

    state = get_game_state()

    # Python validates the action.
    allowed, outcome = validate_action(action, state)

    if not allowed:
        message = outcome

    # AUTOMATIC MOVEMENT

    elif action.startswith("MOVE_TO_"):

        destinations = {
            "MOVE_TO_CABINET": cabinet_rect,
            "MOVE_TO_TABLE": table_rect,
            "MOVE_TO_TERMINAL": terminal_rect,
            "MOVE_TO_PANEL": panel_rect,
            "MOVE_TO_EXIT": exit_rect
        }

        target_rect = destinations[action]

        player_center = pygame.Vector2(
            player_x + player_size / 2,
            player_y + player_size / 2
        )

        destination = pygame.Vector2(target_rect.center)

        direction = destination - player_center

        if direction.length() > 0:
            direction = direction.normalize()

        stopping_point = destination - direction * 85

        move_target = pygame.Vector2(
            stopping_point.x - player_size / 2,
            stopping_point.y - player_size / 2
        )

        outcome = (
            "Moving toward "
            + action.replace("MOVE_TO_", "").lower()
            + "."
        )

        message = outcome

    # COLLECT CHEMICALS

    elif action == "COLLECT_CHEMICAL":

        if not cabinet_searched:

            inventory.extend(CHEMICALS)

            chemical_collected = True
            cabinet_searched = True

            outcome = (
                "You collected four reagent bottles. "
                "Study the clue before choosing one."
            )

        else:
            outcome = "You have already collected all four chemicals."

        message = outcome

    # EXAMINE NOTEBOOK

    elif action == "EXAMINE_NOTEBOOK":

        open_chemical_selection()
        outcome = message

    # UNLOCK TERMINAL

    elif action == "UNLOCK_TERMINAL":

        if terminal_unlocked:

            terminal_open = True
            outcome = "Terminal clues opened."

        else:

            input_mode = "terminal_password"
            input_text = ""
            input_feedback = ""

            outcome = "The terminal is asking for its password."

        message = outcome

    # READ TERMINAL

    elif action == "READ_TERMINAL":

        if not terminal_unlocked:
            outcome = "Unlock the terminal first."
        else:
            terminal_open = not terminal_open

            outcome = (
                "Terminal clues opened."
                if terminal_open
                else "Terminal clues closed."
            )

        message = outcome

    # CONTROL PANEL

    elif action == "USE_CONTROL_PANEL":

        if not code_accepted:

            input_mode = "access_code"
            outcome = "The control panel is asking for the access code."

        elif not sequence_accepted:

            input_mode = "security_sequence"
            outcome = "The control panel is asking for the security sequence."

        else:
            outcome = "The emergency system is already activated."

        input_text = ""
        input_feedback = ""
        message = outcome

    # OPEN EXIT

    elif action == "OPEN_EXIT":

        if not code_accepted or not sequence_accepted:
            outcome = "The emergency system is not fully activated."

        elif not exit_open:

            exit_open = True
            outcome = "The emergency exit is now open."

        else:

            game_won = True
            outcome = "You escaped successfully!"

        message = outcome

    # RESTART

    elif action == "RESTART_GAME":

        reset_game()
        return

    else:

        outcome = "I did not understand that command."
        message = outcome

    # GEMINI GAME MASTER RESPONSE

    latest_state = get_game_state()

    try:
        message = game_master_response(
            player_command,
            action,
            outcome,
            latest_state
        )
    except Exception:
        # Keep the Python game result if Gemini is unavailable.
        message = outcome


# ==================================================
# HANDLE PUZZLE ANSWERS
# ==================================================

def submit_puzzle_answer():

    global wrong_chemical_attempts, notebook_failed
    global message_revealed
    global terminal_unlocked
    global code_accepted, sequence_accepted
    global input_mode, input_text, input_feedback
    global message

    answer = (
        input_text.strip()
        .upper()
        .replace(" ", "")
    )

    # CHEMICAL SELECTION

    if input_mode == "chemical_selection":

        if notebook_failed:
            input_feedback = "The notebook message has vanished."
            input_text = ""
            return

        if answer == "LUMEN-12":

            message_revealed = True

            input_mode = None
            input_text = ""
            input_feedback = ""

            message = "Correct reagent! Notebook revealed password: ORION-27!"

        else:

            wrong_chemical_attempts += 1
            input_text = ""

            if wrong_chemical_attempts >= 2:

                notebook_failed = True

                input_mode = None
                input_feedback = ""

                message = (
                    "The notebook message has vanished. "
                    "Press R to restart."
                )

            else:

                input_feedback = (
                    "Incorrect chemical! "
                    "You have one chance remaining."
                )

    # TERMINAL PASSWORD

    elif input_mode == "terminal_password":

        if answer == "ORION-27":

            terminal_unlocked = True
            input_mode = None
            input_text = ""
            input_feedback = ""

            message = "Terminal unlocked!"

        else:

            input_feedback = "Incorrect password. Try again."
            input_text = ""

    # ACCESS CODE

    elif input_mode == "access_code":

        if answer == "0302":

            code_accepted = True

            input_mode = None
            input_text = ""
            input_feedback = ""

            message = "Access code accepted!"

        else:

            input_feedback = "Incorrect access code. Try again."
            input_text = ""

    # SECURITY SEQUENCE

    elif input_mode == "security_sequence":

        if answer in (
            "BLUE-GREEN-RED",
            "BLUE,GREEN,RED"
        ):

            sequence_accepted = True

            input_mode = None
            input_text = ""
            input_feedback = ""

            message = "Security sequence accepted!"

        else:

            input_feedback = "Incorrect sequence. Try again."
            input_text = ""


# ==================================================
# DRAW LAB OBJECTS
# ==================================================

def draw_lab():

    screen.fill(DARK)

    # Room walls and floor

    pygame.draw.rect(screen, WALL, (30, 30, 940, 500))
    pygame.draw.rect(screen, FLOOR, (45, 100, 910, 415))

    title = font.render("CHEMICAL RESEARCH LAB", True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

    # RESEARCH TABLE

    pygame.draw.rect(screen, (130, 90, 55), table_rect)

    screen.blit(
        small_font.render("Research Table", True, WHITE),
        (130, 285)
    )

    if message_revealed:

        screen.blit(
            small_font.render("Password: ORION-27", True, YELLOW),
            (125, 320)
        )

    else:

        screen.blit(
            small_font.render("Notebook", True, WHITE),
            (165, 210)
        )

    if cabinet_searched and not message_revealed and not notebook_failed:

        draw_wrapped_text(
            screen,
            "The first letter and the last number are related.",
            tiny_font,
            YELLOW,
            75,
            350,
            260,
            3
        )

    if notebook_failed:

        screen.blit(
            small_font.render("NOTEBOOK MESSAGE LOST", True, RED),
            (95, 375)
        )

    # CHEMICAL CABINET

    pygame.draw.rect(screen, (100, 110, 125), cabinet_rect)

    if not cabinet_searched:

        bottle_colors = [YELLOW, RED, GREEN, BLUE]

        bottle_positions = [
            (382, 175),
            (435, 175),
            (382, 235),
            (435, 235)
        ]

        bottle_names = ["L-12", "C-4", "V-6", "N-2"]

        for bottle_color, (bx, by), bottle_name in zip(
            bottle_colors,
            bottle_positions,
            bottle_names
        ):

            pygame.draw.rect(
                screen,
                bottle_color,
                (bx, by, 25, 38)
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (bx + 7, by - 6, 11, 7)
            )

            screen.blit(
                tiny_font.render(bottle_name, True, WHITE),
                (bx - 2, by + 40)
            )

    else:

        screen.blit(
            small_font.render("4 REAGENTS", True, GREEN),
            (380, 205)
        )

        screen.blit(
            small_font.render("Collected", True, WHITE),
            (385, 230)
        )

    screen.blit(
        small_font.render("Chemical Cabinet", True, WHITE),
        (355, 310)
    )

    # COMPUTER TERMINAL

    pygame.draw.rect(
        screen,
        GREEN if terminal_unlocked else BLUE,
        terminal_rect
    )

    screen.blit(
        small_font.render("Computer Terminal", True, WHITE),
        (640, 285)
    )

    if terminal_unlocked:

        screen.blit(
            small_font.render("UNLOCKED", True, GREEN),
            (675, 155)
        )

    # CONTROL PANEL

    pygame.draw.rect(
        screen,
        GREEN if sequence_accepted else (160, 60, 60),
        panel_rect
    )

    screen.blit(
        small_font.render("Control Panel", True, WHITE),
        (655, 455)
    )

    # EMERGENCY EXIT

    if exit_open:

        pygame.draw.rect(screen, (20, 20, 25), exit_rect)

        pygame.draw.rect(
            screen,
            GREEN,
            exit_rect,
            4
        )

        screen.blit(
            small_font.render("OPEN", True, GREEN),
            (860, 225)
        )

    else:

        pygame.draw.rect(screen, RED, exit_rect)

        screen.blit(
            small_font.render("LOCKED", True, WHITE),
            (855, 225)
        )

    # SCIENTIST

    pygame.draw.circle(
        screen,
        (240, 210, 170),
        (int(player_x + 15), int(player_y + 8)),
        10
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (int(player_x + 5), int(player_y + 17), 20, 20)
    )


# ==================================================
# DRAW INVENTORY AND BOTTOM HUD
# ==================================================

def draw_hud():

    # Separate HUD background

    pygame.draw.rect(screen, DARK, (0, 530, WIDTH, 190))

    # Controls

    screen.blit(
        tiny_font.render(
            "Move: WASD / Arrows     Interact: E     AI command: T",
            True,
            WHITE
        ),
        (35, 537)
    )

    # INVENTORY SECTION

    screen.blit(
        small_font.render("INVENTORY", True, WHITE),
        (35, 568)
    )

    if inventory:

        item_positions = [200, 395, 590, 785]

        for i, item in enumerate(inventory):

            item_rect = pygame.Rect(
                item_positions[i],
                562,
                165,
                34
            )

            pygame.draw.rect(screen, PANEL_BG, item_rect, border_radius=5)

            item_text = small_font.render(item, True, YELLOW)

            screen.blit(
                item_text,
                item_text.get_rect(center=item_rect.center)
            )

    else:

        screen.blit(
            small_font.render("Empty", True, WHITE),
            (200, 568)
        )

    # STATUS MESSAGE ON ITS OWN ROW

    pygame.draw.line(
        screen,
        WALL,
        (35, 605),
        (965, 605),
        1
    )

    screen.blit(
        tiny_font.render("STATUS:", True, GREEN),
        (35, 615)
    )

    draw_wrapped_text(
        screen,
        message,
        tiny_font,
        WHITE,
        115,
        613,
        840,
        2
    )

    # COMMAND INSTRUCTION

    screen.blit(
        tiny_font.render(
            "Press T to type a command for the AI Game Master",
            True,
            YELLOW
        ),
        (35, 650)
    )

    # COMMAND INPUT BAR

    pygame.draw.rect(
        screen,
        (35, 45, 60),
        (35, 674, 930, 34),
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        BLUE if command_mode else WALL,
        (35, 674, 930, 34),
        2,
        border_radius=5
    )

    command_label = (
        "Command: " + command_text
        if command_mode
        else "Example: Go to the computer terminal"
    )

    screen.blit(
        tiny_font.render(command_label[:110], True, WHITE),
        (48, 682)
    )


# ==================================================
# DRAW TERMINAL CLUES
# ==================================================

def draw_terminal():

    if terminal_unlocked and terminal_open and not input_mode:

        pygame.draw.rect(
            screen,
            (30, 40, 55),
            (250, 175, 500, 305)
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (250, 175, 500, 305),
            3
        )

        screen.blit(
            font.render("TERMINAL CLUES", True, GREEN),
            (390, 195)
        )

        clues = [
            "1. The access code has two parts.",
            "2. First: count oxygen atoms in AZ-4.",
            "3. Second: count the lab's research chambers.",
            "4. Write each number using two digits.",
            "5. The status cycle goes from stable,",
            "   to active, then to critical.",
            "6. BLUE = stable, GREEN = active, RED = critical."
        ]

        y = 240

        for clue in clues:

            screen.blit(
                tiny_font.render(clue, True, WHITE),
                (280, y)
            )

            y += 27

        screen.blit(
            tiny_font.render(
                "Press E near terminal to close.",
                True,
                YELLOW
            ),
            (330, 445)
        )


# ==================================================
# DRAW PUZZLE INPUT WINDOW
# ==================================================

def draw_input_window():

    if not input_mode:
        return

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(210)
    overlay.fill((0, 0, 0))

    screen.blit(overlay, (0, 0))

    pygame.draw.rect(
        screen,
        (45, 55, 70),
        (180, 190, 640, 310)
    )

    pygame.draw.rect(
        screen,
        BLUE,
        (180, 190, 640, 310),
        3
    )

    headings = {
        "chemical_selection": "NOTEBOOK CHEMICAL PUZZLE",
        "terminal_password": "COMPUTER TERMINAL",
        "access_code": "EMERGENCY CONTROL PANEL",
        "security_sequence": "SECURITY SEQUENCE"
    }

    heading = headings.get(input_mode, "PUZZLE")

    screen.blit(
        font.render(heading, True, WHITE),
        (300, 235)
    )

    if input_mode == "chemical_selection":

        screen.blit(
            small_font.render(
                "The first letter and the last number are related.",
                True,
                YELLOW
            ),
            (210, 285)
        )

        screen.blit(
            small_font.render(
                "Choose: Lumen-12, Crimson-4, Vitra-6 or Nexon-2",
                True,
                WHITE
            ),
            (210, 315)
        )

        screen.blit(
            small_font.render(
                f"Chances remaining: {2 - wrong_chemical_attempts}",
                True,
                YELLOW
            ),
            (210, 370)
        )

    elif input_mode == "terminal_password":

        screen.blit(
            small_font.render(
                "Enter terminal password:",
                True,
                WHITE
            ),
            (210, 295)
        )

    elif input_mode == "access_code":

        screen.blit(
            small_font.render(
                "Enter the emergency access code:",
                True,
                WHITE
            ),
            (210, 295)
        )

    elif input_mode == "security_sequence":

        screen.blit(
            small_font.render(
                "Enter colours in the correct order:",
                True,
                WHITE
            ),
            (210, 295)
        )

    # Text input box

    pygame.draw.rect(
        screen,
        WHITE,
        (210, 405, 580, 40)
    )

    screen.blit(
        font.render(input_text, True, DARK),
        (220, 412)
    )

    screen.blit(
        tiny_font.render(
            "Press ENTER to submit | ESC to cancel",
            True,
            WHITE
        ),
        (210, 460)
    )

    if input_feedback:

        screen.blit(
            small_font.render(input_feedback, True, RED),
            (210, 480)
        )


# ==================================================
# NOTEBOOK FAILURE SCREEN
# ==================================================

def draw_failure_screen():

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))

    screen.blit(overlay, (0, 0))

    title = big_font.render(
        "NOTEBOOK MESSAGE LOST",
        True,
        RED
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 270))
    )

    subtitle = font.render(
        "You used both chances. Restart the game.",
        True,
        WHITE
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(center=(WIDTH // 2, 345))
    )

    restart_text = small_font.render(
        "Press R to restart.",
        True,
        YELLOW
    )

    screen.blit(
        restart_text,
        restart_text.get_rect(center=(WIDTH // 2, 415))
    )


# ==================================================
# VICTORY SCREEN
# ==================================================

def draw_victory_screen():

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(235)
    overlay.fill((5, 15, 20))

    screen.blit(overlay, (0, 0))

    title = big_font.render(
        "ESCAPE SUCCESSFUL!",
        True,
        GREEN
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 230))
    )

    screen.blit(
        font.render(
            "You survived the Chemical Lab Disaster.",
            True,
            WHITE
        ),
        (260, 310)
    )

    screen.blit(
        font.render(
            "Congratulations, Scientist!",
            True,
            YELLOW
        ),
        (340, 360)
    )

    screen.blit(
        small_font.render(
            "Press R to restart | ESC to quit",
            True,
            WHITE
        ),
        (355, 440)
    )


# ==================================================
# MAIN GAME LOOP
# ==================================================

running = True

while running:

    clock.tick(60)

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # VICTORY SCREEN

            if game_won:

                if event.key == pygame.K_r:
                    reset_game()

                elif event.key == pygame.K_ESCAPE:
                    running = False

            # NOTEBOOK FAILED

            elif notebook_failed:

                if event.key == pygame.K_r:
                    reset_game()

            # GEMINI COMMAND INPUT

            elif command_mode:

                if event.key == pygame.K_RETURN:

                    typed_command = command_text.strip()

                    command_mode = False
                    command_text = ""

                    if typed_command:

                        message = "Gemini is interpreting your command..."

                        try:
                            action = interpret_command(typed_command)

                            execute_game_action(
                                action,
                                typed_command
                            )

                        except Exception as error:
                            message = f"Command error: {error}"

                elif event.key == pygame.K_BACKSPACE:
                    command_text = command_text[:-1]

                elif event.key == pygame.K_ESCAPE:

                    command_mode = False
                    command_text = ""
                    message = "Command cancelled."

                elif event.unicode.isprintable() and len(command_text) < 100:
                    command_text += event.unicode

            # PUZZLE INPUT

            elif input_mode:

                if event.key == pygame.K_RETURN:
                    submit_puzzle_answer()

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                elif event.key == pygame.K_ESCAPE:

                    input_mode = None
                    input_text = ""
                    input_feedback = ""

                    message = "Input cancelled."

                elif event.unicode.isprintable() and len(input_text) < 30:
                    input_text += event.unicode

            # OPEN GEMINI COMMAND BOX

            elif event.key == pygame.K_t:

                command_mode = True
                command_text = ""

                message = "Type a command and press ENTER."

            # NORMAL INTERACTION

            elif event.key == pygame.K_e:
                interact_with_object()

    # --------------------------------------------------
    # AUTOMATIC MOVEMENT
    # --------------------------------------------------

    if (
        move_target is not None
        and not input_mode
        and not command_mode
        and not game_won
        and not notebook_failed
    ):

        current_position = pygame.Vector2(
            player_x,
            player_y
        )

        difference = move_target - current_position

        if difference.length() <= player_speed:

            player_x = move_target.x
            player_y = move_target.y

            move_target = None

            message = "You have arrived. Press E to interact."

        else:

            step = difference.normalize() * player_speed

            player_x += step.x
            player_y += step.y

    # --------------------------------------------------
    # MANUAL MOVEMENT
    # --------------------------------------------------

    if (
        not input_mode
        and not command_mode
        and not game_won
        and not notebook_failed
    ):

        keys = pygame.key.get_pressed()

        movement_keys = (
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_a,
            pygame.K_d,
            pygame.K_w,
            pygame.K_s
        )

        if any(keys[key] for key in movement_keys):
            move_target = None

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_x -= player_speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_x += player_speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_y -= player_speed

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_y += player_speed

    # Keep player inside the laboratory

    player_x = max(45, min(player_x, 955 - player_size))
    player_y = max(100, min(player_y, 515 - player_size))

    # --------------------------------------------------
    # DRAW EVERYTHING
    # --------------------------------------------------

    draw_lab()
    draw_hud()
    draw_terminal()
    draw_input_window()

    if notebook_failed:
        draw_failure_screen()

    if game_won:
        draw_victory_screen()

    pygame.display.flip()


# ==================================================
# QUIT
# ==================================================

pygame.quit()
sys.exit()








