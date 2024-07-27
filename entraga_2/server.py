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
            if ip_client not in dictionary_messages:
                dictionary_messages[ip_client] = {}

            if initial_message.decode("ISO-8859-1").startswith('*$*') or initial_message.decode(
                    "ISO-8859-1").startswith('*#*'):
                package_header = struct.pack("!III", 0, 1, crc32(initial_message))
                dictionary_messages[ip_client]['$#'] = [(initial_message.decode("ISO-8859-1"), package_header)]
                # messages_queue.put(('$#', initial_message, ip_client))
                continue

            if initial_message.decode("ISO-8859-1").startswith('//ACK//'):
                ACK = True
                NACK = False
                print('//ACK//')
                # messages_queue.put(('$#', initial_message, ip_client))
                continue

            if initial_message.decode("ISO-8859-1").startswith('//NACK//'):
                ACK = False
                NACK = True
                print('//ACK//')
                # messages_queue.put(('$#', initial_message, ip_client))
                continue
            header = initial_message[:HEADER_SIZE]
            message_received_bytes = initial_message[HEADER_SIZE:]
            packageSize, packageIndex, packagesQuantity, hashVerify, sequence_number = struct.unpack('!IIIII', header)
            decoded_message = message_received_bytes.decode("ISO-8859-1")


            if hashVerify != crc32(message_received_bytes):
                acknowledgement = '//NACK//'

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
                            message_to_send = f'{ip_client[0]}:{ip_client[1]}/~{name}: "{message}" {time_data}'
                        else:
                            if packageIndex == 0:
                                message_to_send = f'{ip_client[0]}:{ip_client[1]}/~{name}: "{message}'
                            elif packageIndex + 1 == packagesQuantity:
                                message_to_send = f'{message}" {time_data}'
                            else:
                                message_to_send = message
                        with dictionary_lock:
                            package_header = struct.pack(f'!III', packageIndex, packagesQuantity, crc32(message_to_send.encode("ISO-8859-1")))
                            print(len(package_header))
                            package = package_header + message_to_send.encode("ISO-8859-1")

                            if ip_client not in dictionary_messages:
                                dictionary_messages[ip_client] = {}
                            if packagesQuantity not in dictionary_messages[ip_client]:
                                dictionary_messages[ip_client][packagesQuantity] = []
                            dictionary_messages[ip_client][packagesQuantity].append((message_to_send, package_header))
                        #messages_queue.put((packagesQuantity, message_to_send, ip_client))
        except socket.error:
            break


def broadcast():
    global running, ACK, NACK
    while running:
        with dictionary_lock:
            if not dictionary_messages:
                continue

            ip_client = next(iter(dictionary_messages), None)
            if ip_client is None or not dictionary_messages[ip_client]:
                continue

            package_quantity_or_command = next(iter(dictionary_messages[ip_client]), None)
            if package_quantity_or_command is None:
                continue


            message = dictionary_messages[ip_client][package_quantity_or_command][0]

        # package_quantity_or_command, encoded_message, ip_client = messages_queue.get()
        #encoded_message = message.encode("ISO-8859-1")

        if package_quantity_or_command == "$#":
            message_split = message[0].split()
            username_garbage = message_split[0]
            command = username_garbage[:3]
            client_name = username_garbage[3:]

            if command == "*$*":
                clients_address.append(ip_client)
                clients_usernames.append(client_name)

            elif command == "*#*":
                clients_address.remove(ip_client)
                clients_usernames.remove(client_name)

        with dictionary_lock:
            print(dictionary_messages)
            sent_messages.setdefault(ip_client, {package_quantity_or_command: (message, )})
            dictionary_messages[ip_client][package_quantity_or_command].pop(0)
            if len(dictionary_messages[ip_client][package_quantity_or_command]) == 0:
                last_message = True
                del dictionary_messages[ip_client][package_quantity_or_command]
            else:
                last_message = False
            if len(dictionary_messages[ip_client]) == 0:
                del dictionary_messages[ip_client]

        for client in clients_address:
            server_socket.sendto(message[1] + message[0].encode("ISO-8859-1"), client)


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
