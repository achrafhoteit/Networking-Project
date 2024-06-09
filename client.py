import socket
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font

MSG_LEN = 5

RED = "#FF0000"
GREEN = "#1D5C06"
BLUE = "#0000FF"
WHITE = "#FFFFFF"
timer_thread = None
run_timer = True
hidden = False
Host = 'localhost'
Port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_name_to_server(socket, message):
    print("sending name")
    if message == "":
        print("Please choose a name and join again")
        print("DISCONNECTED")
        sys.exit()
    else:
        try:
            socket.send(bytes(message, 'utf-8'))
        except:
            socket.close()


def receive_messages():
    question_text = " "
    winner_info = ""
    duration = 10
    wait = 10
    answer_time = 10
    global timer_thread
    global run_timer
    while True:
        try:
            encoded_message_len = server.recv(MSG_LEN)
            if not encoded_message_len:
                print("DISCONNECTED")
                sys.exit()
            message_len = int(encoded_message_len.decode('utf-8').strip())
            data = server.recv(message_len)
            message = data.decode('utf-8')
            print(message)
            if "ENTER YOUR ANSWER:" in message:
                timer_label_type.config(text="Time Left:")
                submit_button.config(state="normal", bg=BLUE, fg=WHITE)
            else:
                submit_button.config(state="disabled", bg=WHITE, fg=BLUE)
            # disabling submit until buzzer is pressed
            # submit_button.config(state="disabled", bg=WHITE, fg=BLUE)
            # buzzer_button.config(state="disabled", bg=WHITE, fg=BLUE)
            # Check different conditions based on the message received
            if "Quiz time:" in message:
                wait = message[11:]
                print(wait)

            elif "Question time:" in message:
                duration = message[15:]
                print(duration)

            elif "Answer time:" in message:
                answer_time = message[13:]
                print(answer_time)

            elif "INSTRUCTIONS:" in message:
                hide_widgets()
                if timer_thread is not None:
                    run_timer = False
                    timer_thread.join()
                    run_timer = True

                timer_label_type.config(text="Starts after:")

                update_question(message)
                timer_thread = threading.Thread(target=countdown_timer, args=(wait,))
                timer_thread.start()

            elif "Q. " in message:
                if timer_thread is not None:
                    run_timer = False
                    timer_thread.join()
                    # Wait for the timer thread to finish
                    run_timer = True

                show_widgets()
                answer_entry.set("")
                timer_label_type.config(text="Timer:")
                # thread for timer
                timer_thread = threading.Thread(target=countdown_timer, args=(duration,))
                timer_thread.start()

                buzzer_label.config(text="BUZZER STATUS HERE")
                answer_status.config(text="ANSWER STATUS HERE")
                buzzer_button.config(state="normal", bg=RED, fg=WHITE)
                question_text = message
                update_question(question_text)

            elif message == "All questions asked!":
                # Handle end of quiz
                update_question(question_text)
                sys.exit()

            elif any(option in message for option in
                     ["Hit buzzer to answer", "YOU PRESSED THE BUZZER", "ENTER YOUR ANSWER:", "BUZZER PRESSED",
                      "BUZZER NOT PRESSED"]):
                buzzer_label.config(text=message)

                if any(option in message for option in
                       ["YOU PRESSED THE BUZZER", "ENTER YOUR ANSWER:", "BUZZER PRESSED",
                        "BUZZER NOT PRESSED"]):
                    buzzer_button.config(state="disabled", bg=RED, fg=WHITE)

                    if any(option in message for option in
                           ["YOU PRESSED THE BUZZER", "BUZZER PRESSED"]):
                        if timer_thread is not None:
                            run_timer = False
                            timer_thread.join()  # Wait for the timer thread to finish
                            run_timer = True

                        timer_thread = threading.Thread(target=countdown_timer, args=(answer_time,))
                        timer_thread.start()

                    elif "BUZZER NOT PRESSED" in message:
                        if timer_thread is not None:
                            run_timer = False
                            timer_thread.join()  # Wait for the timer thread to finish
                            run_timer = True

                        timer_label_type.config(text="Next question after:")
                        timer_thread = threading.Thread(target=countdown_timer, args=(duration,))
                        timer_thread.start()

                    buzzer_button.config(state="disabled", bg=WHITE, fg=BLUE)

            elif any(option in message for option in ["CORRECT ANSWER", "WRONG ANSWER"]):
                if timer_thread is not None:
                    run_timer = False
                    timer_thread.join()
                    run_timer = True

                timer_label_type.config(text="Next question after:")
                buzzer_label.config(text="Buzzer status here")
                answer_status.config(text=message)

            elif any(option in message for option in ["Score of", "added to", "deducted from"]):
                if timer_thread is not None:
                    run_timer = False
                    timer_thread.join()
                    run_timer = True

                timer_label_type.config(text="Next question after:")
                timer_thread = threading.Thread(target=countdown_timer, args=(duration,))
                timer_thread.start()
                if "Score of" in message:
                    update_score(message[8:])

            elif any(option in message for option in ["1)", "2)", "3)", "4)"]):
                question_text += "\n" + message
                update_question(question_text, anchor="w")  # Align left

            elif any(option in message for option in ["PLAYER", "Scoreboard:", "WINNER:"]):
                if "WINNER" in message:
                    timer_label_type.config(text="Quiz Ended")

                    buzzer_label.destroy()
                    buzzer_button.destroy()
                    answer_label.destroy()
                    answer_status.destroy()
                    answer_entry.destroy()

                winner_info += "\n" + message
                update_question(winner_info)

            else:
                update_question(message)

        except Exception as e:
            print("GAME OVER")
            sys.exit()


