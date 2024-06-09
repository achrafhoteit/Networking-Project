import socket
import threading

import select
import random
import sys
import time
from Questions import Q_and_A
from _thread import *
import tkinter as tk

MSG_LEN = 5
quiz_start = 20
question_timer = 10
answer_timer = 30
deduct_marks = -0.5
winner_marks = 1
random.shuffle(Q_and_A)
number_of_participants = 1
IP_address = '127.0.0.1'
Port = 9999
number_joined = 0
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# Function to start the server
def start_server():
    global number_of_participants
    global IP_address
    global Port
    global quiz_start
    global question_timer
    global answer_timer
    global server
    global deduct_marks
    global winner_marks
    try:
        number_of_participants = int(participants_entry.get())

        if number_of_participants > 4 or number_of_participants < 1:
            result.config(text="Please input valid number of participants: (1-4)")
            return

        IP_address = ip_entry.get()
        Port = int(port_entry.get())
        quiz_start = int(quiz_start_entry.get())
        question_timer = int(question_timer_entry.get())
        answer_timer = int(answer_timer_entry.get())
        winner_marks = int(winner_entry.get())
        deduct_marks = float(Negative_entry.get())

        if quiz_start <= 3 or question_timer <= 3 or answer_timer <= 3:
            result.config(text="Timer values should be greater than 3 seconds.")
            time.sleep(10)
            return

        server.bind((IP_address, Port))
        server.listen(10)
        print("Server started!")
        result.config(text=f"Waiting for connection on IP address and Port number: {IP_address}, {Port}")
        start_button.config(state="disabled")
        # Start timer to destroy the root window after 10 seconds
        root.after(10000, root.destroy)

        print(f"Waiting for connection on IP address and Port number: {IP_address}, {Port}")
    except ValueError:
        print(ValueError)
        print("Please enter valid values for participants, IP address, and port.")


# Create Tkinter GUI window
root = tk.Tk()
root.title("Server Configuration")

# IP address entry
ip_label = tk.Label(root, text="Enter IP Address:")
ip_label.grid(row=0, column=0, padx=10, pady=5)
ip_entry = tk.Entry(root)
ip_entry.grid(row=0, column=1, padx=10, pady=5)

# Port entry
port_label = tk.Label(root, text="Enter Port Number:")
port_label.grid(row=1, column=0, padx=10, pady=5)
port_entry = tk.Entry(root)
port_entry.grid(row=1, column=1, padx=10, pady=5)

# Number of participants entry
participants_label = tk.Label(root, text="Enter Number of Participants:")
participants_label.grid(row=2, column=0, padx=10, pady=5)
participants_entry = tk.Entry(root)
participants_entry.grid(row=2, column=1, padx=10, pady=5)

# Timer labels
timer_label = tk.Label(root, text="Timer Values", font=("Helvetica", 16, "bold"))
timer_label.grid(row=3, column=0, columnspan=2, pady=10)

quiz_start_label = tk.Label(root, text=f"Quiz Start Timer: ")
quiz_start_entry = tk.Entry(root)
quiz_start_entry.grid(row=4, column=1,  padx=10, pady=5)
quiz_start_label.grid(row=4, column=0,  padx=10, pady=5)

question_timer_label = tk.Label(root, text=f"Question Timer: ")
question_timer_entry = tk.Entry(root)
question_timer_entry.grid(row=5, column=1,  padx=10, pady=5)
question_timer_label.grid(row=5, column=0,  padx=10, pady=5)

answer_timer_label = tk.Label(root, text=f"Answer Timer: ")
answer_timer_entry = tk.Entry(root)
answer_timer_entry.grid(row=6, column=1, padx=10, pady=5)
answer_timer_label.grid(row=6, column=0,  padx=10, pady=5)

# Timer labels
timer_label = tk.Label(root, text="Marking Scheme", font=("Helvetica", 16, "bold"))
timer_label.grid(row=7, column=0, columnspan=2, pady=10)

Negative_label = tk.Label(root, text=f"Mark Deduction:")
Negative_entry = tk.Entry(root)
Negative_entry.grid(row=8, column=1, padx=10, pady=5)
Negative_label.grid(row=8, column=0,  padx=10, pady=5)

