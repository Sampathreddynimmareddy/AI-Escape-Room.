
import streamlit as st
from google import genai

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="AI Escape Room - Chemical Lab",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 AI Escape Room: Chemical Lab Disaster")

st.write(
    "You are trapped inside a research laboratory during "
    "a fictional chemical emergency. Solve the puzzles and escape!"
)

# --------------------------------------------------
# GAME STATE
# --------------------------------------------------

defaults = {
    "game_started": False,
    "inventory": [],
    "message_revealed": False,
    "terminal_unlocked": False,
    "control_panel_unlocked": False,
    "escape_sequence_solved": False,
    "game_won": False,
    "chat_messages": [],
    "reset_count": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

suffix = str(st.session_state.reset_count)


def restart_game():
    st.session_state.reset_count += 1

    for key, value in defaults.items():
        if key != "reset_count":
            st.session_state[key] = value

    st.rerun()


# --------------------------------------------------
# GEMINI AI GAME MASTER
# --------------------------------------------------

def get_game_master_response(player_message):

    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    # Give Gemini the current game situation.
    game_context = f"""
    GAME: AI Escape Room - Chemical Lab Disaster

    ROLE:
    You are the AI Game Master of a fictional chemical laboratory
    escape room. Stay in character. Be friendly, mysterious and helpful.

    STORY:
    The player is trapped in a fictional research laboratory.
    They must solve puzzles and unlock the emergency exit.

    CURRENT GAME STATE:
    Game started: {st.session_state.game_started}
    Inventory: {st.session_state.inventory}
    Hidden notebook message revealed: {st.session_state.message_revealed}
    Computer terminal unlocked: {st.session_state.terminal_unlocked}
    Control panel unlocked: {st.session_state.control_panel_unlocked}
    Security switches activated: {st.session_state.escape_sequence_solved}
    Player escaped: {st.session_state.game_won}

    OBJECTS IN THE ROOM:
    1. Research Table: Contains a notebook with invisible writing.
    2. Chemical Cabinet: Contains the fictional reagent Lumen-9.
    3. Computer Terminal: Requires a password.
    4. Emergency Control Panel: Requires a four-digit code and a switch sequence.
    5. Emergency Exit: Opens after all challenges are completed.

    IMPORTANT RULES:
    - Answer the player's questions naturally.
    - Use the current game state when giving advice.
    - Give hints gradually instead of immediately revealing answers.
    - Never reveal hidden passwords, security codes or switch sequences
      unless the player has already discovered the relevant information.
    - Never claim that an item has been collected unless it appears in inventory.
    - Never claim that a puzzle has been solved unless the game state confirms it.
    - You cannot change inventory, unlock objects or complete puzzles.
    - The Python game controls all actual actions.
    - If the player asks you to unlock something, explain that they must
      interact with the object in the game.
    - Keep replies reasonably short.
    - Keep the story fictional. Do not provide real chemical or explosive instructions.
    """

    # Include recent conversation for memory.
    history = st.session_state.chat_messages[-12:]

    conversation = ""

    for message in history:
        if message["role"] == "user":
            conversation += f"\nPlayer: {message['content']}\n"
        else:
            conversation += f"\nGame Master: {message['content']}\n"

    prompt = f"""
    {game_context}

    PREVIOUS CONVERSATION:
    {conversation}

    NEW PLAYER MESSAGE:
    {player_message}

    Respond as the AI Game Master.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# --------------------------------------------------
# INTRODUCTION
# --------------------------------------------------

if not st.session_state.game_started:

    st.subheader("🚨 Emergency Mission")

    st.write("""
    A fictional chemical emergency has triggered an automatic
    lockdown inside an underground research laboratory.

    The emergency exit is locked.

    Explore the laboratory, discover the security password,
    solve the control panel puzzle and escape safely.
    """)

    st.info("Your mission: Find a way to unlock the Emergency Exit.")

    if st.button("Start Mission", type="primary"):
        st.session_state.game_started = True
        st.rerun()


# --------------------------------------------------
# MAIN GAME
# --------------------------------------------------

elif not st.session_state.game_won:

    st.subheader("🔍 Explore the Laboratory")

    selected_object = st.selectbox(
        "Choose an object to investigate:",
        [
            "Research Table",
            "Chemical Cabinet",
            "Computer Terminal",
            "Emergency Control Panel",
            "Emergency Exit"
        ],
        key=f"object_{suffix}"
    )

    # --------------------------------------------------
    # RESEARCH TABLE
    # --------------------------------------------------

    if selected_object == "Research Table":

        st.subheader("📓 Research Table")

        st.write("""
        You find an old research notebook on the table.
        Its pages appear completely blank.
        There may be a hidden message.
        """)

        if st.session_state.message_revealed:
            st.success("The hidden message has been revealed!")
        else:
            st.warning(
                "The notebook contains invisible writing. "
                "You need something to reveal it."
            )

    # --------------------------------------------------
    # CHEMICAL CABINET
    # --------------------------------------------------

    elif selected_object == "Chemical Cabinet":

        st.subheader("🧴 Chemical Cabinet")

        st.write("""
        You notice a small fictional reagent labelled Lumen-9.
        A note says it can reveal invisible writing.
        """)

        if "Lumen-9" in st.session_state.inventory:

            st.success("You have already collected Lumen-9.")

        else:

            if st.button("Collect Lumen-9"):

                st.session_state.inventory.append("Lumen-9")

                st.success("Lumen-9 added to your inventory!")
                st.rerun()

    # --------------------------------------------------
    # COMPUTER TERMINAL
    # --------------------------------------------------

    elif selected_object == "Computer Terminal":

        st.subheader("💻 Computer Terminal")

        if st.session_state.terminal_unlocked:

            st.success("Computer Terminal unlocked!")

            st.write("📁 CLASSIFIED RESEARCH FILE")

            st.write("""
            The emergency control panel requires a four-digit security code.

            Research notes:
            - Fictional compound AZ-4 contains 3 oxygen atoms.
            - This laboratory has 2 research chambers.

            Combine the two numbers using two digits each.

            Additional security note:
            The emergency switches must be activated in the order
            BLUE → GREEN → RED.
            """)

        else:

            st.write("The terminal is password protected.")

            password = st.text_input(
                "Enter the terminal password:",
                key=f"terminal_password_{suffix}"
            )

            if st.button("Unlock Terminal"):

                if not st.session_state.message_revealed:

                    st.error(
                        "You haven't discovered the password yet. "
                        "Investigate the Research Table."
                    )

                elif password.strip().upper() == "ORION-27":

                    st.session_state.terminal_unlocked = True

                    st.success("Correct password! Terminal unlocked.")
                    st.rerun()

                else:

                    st.error("Incorrect password. Try again.")

    # --------------------------------------------------
    # EMERGENCY CONTROL PANEL
    # --------------------------------------------------

    elif selected_object == "Emergency Control Panel":

        st.subheader("🎛️ Emergency Control Panel")

        if not st.session_state.terminal_unlocked:

            st.warning(
                "Unlock the Computer Terminal first."
            )

        elif not st.session_state.control_panel_unlocked:

            st.write("Enter the four-digit security code.")

            security_code = st.text_input(
                "Security code:",
                max_chars=4,
                key=f"security_code_{suffix}"
            )

            if st.button("Verify Security Code"):

                if security_code == "0302":

                    st.session_state.control_panel_unlocked = True

                    st.success("Correct code! Control panel accessible.")
                    st.rerun()

                else:

                    st.error("Incorrect security code.")

        else:

            st.success("Control panel access granted!")

            if not st.session_state.escape_sequence_solved:

                st.write("Activate the three security switches.")

                col1, col2, col3 = st.columns(3)

                choices = [
                    "Select colour",
                    "BLUE",
                    "GREEN",
                    "RED"
                ]

                with col1:
                    switch_1 = st.selectbox(
                        "Switch 1",
                        choices,
                        key=f"switch_1_{suffix}"
                    )

                with col2:
                    switch_2 = st.selectbox(
                        "Switch 2",
                        choices,
                        key=f"switch_2_{suffix}"
                    )

                with col3:
                    switch_3 = st.selectbox(
                        "Switch 3",
                        choices,
                        key=f"switch_3_{suffix}"
                    )

                if st.button("Activate Security Switches"):

                    entered_sequence = [
                        switch_1,
                        switch_2,
                        switch_3
                    ]

                    correct_sequence = [
                        "BLUE",
                        "GREEN",
                        "RED"
                    ]

                    if entered_sequence == correct_sequence:

                        st.session_state.escape_sequence_solved = True

                        st.success(
                            "Correct sequence! Emergency lockdown disabled."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Incorrect sequence. Check the Computer Terminal."
                        )

            else:

                st.success("All security switches activated!")
                st.success("Emergency lockdown disabled.")
                st.write("The Emergency Exit is now unlocked.")

    # --------------------------------------------------
    # EMERGENCY EXIT
    # --------------------------------------------------

    elif selected_object == "Emergency Exit":

        st.subheader("🚪 Emergency Exit")

        if st.session_state.escape_sequence_solved:

            st.success("The Emergency Exit is unlocked!")

            st.write(
                "The lockdown has been disabled. "
                "You can now leave the laboratory safely."
            )

            if st.button("🚀 Escape Now", type="primary"):

                st.session_state.game_won = True
                st.rerun()

        else:

            st.error("The Emergency Exit is still locked.")

            st.write("""
            You must unlock the Computer Terminal,
            solve the Control Panel code and activate
            the security switches before escaping.
            """)

    # --------------------------------------------------
    # INVENTORY
    # --------------------------------------------------

    st.divider()

    st.subheader("🎒 Inventory")

    if st.session_state.inventory:

        for item in st.session_state.inventory:
            st.write(f"• {item}")

    else:

        st.write("Your inventory is empty.")

    # --------------------------------------------------
    # USE ITEMS
    # --------------------------------------------------

    if st.session_state.inventory:

        st.divider()
        st.subheader("🧪 Use an Item")

        target = st.selectbox(
            "Where do you want to use Lumen-9?",
            [
                "Select an object",
                "Research Table",
                "Computer Terminal",
                "Emergency Control Panel",
                "Emergency Exit"
            ],
            key=f"item_target_{suffix}"
        )

        if st.button("Use Lumen-9"):

            if target == "Research Table":

                if not st.session_state.message_revealed:

                    st.session_state.message_revealed = True

                    st.success(
                        "Lumen-9 reveals a hidden message in the notebook!"
                    )

                    st.rerun()

                else:

                    st.info("The hidden message is already revealed.")

            elif target == "Select an object":

                st.warning("Please select an object first.")

            else:

                st.warning("Lumen-9 does not work on this object.")

    # --------------------------------------------------
    # SECRET MESSAGE
    # --------------------------------------------------

    if st.session_state.message_revealed:

        st.divider()
        st.subheader("🔐 Discovered Secret Message")

        st.success("The notebook reveals the password: ORION-27")

    # --------------------------------------------------
    # MISSION PROGRESS
    # --------------------------------------------------

    st.divider()
    st.subheader("📊 Mission Progress")

    progress_items = [
        (
            "Lumen-9 collected",
            "Lumen-9" in st.session_state.inventory
        ),
        (
            "Hidden message revealed",
            st.session_state.message_revealed
        ),
        (
            "Computer Terminal unlocked",
            st.session_state.terminal_unlocked
        ),
        (
            "Control Panel unlocked",
            st.session_state.control_panel_unlocked
        ),
        (
            "Security switches activated",
            st.session_state.escape_sequence_solved
        )
    ]

    for label, completed in progress_items:

        if completed:
            st.write(f"✅ {label}")
        else:
            st.write(f"⬜ {label}")

    # --------------------------------------------------
    # RESTART
    # --------------------------------------------------

    st.divider()

    if st.button("🔄 Restart Mission"):
        restart_game()

    # --------------------------------------------------
    # AI GAME MASTER CHAT
    # --------------------------------------------------

    st.divider()

    st.subheader("🤖 AI Game Master")

    st.caption(
        "Ask questions, investigate clues or request hints. "
        "The Game Master remembers your conversation."
    )

    # Display previous messages.
    for message in st.session_state.chat_messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Player input.
    player_message = st.chat_input(
        "Ask the Game Master something..."
    )

    if player_message:

        st.session_state.chat_messages.append({
            "role": "user",
            "content": player_message
        })

        with st.chat_message("user"):
            st.write(player_message)

        with st.chat_message("assistant"):

            with st.spinner("Game Master is thinking..."):

                try:

                    answer = get_game_master_response(
                        player_message
                    )

                    st.write(answer)

                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as e:

                    st.error(
                        "The Game Master could not respond. "
                        "Please try again."
                    )

                    st.code(str(e))


# --------------------------------------------------
# VICTORY SCREEN
# --------------------------------------------------

else:

    st.balloons()

    st.title("🎉 MISSION COMPLETED!")

    st.success(
        "You escaped the Chemical Research Laboratory!"
    )

    st.write("""
    You successfully:

    - Collected the fictional Lumen-9 reagent.
    - Discovered the hidden password.
    - Unlocked the Computer Terminal.
    - Solved the security code.
    - Activated the security switches.
    - Disabled the fictional laboratory lockdown.
    - Escaped through the Emergency Exit.
    """)

    st.subheader("🏆 Congratulations, Scientist!")

    if st.button("🔄 Play Again", type="primary"):
        restart_game()