def send_answer():
    answer = answer_entry.get()
    try:
        server.send(bytes(answer, 'utf-8'))
    except:
        print("Cannot send message to server")


def send_buzzer():
    global run_timer
    global timer_thread
    try:
        if timer_thread is not None:
            run_timer = False
            timer_thread.join()  # Wait for the timer thread to finish
            run_timer = True

        server.send(b"BUZZER")
    except:
        print("Cannot send buzzer signal to server")


def update_question(question_text, anchor="center"):
    question_label.config(text=question_text, anchor=anchor)


def update_score(score):
    score_label.config(text="Score: " + str(score))


# Functionality to send name to server
def join_server():
    global Host
    global Port
    global server
    name = name_entry.get()
    Host = ip_entry.get()
    Port = int(port_entry.get())

    try:
        server.connect((Host, Port))
    except:
        print("CAN'T CONNECT TO SERVER!")
        sys.exit()

    # Start a separate thread for receiving messages
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()
    send_name_to_server(server, name)

    name_entry.config(state="disabled")
    join_button.destroy()  # Remove the "Join Server" button
    join_panel.pack_forget()  # Hide the join panel
    quiz_panel.pack()  # Display the quiz panel


def countdown_timer(duration):
    remaining_time = int(duration)
    while remaining_time >= 0 and run_timer:
        mins, secs = divmod(remaining_time, 60)
        timer_text = '{:02d}:{:02d}'.format(mins, secs)
        print(timer_text, end="\r")
        timer_label.config(text='{:02d}:{:02d}'.format(mins, secs))
        time.sleep(1)
        remaining_time -= 1


def hide_widgets():
    global hidden
    hidden = True
    buzzer_label.grid_remove()
    buzzer_button.grid_remove()
    answer_label.grid_remove()
    answer_entry.grid_remove()
    answer_status.grid_remove()
    submit_button.grid_remove()


def show_widgets():
    global hidden
    if hidden:
        hidden = False
        # Show widgets by placing them back in the grid
        buzzer_label.grid(row=4, column=0, columnspan=5)

        buzzer_button.grid(row=5, column=0, columnspan=5, padx=10, pady=1, sticky="ew")

        answer_label.grid(row=6, column=0, columnspan=5)

        answer_entry.grid(row=7, column=0, columnspan=5, padx=5, pady=1)

        answer_status.grid(row=8, column=0, columnspan=5)

        submit_button.grid(row=9, column=0, columnspan=5, padx=10, pady=1, sticky="ew")


# Create Tkinter GUI window
root = tk.Tk()
root.title("Quiz Game")
root.geometry("500x700")  # Set window size

font_size = 13
# Create a font object with the desired size
custom_font = font.Font(size=font_size)

# Set background color for all widgets
root.configure(bg=WHITE)

# Create Join Panel
join_panel = tk.Frame(root, bg=WHITE)
join_panel.pack()