winner_label = tk.Label(root, text=f"Winning Marks:")
winner_entry = tk.Entry(root)
winner_entry.grid(row=9, column=1,  padx=10, pady=5)
winner_label.grid(row=9, column=0,  padx=10, pady=5)

result = tk.Label(root, text="")
result.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

ip_entry.insert(0, str(IP_address))
port_entry.insert(0,str(Port))
quiz_start_entry.insert(0, str(quiz_start))
question_timer_entry.insert(0, str(question_timer))
Negative_entry.insert(0,str(deduct_marks))
winner_entry.insert(0,str(winner_marks))
answer_timer_entry.insert(0, str(answer_timer))
participants_entry.insert(0, str(1))

# Button to start the server
start_button = tk.Button(root, text="Start Server", command=start_server)
start_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()


clients_list = []
participants = {}
marks = {}
mapping = {}
Person = [server]
answer = [-1]


def receive_message(client_socket):
    message = client_socket.recv(1024).decode('utf-8')
    return message


def send_to_one(receiver, message):
    message = f"{len(message):<{MSG_LEN}}" + message
    try:
        receiver.send(bytes(message, 'utf-8'))
    except:
        receiver.close()
        clients_list.remove(receiver)


def send_to_all(sender, message):
    message = f"{len(message):<{MSG_LEN}}" + message
    for socket in clients_list:
        if (socket != server and socket != sender):
            try:
                socket.send(bytes(message, 'utf-8'))
            except:
                socket.close()
                clients_list.remove(socket)


def update_marks(player, number):
    print(participants[mapping[player]])
    marks[participants[mapping[player]]] += number
    print(marks)
    send_to_all(server, f"\nNew Score: {marks}")
    send_to_one(player, "Score of " + str(marks[participants[mapping[player]]]))


def end_quiz():
    send_to_all(server, "GAME OVER\n")
    print("GAME OVER\n")
    for i in marks:
        if marks[i] >= winner_marks:
            send_to_all(server, "WINNER: " + str(i))
    send_to_all(server, "Scoreboard:")
    print("Scoreboard: ")
    for i in marks:
        send_to_all(server, "PLAYER " + str(i) + ": " + str(marks[i]))
        print("PLAYER " + str(i) + " : " + str(i) + " : " + str(marks[i]))

    time.sleep(10)
    sys.exit()


def ask_question():
    if len(Q_and_A) != 0:
        question_and_answer = Q_and_A[0]
        question = question_and_answer[0]
        options = question_and_answer[1]
        Answer = question_and_answer[2]

        random.shuffle(options)
        option_number = 1

        send_to_all(server, "\nQ. " + str(question))
        print("\nQ. " + str(question))
        for j in range(len(options)):
            send_to_all(server, "   " + str(option_number) + ") " + str(options[j]))
            print("   " + str(option_number) + ") " + str(options[j]))
            if options[j] == Answer:
                answer.pop(0)
                answer.append(int(option_number))
            option_number += 1
        send_to_all(server, "\nHit buzzer to answer")
        print("answer: option number " + str(answer))
    else:
        send_to_all(server, "All questions asked!")
        end_quiz()
        sys.exit()


def quiz():
    Person[0] = server
    random.shuffle(Q_and_A)
    ask_question()
    keypress = select.select(clients_list, [], [], 10)
    if len(keypress[0]) > 0:
        who_buzzed = keypress[0][0]
        send_to_one(who_buzzed, "YOU PRESSED THE BUZZER")
        send_to_one(who_buzzed, "ENTER YOUR ANSWER: ")
        send_to_all(who_buzzed, "BUZZER PRESSED")
        print("BUZZER PRESSED")
        time.sleep(0.01)
        Person.pop(0)
        Person.append(who_buzzed)
        t0 = time.time()
        Q_and_A.pop(0)

        answering = select.select(Person, [], [], 10)
        if len(answering) > 0:
            if time.time() - t0 >= answer_timer:
                send_to_one(who_buzzed, "NOT ANSWERED!")
                send_to_all(server, str(participants[mapping[who_buzzed]]) + f" {deduct_marks}")
                print(str(participants[mapping[who_buzzed]]) + f" {deduct_marks}")
                update_marks(who_buzzed, deduct_marks)
                time.sleep(question_timer)
                quiz()
            else:
                time.sleep(question_timer)
                quiz()
        else:
            print("NOTHING!")
    else:
        send_to_all(server, "BUZZER NOT PRESSED")
        print("BUZZER NOT PRESSED")
        time.sleep(question_timer)
        Q_and_A.pop(0)
        quiz()


