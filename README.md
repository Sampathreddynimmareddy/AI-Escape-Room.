
# AI Escape Room

## 1. About the Project

The AI Escape Room is an interactive game in which the player gets trapped inside an underground chemical research laboratory during a fictional emergency. The player must explore the laboratory, collect items, solve puzzles, and unlock the emergency exit to escape.

The main idea of this project is to explore how Generative AI can make a game more interactive. Players can communicate with an AI Game Master using natural language instead of depending only on fixed instructions.

The project was developed in two versions. Each version introduces a different approach to player interaction and game development.

## 2. Project Versions

### Version 1 – Streamlit Application

The first version was developed using Streamlit and Google Gemini AI. It provides a web-based interface where players can explore five objects, solve puzzles, and communicate with the AI Game Master.

Gemini helps guide the player and respond to their questions, while Python and Streamlit session state keep track of the game progress.

### Version 2 – Pygame Application

The second version introduces a graphical game environment using Pygame. Players can move around the laboratory, interact with objects, collect chemicals, and complete puzzles.

An important improvement in this version is the separation between AI interaction and game logic. Gemini interprets natural-language commands and provides responses, while Python validates actions and controls the actual game state.

This makes the game more consistent and prevents the AI from directly changing important game decisions.

## 3. Main Game Features

- Interactive chemical research laboratory environment.
- Five objects that players can explore and interact with.
- Puzzle-solving challenges based on clues found inside the laboratory.
- Chemical selection puzzle with limited attempts.
- Password-protected computer terminal.
- Emergency control panel with a final access code and sequence.
- Gemini-powered Game Master for natural-language interaction.
- Python-based validation to ensure game rules are followed.
- Restart option to play the game again.

## 4. Technologies Used

- **Python:** Main programming language.
- **Google Gemini AI:** Natural-language understanding and AI Game Master responses.
- **Streamlit:** User interface for Version 1.
- **Pygame:** Graphical game environment for Version 2.
- **Git and GitHub:** Source code management and project development.

## 5. Project Structure

The main project files are:

- `app.py` – Version 1 Streamlit application.
- `app_v2.py` – Version 2 Pygame application.
- `gemini_controller.py` – Handles Gemini-based command interpretation and Game Master responses.
- `requirements.txt` – Contains the required Python packages.
- `.env.example` – Provides an example of the API key configuration.
- `.gitignore` – Prevents sensitive and unnecessary files from being uploaded.

## 6. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sampathreddynimmareddy/AI-Escape-Room..git
cd AI-Escape-Room
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\activate
```

### Step 3: Install the Required Packages

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Gemini API Key

Create a folder named `.streamlit` in the project directory if it does not already exist.

Inside that folder, create a file named `secrets.toml` and add:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

Replace the placeholder with your own Gemini API key.

**Important:** Never upload your actual API key or `secrets.toml` file to GitHub.

### Step 5: Run the Applications

To run Version 1:

```bash
streamlit run app.py
```

To run Version 2:

```bash
python app_v2.py
```

## 7. Game Controls – Version 2

| Key | Action |
|---|---|
| W / Up Arrow | Move up |
| S / Down Arrow | Move down |
| A / Left Arrow | Move left |
| D / Right Arrow | Move right |
| E | Interact with nearby objects |
| T | Enter a natural-language command |
| Enter | Submit a command |
| ESC | Quit the game |
| R | Restart after winning |

## 8. Testing and Validation

The game was tested using different player actions to check whether the puzzles and game rules work correctly.

The following test cases cover the main game scenarios:

| Test Case | Expected Result |
|---|---|
| Collect chemicals from the cabinet | Chemicals are added to inventory. |
| Select an incorrect chemical once | Warning is displayed and one chance remains. |
| Select an incorrect chemical twice | Notebook message disappears and restart is required. |
| Enter an incorrect terminal password | Terminal remains locked. |
| Enter the correct password | Terminal unlocks and displays clues. |
| Enter an incorrect access code | Access is rejected. |
| Enter an incorrect control sequence | Exit remains locked. |
| Try to open the exit before solving puzzles | Exit remains locked. |
| Complete both control panel challenges | Exit becomes available. |
| Try to bypass game rules using an AI command | Python validation should reject unauthorized actions. |

These tests help evaluate whether the game responds correctly to normal interactions and invalid or unexpected commands.

## 9. Limitations and Future Improvements

Although the project provides an interactive escape room experience, there are some areas that could be improved.

- The game currently contains only one laboratory environment.
- The number of puzzles and interactive objects is limited.
- AI responses may sometimes take time because they depend on an external API.
- The graphical design and animations could be improved further.

In the future, additional rooms, more challenging puzzles, improved graphics, sound effects, and multiplayer functionality could make the experience more engaging.

## 10. Conclusion

This project demonstrates how Generative AI can be combined with traditional Python programming to create an interactive game.

The development of two versions helped explore different approaches to AI integration. While Version 1 focuses on a simple web-based experience, Version 2 introduces a graphical environment and stronger control over game actions through Python-based validation.

Overall, the project provided practical experience in working with AI APIs, game development, application design, and software version control.

```