ip_label = tk.Label(join_panel, text="Enter IP:", bg=WHITE)
ip_label.grid(row=0, column=0, sticky="news")
ip_entry = tk.Entry(join_panel)
ip_entry.grid(row=0, column=1)

port_label = tk.Label(join_panel, text="Enter Port:", bg=WHITE)
port_label.grid(row=1, column=0, sticky="news")
port_entry = tk.Entry(join_panel)
port_entry.grid(row=1, column=1)

# Input for name
name_label = tk.Label(join_panel, text="Enter Name:", bg=WHITE)
name_label.grid(row=2, column=0, sticky="news")
name_entry = tk.Entry(join_panel)
name_entry.grid(row=2, column=1)

ip_entry.insert(0, Host)
port_entry.insert(0, str(Port))
# Button to join server
join_button = tk.Button(join_panel, text="Join Server", command=join_server, fg=WHITE, bg=GREEN, padx=10, pady=5)
join_button.grid(row=3, columnspan=2, pady=5, sticky="news")

# Create Quiz Panel
quiz_panel = tk.Frame(root, bg=WHITE)

# quiz_panel.grid_rowconfigure(0, minsize=20)
# quiz_panel.grid_rowconfigure(1, minsize=20)
quiz_panel.grid_rowconfigure(2, minsize=50)
quiz_panel.grid_rowconfigure(3, minsize=100)
quiz_panel.grid_rowconfigure(4, minsize=50)
# quiz_panel.grid_rowconfigure(5, minsize=50)  # Button to signal buzzer
# quiz_panel.grid_rowconfigure(6, minsize=50)  # Answer entry
# quiz_panel.grid_rowconfigure(7, minsize=50)  # Answer status
# quiz_panel.grid_rowconfigure(8, minsize=50)  # Button to submit answer
# quiz_panel.grid_rowconfigure(9, minsize=50)
quiz_panel.grid_columnconfigure(0, weight=1)  # Left column
quiz_panel.grid_columnconfigure(1, weight=1)  # Center column
quiz_panel.grid_columnconfigure(2, weight=1)  # Right column

# Timer Type Label
timer_label_type = tk.Label(quiz_panel, text="Quiz Timer", font=custom_font)
timer_label_type.grid(row=0, column=0, columnspan=3)

# Timer display
timer_label = tk.Label(quiz_panel, text="Start after: ", fg=BLUE, font=custom_font)
timer_label.grid(row=1, column=0, columnspan=3, sticky="ew")

# Score display
score_label = tk.Label(quiz_panel, text="Score: 0", bg=WHITE, font=custom_font)
score_label.grid(row=2, column=0, columnspan=5)

# Question display
question_label = tk.Label(quiz_panel, text="Waiting Server to start or Connection Full", wraplength=400, bg=WHITE, font=custom_font)
question_label.grid(row=3, column=0, columnspan=5)

# Buzzer status
buzzer_label = tk.Label(quiz_panel, text="Your buzzer status here", fg=RED, bg=WHITE)
# buzzer_label.grid(row=4, column=0, columnspan=5)

# Button to signal buzzer
buzzer_button = tk.Button(quiz_panel, text="Buzzer", command=send_buzzer, fg=WHITE, bg=RED, padx=10, pady=5)
# buzzer_button.grid(row=5, column=0, columnspan=5, padx=10, pady=1, sticky="ew")

# Answer entry
answer_label = tk.Label(quiz_panel, text="Select Answer: ", fg=BLUE, bg=WHITE)
answer_label.grid(row=6, column=0, columnspan=5)
answer_var = tk.StringVar()
answer_entry = ttk.Combobox(quiz_panel, textvariable=answer_var, values=["1", "2", "3", "4"])
# answer_entry.grid(row=7, column=0, columnspan=5, padx=5, pady=1)

# Answer status
answer_status = tk.Label(quiz_panel, text="Answer status", fg=BLUE, bg=WHITE)
# answer_status.grid(row=8, column=0, columnspan=5)

# Button to submit answer
submit_button = tk.Button(quiz_panel, text="Submit", command=send_answer, fg=WHITE, bg=BLUE, padx=10, pady=5)
# submit_button.grid(row=9, column=0, columnspan=5, padx=10, pady=1, sticky="ew")

root.mainloop()

server.close()
