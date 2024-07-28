import threading
import struct
import socket
import queue
import time
from suport import database, get_time_data, convert_str_to_txt
from zlib import crc32

SERVER_ADDRESS = database.server_address_tuple
BUFFER_SIZE = database.buffer_size
HEADER_SIZE = database.header_size

clients_usernames = []
clients_address = []
dictionary_messages = {}
sent_messages = {}

messages_queue = queue.Queue()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)

running = True
ACK = False
NACK = False

dictionary_lock = threading.Lock()


def receive_message():
    global running, ACK, NACK
    while running:
        try:
            initial_message, ip_client = server_socket.recvfrom(BUFFER_SIZE)

            if initial_message.decode("ISO-8859-1").startswith('*$*') or initial_message.decode(
                    "ISO-8859-1").startswith('*#*'):
                package_header = struct.pack("!III", 0, 1, crc32(initial_message))
                messages_queue.put(((package_header + initial_message), ip_client))
                continue

            if initial_message.decode("ISO-8859-1").startswith('//ACK//'):
                ACK = True
                NACK = False
                print('//ACK//')
                continue

            if initial_message.decode("ISO-8859-1").startswith('//NACK//'):
                ACK = False
                NACK = True
                print('//ACK//')
                continue
            header = initial_message[:HEADER_SIZE]
            message_received_bytes = initial_message[HEADER_SIZE:]
            packageSize, packageIndex, packagesQuantity, hashVerify, sequence_number = struct.unpack('!IIIII', header)
            decoded_message = message_received_bytes.decode("ISO-8859-1")

            if hashVerify != crc32(message_received_bytes):
                acknowledgement = '//NACK//'
                server_socket.sendto(acknowledgement.encode("ISO-8859-1"), ip_client)

            else:
                acknowledgement = '//ACK//'

                server_socket.sendto(acknowledgement.encode("ISO-8859-1"), ip_client)

                for address in clients_address:
                    if address == ip_client:
                        client_index = clients_address.index(address)
                        name = clients_usernames[client_index]
                        file = convert_str_to_txt.convert_str_to_txt(name, decoded_message, backEnd=True)
                        with open(file, encoding="ISO-8859-1") as txt:
                            message = txt.read()
                            time_data = get_time_data.get_time_data()
                            if packagesQuantity == 1:
                                message_to_send = f'{ip_client[0]}:{ip_client[1]}/~{name}: "{message}" {time_data}'.encode(
                                    "ISO-8859-1")
                            else:
                                if packageIndex == 0:
                                    message_to_send = f'{ip_client[0]}:{ip_client[1]}/~{name}: "{message}'.encode(
                                        "ISO-8859-1")
                                elif packageIndex + 1 == packagesQuantity:
                                    message_to_send = f'{message}" {time_data}'.encode("ISO-8859-1")
                                else:
                                    message_to_send = message.encode("ISO-8859-1")
                            package_header = struct.pack('!III', packageIndex, packagesQuantity, crc32(message_to_send))
                            messages_queue.put(((package_header + message_to_send), ip_client))
        except socket.error:
            break


def broadcast():
    global running
    while running:
        while messages_queue.qsize() != 0:
            encoded_package, ip_client = messages_queue.get()
            decoded_package = encoded_package.decode("ISO-8859-1")
            package_header = decoded_package[:12]
            decoded_message = decoded_package[12:]

            if decoded_message.startswith('*$*'):
                message_split = decoded_message.split()
                username_garbage = message_split[0]
                client_name = username_garbage[3:]
                clients_address.append(ip_client)
                clients_usernames.append(client_name)

            elif decoded_message.startswith('*#*'):
                message_split = decoded_message.split()
                username_garbage = message_split[0]
                client_name = username_garbage[3:]
                clients_address.remove(ip_client)
                clients_usernames.remove(client_name)

            for client in clients_address:
                server_socket.sendto(encoded_package, client)


def close_server():
    global running
    running = False
    server_socket.close()
    print('porta fechada')


receive_tread = threading.Thread(target=receive_message)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()

try:
    while running:
        time.sleep(1)
except KeyboardInterrupt:
    close_server()
    receive_tread.join()
    broadcast_tread.join()
