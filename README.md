# Details about repository
This repository contains a project for a hardware-based Tic-Tac-Toe 3x3 game using Arduino Uno and C# WPF. The game logic and decision-making will run primarily on the Arduino Uno, while the C# WPF application will serve as a graphical interface for users to interact with the game.
 


# Task details
## Task 1
Main goals to this task is to create repository with main branch **develop**. Then create branch with name **feature/develop/task1** and create `README.md` file with all descriptions. Also create **TAG** and make pull request.

 ## Student details
| Student number | Game | config format |
| :-----------: | :-------------: | :-----------: |
| 09 | tik-tac-toe 3x3 | INI |

## Technology Stack and Hardware Used

### Hardware
- **Arduino Uno**: The Arduino will handle most of the game logic, including managing inputs, processing the current game state, and sending data to the C# application.

### Software
- **C# WPF**: Used for creating the graphical user interface (GUI) that displays the game board and allows users to view the game progress in real time.
- **Arduino IDE**: To write and upload the logic code to the Arduino Uno, primarily using C/C++ for low-level control.

### Programming Languages
- **C#**: Used to develop the WPF interface that will interact with the Arduino.
- **C/C++**: Used in the Arduino environment to develop the Tic-Tac-Toe game logic.
### Communication
- **Serial Communication**: The Arduino will communicate with the C# WPF interface through a UART serial port to send and receive game status and input data.