clients_list.append(server)

while True:
    rList, wList, error_sockets = select.select(clients_list, [], [])
    for socket in rList:
        if socket == server:
            client_socket, client_address = server.accept()
            if number_joined == number_of_participants:
                send_to_one(client_socket, "Maximum number of players joined!")
                client_socket.close()
            else:
                name = receive_message(client_socket)
                if name:
                    if name in participants.values():
                        send_to_one(client_socket, "Name already taken. Please choose a different one and join again!")
                        client_socket.close()
                    else:
                        participants[client_address] = name
                        marks[name] = 0
                        number_joined += 1
                        mapping[client_socket] = client_address
                        clients_list.append(client_socket)
                        print("Participant connected: " + str(client_address) + " [ " + participants[
                            client_address] + " ]")
                        if number_joined < number_of_participants:
                            send_to_one(client_socket,
                                        "Welcome to the quiz " + name + "!\nPlease wait for other participants to "
                                                                        "join...")

                        if number_joined == number_of_participants:
                            send_to_all(server, "\nParticipant(s) joined:")
                            send_to_all(server, f"\nQuiz time: {quiz_start}")
                            send_to_all(server, f"\nQuestion time: {question_timer}")
                            send_to_all(server, f"\nAnswer time: {answer_timer}")
                            for i in participants:
                                send_to_all(server, ">> " + participants[i])
                            send_to_all(server,
                                        "\nThe quiz will begin in 30 seconds. Quickly go through the instructions\n")
                            send_to_all(server,
                                        f"INSTRUCTIONS:\n* For each question you will be provided {question_timer} seconds to press the buzzer.\n* To press the buzzer, Click on buzzer\n> After pressing the buzzer you will be provided {answer_timer} seconds to answer the question.\n\n* You will be awarded 1 point in the following case:\n  * If you enter the correct option number after pressing the buzzer first\n\n> {deduct_marks} points will be deducted in the following cases:\n  * If you press the buzzer first and give wrong answer\n  > If you press the buzzer first but don't give the answer\n  * If you provide any other answer other than the option numbers(1 to 4)\n\n* First person to score {winner_marks} points and above is the winner\n\nALL THE BEST!")
                            print("\n" + str(
                                number_of_participants) + f" participant(s) connected! The quiz will begin in {quiz_start} seconds")
                            time.sleep(quiz_start)
                            start_new_thread(quiz, ())
        else:
            msg = receive_message(socket)
            print(msg)
            if socket == Person[0]:
                try:
                    ans = int(msg)
                    if ans == answer[0]:
                        send_to_one(socket, "CORRECT ANSWER")
                        send_to_all(server, "added to " + str(participants[mapping[socket]]) + " +1")
                        print(str(participants[mapping[socket]]) + " +1")
                        update_marks(socket, 1)
                        Person[0] = server
                        if marks[participants[mapping[socket]]] >= winner_marks:
                            end_quiz()

                    else:
                        send_to_one(socket, "WRONG ANSWER")
                        send_to_all(server, "deducted from" + str(participants[mapping[socket]]) + f" {deduct_marks}")
                        print(str(participants[mapping[socket]]) + f" {deduct_marks}")
                        update_marks(socket, deduct_marks)
                        Person[0] = server
                except ValueError:
                    send_to_one(socket, "INVALID OPTION")
                    send_to_all(server, str(participants[mapping[socket]]) + f" {deduct_marks}")
                    print(str(participants[mapping[socket]]) + f" {deduct_marks}")
                    update_marks(socket, deduct_marks)
                    Person[0] = server

            elif Person[0] != server:
                send_to_one(socket, "TOO LATE!")

client_socket.close()
server.close()


