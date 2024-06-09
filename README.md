# README for Quiz Game Project

## Overview
This project is a networked quiz game built using Python's socket and threading libraries. It allows multiple clients to connect to a server and participate in a quiz. The server controls the flow of the game, including the distribution of questions, timers for answering, and scorekeeping. The client side includes a graphical user interface (GUI) built with Tkinter for a user-friendly experience.

## Features
* Server setup via a Tkinter GUI
* Configurable quiz settings (timers, number of participants, marking scheme)
* Real-time buzzer system for answering questions
* Score tracking and display
* Automated handling of multiple clients

## Prerequisites
* Python 3.x
* Tkinter (usually included with Python)
* The Questions module containing the Q_and_A list of questions and answers

## Directory Structure
```
QuizGame/
├── server.py
├── client.py
├── Questions.py
└── README.md
```

## Setup and Installation
1. Clone the repository:

```sh
git clone <repository_url>
cd QuizGame
```

2. Install dependencies:

Tkinter is included with Python, so no additional installations should be needed. Ensure Python 3 is installed.

3. Prepare the questions:

Ensure you have a Questions.py file with the following structure:

```python
Copy code
Q_and_A = [
    ("Question 1", ["Option 1", "Option 2", "Option 3", "Option 4"], "Correct Answer"),
    ("Question 2", ["Option 1", "Option 2", "Option 3", "Option 4"], "Correct Answer"),
    ...
]
```

## Running the Server
1. Execute the server script:

```sh
python server.py
```

2. Configure the server:

- Enter the IP address, port number, and the number of participants.
- Set the timer values for quiz start, question time, and answer time.
- Configure the marking scheme (winning marks and negative marks).
- Click "Start Server".

3. Server will wait for clients to join:

The server will display a message with the IP address and port number it's listening on.

## Running the Client

1. Execute the client script:

```sh
python client.py
```

2. Connect to the server:

* Enter the IP address and port number provided by the server.
* Enter your name and click "Join Server".

3. Participate in the quiz:

- Wait for the quiz to start as indicated by the server.
- Press the buzzer button when a question is displayed to answer first.
- Enter your answer when prompted and submit.

## Game Flow
1. The server shuffles and presents questions to all connected clients.
2. Clients press the buzzer to answer questions within a specified time.
3. Points are awarded for correct answers, and deducted for wrong answers or failing to answer after pressing the buzzer.
4. The game continues until all questions are asked or a player reaches the winning score.

## Configuration Options
- Server Configuration:

    Set IP, Port, Number of Participants, Quiz Start Timer, Question Timer, Answer Timer, Winning Marks, and Deduction Marks.
- Client Configuration:

    Set IP, Port, and Player Name.

## Notes
* Ensure the server is running before clients attempt to join.
* The server must be reachable by clients via the specified IP address and port.
* Timer values must be greater than 3 seconds to ensure smooth game flow.
* The number of participants should be between 1 and 4.

## Troubleshooting
* Connection Issues: Verify the server's IP address and port are correct and accessible.
* Duplicate Names: Ensure each client uses a unique name.
* Timers: Ensure timer values are set correctly and are greater than 3 seconds.

### Done By:
Achraf Hoteit

Nancy Monzer

Ribal Zaiter
