import socket
import threading
import time

# Configuração do servidor
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
BUFFER_SIZE = 1024

clients = {}
usernames = {}

def broadcast(message, sender_address):
    for client in clients:
        if client != sender_address:
            server_socket.sendto(message.encode(), client)

def handle_client(data, address):
    data = data.decode().strip()
    if address not in usernames:
        if data.startswith("hi, meu nome eh "):
            username = data.split(" ", 4)[4]
            usernames[address] = username
            clients[address] = username
            welcome_message = f"{username} entrou na sala."
            broadcast(welcome_message, address)
    else:
        if data == "bye":
            username = usernames.pop(address, None)
            clients.pop(address, None)
            bye_message = f"{username} saiu da sala."
            broadcast(bye_message, address)
        else:
            username = usernames[address]
            timestamp = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime())
            formatted_message = f"{address[0]}:{address[1]}/~{username}: {data} {timestamp}"
            broadcast(formatted_message, address)

def server():
    while True:
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        threading.Thread(target=handle_client, args=(data, address)).start()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
print(f"Servidor UDP rodando em {SERVER_IP}:{SERVER_PORT}")

server_thread = threading.Thread(target=server)
server_thread.start()
