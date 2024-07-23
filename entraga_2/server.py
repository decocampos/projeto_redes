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
messages_queue = queue.Queue()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)

running = True

# Dicionário para armazenar o número de sequência esperado para cada cliente
expected_sequence_number = {}

def receive_message():
    global running
    while running:
        try:
            initial_message, ip_client = server_socket.recvfrom(BUFFER_SIZE)
            if initial_message.decode("ISO-8859-1").startswith('*$*') or initial_message.decode("ISO-8859-1").startswith('*#*'):
                messages_queue.put(('$#', initial_message, ip_client))
                continue

            header = initial_message[:HEADER_SIZE]
            message_received_bytes = initial_message[HEADER_SIZE:]
            packageSize, packageIndex, packagesQuantity, hashVerify, sequence_number = struct.unpack('!IIIII', header)

            # Verifica se o número de sequência é esperado
            if ip_client in expected_sequence_number:
                expected_seq_num = expected_sequence_number[ip_client]
            else:
                expected_seq_num = 0  # Define 0 como inicial se não estiver definido

            # Verifica integridade do pacote e número de sequência
            if hashVerify == crc32(message_received_bytes) and sequence_number == expected_seq_num:
                decoded_message = message_received_bytes.decode("ISO-8859-1")
                print(f'Recebido pacote seq_num: {sequence_number} de {ip_client}')
                
                # Enviar ACK e atualizar o número de sequência esperado
                acknowledgement = '//ACK//'
                expected_sequence_number[ip_client] = (expected_seq_num + 1) % 2
                
                for address in clients_address:
                    if address == ip_client:
                        client_index = clients_address.index(address)
                        name = clients_usernames[client_index]
                        file = convert_str_to_txt.convert_str_to_txt(name, decoded_message, backEnd=True)
                        with open(file, encoding="ISO-8859-1") as txt:
                            message = txt.read()
                            time_data = get_time_data.get_time_data()
                            message_to_send = f'{ip_client[0]}:{ip_client[1]}/~{name}: "{message}" {time_data}'.encode("ISO-8859-1")

                            while messages_queue.qsize() > 0:
                                time_to_wait = 0.1
                                time.sleep(time_to_wait)

                            messages_queue.put((packagesQuantity, message_to_send, ip_client))
            else:
                print(f'Erro de sequência ou dados corrompidos do cliente {ip_client}')
                acknowledgement = '//NACK//'

            # Envia ACK ou NACK
            server_socket.sendto(acknowledgement.encode("ISO-8859-1"), ip_client)

        except socket.error:
            break

def broadcast():
    global running
    while running:
        while messages_queue.qsize() != 0:
            package_quantity_or_command, encoded_message, ip_client = messages_queue.get()
            message = encoded_message.decode("ISO-8859-1")

            if package_quantity_or_command == "$#":
                message_split = message.split()
                username_garbage = message_split[0]
                command = username_garbage[:3]
                client_name = username_garbage[3:]

                if command == "*$*":
                    clients_address.append(ip_client)
                    clients_usernames.append(client_name)
                    expected_sequence_number[ip_client] = 0  # Inicializa o número de sequência esperado

                elif command == "*#*":
                    clients_address.remove(ip_client)
                    clients_usernames.remove(client_name)
                    expected_sequence_number.pop(ip_client, None)  # Remove o cliente

            for client in clients_address:
                server_socket.sendto(encoded_message, client)

def close_server():
    global running
    running = False
    server_socket.close()
    print('porta fechada')

receive_thread = threading.Thread(target=receive_message)
broadcast_thread = threading.Thread(target=broadcast)

receive_thread.start()
broadcast_thread.start()

try:
    while running:
        time.sleep(1)
except KeyboardInterrupt:
    close_server()
    receive_thread.join()
    broadcast_thread.join()
