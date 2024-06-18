import threading
import struct
import socket
import queue
from suport import database, get_time_data, convert_str_to_txt
from zlib import crc32

SERVER_ADDRESS = database.server_address_tuple
BUFFER_SIZE = database.buffer_size
HEADER_SIZE = database.header_size

clients_usernames = []
clients_address = []
messages_queue = queue.Queue()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)


def receive_message():

    while True:
        initial_message, ip_client = server_socket.recvfrom(BUFFER_SIZE)

        if initial_message.decode("ISO-8859-1").startswith('*$*') or initial_message.decode("ISO-8859-1").startswith('*#*'):
            messages_queue.put((initial_message, ip_client))
            continue

        header = initial_message[:HEADER_SIZE]
        message_received_bytes = initial_message[HEADER_SIZE:]
        packageSize, packageIndex, packagesQuantity, checksum = struct.unpack('!IIII', header)
        decoded_message = message_received_bytes.decode("ISO-8859-1")

        if checksum != crc32(message_received_bytes):
            decoded_message += ' [MENSAGEM COM PACOTE PERDIDO]'

        for address in clients_address:
            if address == ip_client:
                client_index = clients_address.index(address)
                name = clients_usernames[client_index]
                file = convert_str_to_txt.convert_str_to_txt(name, decoded_message, backEnd=True)
                with open(file, 'r', encoding="ISO-8859-1") as txt:
                    time = get_time_data.get_time_data()
                    message = f'{ip_client[0]}:{ip_client[1]}/~{name}: "{txt.read()}" {time}'.encode("ISO-8859-1")
                messages_queue.put((message, ip_client))

def disconnetct_client(client_to_remove_address, name):
    clients_address.remove(client_to_remove_address)
    clients_usernames.remove(name)

def broadcast():
    while True:
        while messages_queue.qsize() != 0:
            encoded_message, ip_client = messages_queue.get()
            message = encoded_message.decode("ISO-8859-1")
            message_split = message.split()
            username_garbage = message_split[0]  #{username}
            command = username_garbage[:3]
            client_name = username_garbage[3:]

            if command == "*$*":
                clients_address.append(ip_client)
                clients_usernames.append(client_name)

            elif command == "*#*":
                disconnetct_client(ip_client, client_name)
                encoded_message = f'{client_name} nao esta mais entre nos. :('.encode("ISO-8859-1")


            for client in clients_address:
                server_socket.sendto(encoded_message, client)


receive_tread = threading.Thread(target=receive_message)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()
