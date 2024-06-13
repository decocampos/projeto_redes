import socket
import threading
import time

# Configuração do cliente
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024
username = ""

def receive_messages():
    while True:
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        print(data.decode())

def client():
    global username
    while True:
        command = input()
        if command.startswith("hi, meu nome eh "):
            username = command.split(" ", 4)[4]
        elif command == "bye":
            client_socket.sendto(command.encode(), (SERVER_IP, SERVER_PORT))
            print("Você saiu da sala.")
            break

        if username:
            client_socket.sendto(command.encode(), (SERVER_IP, SERVER_PORT))


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

client()
