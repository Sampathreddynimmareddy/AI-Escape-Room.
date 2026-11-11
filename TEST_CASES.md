# AI Escape Room – Test Cases and Results

## 1. Introduction

Testing was carried out to evaluate the functionality, reliability and security of the AI-Powered Escape Room. The project contains two versions.

- **Version 1:** Uses Streamlit and Gemini AI to provide an interactive escape-room experience.
- **Version 2:** Uses Pygame, Gemini AI and Python-based action validation to improve game-state consistency and prevent unauthorized actions.

The main objective of testing was to check whether players could complete the puzzles correctly and whether the application could reject invalid actions without allowing the player to bypass the game rules.

## 2. Test Cases

### Test Case 1: Collecting Chemicals

**Objective:** Verify that the player can collect the available chemicals from the chemical cabinet.

**Steps:**
1. Start the game.
2. Move towards the chemical cabinet.
3. Interact with the cabinet using the E key or a natural-language command.
4. Check the inventory.

**Expected Result:** The chemicals should be added to the player's inventory. The player should not be able to collect them repeatedly.

**Version 2 Actual Result:** Passed. The chemicals were collected successfully, and the cabinet indicated that the items had already been collected when the player interacted with it again.

### Test Case 2: Incorrect Chemical Selection

**Objective:** Check whether the notebook correctly handles incorrect chemical selections.

**Steps:**
1. Collect all four chemicals.
2. Interact with the research table.
3. Select an incorrect chemical.
4. Attempt another incorrect selection.

**Expected Result:** The first incorrect attempt should produce a warning and leave one attempt remaining. The second incorrect attempt should cause the notebook message to disappear and require a restart.

**Version 2 Actual Result:** Passed. The first incorrect selection produced a warning. The second incorrect selection caused the notebook message to disappear.

### Test Case 3: Terminal Password Validation

**Objective:** Verify that the computer terminal cannot be accessed without the correct password.

**Steps:**
1. Approach the computer terminal before revealing the notebook password.
2. Attempt to access the terminal.
3. Enter an incorrect password.
4. Restart or continue after obtaining the correct notebook password.
5. Enter ORION-27.

**Expected Result:** Incorrect passwords should be rejected. The terminal should unlock only after the correct password is entered.

**Version 2 Actual Result:** Passed. Incorrect passwords were rejected, and the terminal unlocked after entering ORION-27.

### Test Case 4: Emergency Access Code Validation

**Objective:** Check whether the control panel accepts only the correct access code.

**Steps:**
1. Unlock the computer terminal.
2. Approach the emergency control panel.
3. Enter an incorrect access code.
4. Enter the correct code, 0302.

**Expected Result:** Incorrect codes should be rejected. The correct code should be accepted.

**Version 2 Actual Result:** Passed. The incorrect code was rejected, and the correct code 0302 was accepted.

### Test Case 5: Security Sequence Validation

**Objective:** Verify that the emergency control panel validates the required security sequence.

**Steps:**
1. Complete the access-code challenge.
2. Enter an incorrect sequence, such as RED-BLUE-GREEN.
3. Enter the correct sequence, BLUE-GREEN-RED.

**Expected Result:** The incorrect sequence should be rejected. The correct sequence should activate the emergency system.

**Version 2 Actual Result:** Passed. The incorrect sequence was rejected, and the correct sequence was accepted.

### Test Case 6: Emergency Exit Protection

**Objective:** Ensure that the player cannot open the emergency exit before completing the required puzzles.

**Steps:**
1. Start a new game.
2. Approach the emergency exit without completing the access code and security sequence.
3. Attempt to open the exit.
4. Complete both challenges and try again.

**Expected Result:** The exit should remain locked until both challenges are successfully completed.

**Version 2 Actual Result:** Passed. The exit remained locked before the required challenges were completed.

### Test Case 7: Complete Escape

**Objective:** Verify that the player can successfully complete the game.

**Steps:**
1. Collect the chemicals.
2. Solve the notebook puzzle.
3. Unlock the computer terminal.
4. Solve the access-code challenge.
5. Complete the security sequence.
6. Open the emergency exit and interact with it again.

**Expected Result:** The game should recognize successful completion and display a victory message.

**Version 2 Actual Result:** Passed. The emergency exit opened, and the game displayed a successful escape message.


## 3. Testing Summary

The tests confirmed that Version 2 supports chemical collection, puzzle validation, password protection, access-code validation, security-sequence validation and emergency-exit protection.

The results demonstrate that Python-based validation controls important game actions instead of relying entirely on AI-generated responses. This improves consistency and reduces the possibility of unauthorized game-state changes.

The adversarial prompt test should be completed and its actual result recorded before final submission.

## 4. Conclusion

Testing demonstrates that Version 2 provides a more controlled and reliable escape-room experience. Gemini is used to interpret natural-language commands and provide game narration, while Python validates actions and maintains the game state. This separation helps prevent invalid actions from changing the progress of the game.