import threading
import struct
import socket
import queue
import time
from suport import database, get_time_data, convert_str_to_txt
from zlib import crc32

#configuração do servidor a partir do banco de dados
SERVER_ADDRESS = database.server_address_tuple
BUFFER_SIZE = database.buffer_size
HEADER_SIZE = database.header_size

#Listas para armazenar os nomes de usuários e endereços dos clientes 
clients_usernames = []
clients_address = []

#fila para armazenar mensagens a serem transmitidas
messages_queue = queue.Queue()

#cria um socket UDP no endereço do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(SERVER_ADDRESS)

#variáveis de controle
running = True
ACK = False
NACK = False

#dicionário para armazenar o número de sequência esperado para cada cliente
expected_sequence_number = {}

#Receber mensagens dos clientes
def receive_message():
    global running, ACK, NACK
    while running:
        try:
            #Recebe a mensagem do cliente
            initial_message, ip_client = server_socket.recvfrom(BUFFER_SIZE)

            #verifica o tipo da mensagem recebida
            if initial_message.decode("ISO-8859-1").startswith('*$*') or initial_message.decode("ISO-8859-1").startswith('*#*'):
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
                print('//NACK//')
                continue

            #Divide a mensagem em cabeçalho e corpo
            header = initial_message[:HEADER_SIZE]
            message_received_bytes = initial_message[HEADER_SIZE:]
            packageSize, packageIndex, packagesQuantity, hashVerify, sequence_number = struct.unpack('!IIIII', header)
            decoded_message = message_received_bytes.decode("ISO-8859-1")

            #Verifica o número de sequência esperado para o cliente
            if ip_client in expected_sequence_number:
                expected_seq_num = expected_sequence_number[ip_client]
            else:
                expected_seq_num = 0  # Define 0 como inicial se não estiver definido

            # Verifica a integridade da mensagem(CHECKSUM) e o número de sequência
            if hashVerify != crc32(message_received_bytes) or sequence_number != expected_seq_num:
                acknowledgement = '//NACK//'
                server_socket.sendto(acknowledgement.encode("ISO-8859-1"), ip_client)
            else:
                acknowledgement = f'//ACK//{sequence_number}'
                expected_sequence_number[ip_client] = (expected_seq_num + 1) % 2

                server_socket.sendto(acknowledgement.encode("ISO-8859-1"), ip_client)

                #Processando a mensagem recebida
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

#transmitir mensagens para todos os clientes
def broadcast():
    global running
    while running:
        while messages_queue.qsize() != 0:
            encoded_package, ip_client = messages_queue.get()
            decoded_package = encoded_package.decode("ISO-8859-1")
            package_header = decoded_package[:12]
            decoded_message = decoded_package[12:]

            #mensagem de conexão do cliente
            if decoded_message.startswith('*$*'):
                message_split = decoded_message.split()
                username_garbage = message_split[0]
                client_name = username_garbage[3:]
                clients_address.append(ip_client)
                clients_usernames.append(client_name)
                expected_sequence_number[ip_client] = 0

            #mensagem de desconexão do cliente
            elif decoded_message.startswith('*#*'):
                message_split = decoded_message.split()
                username_garbage = message_split[0]
                client_name = username_garbage[3:]
                clients_address.remove(ip_client)
                clients_usernames.remove(client_name)

            #envia a mensagem codificada para todos os clientes conectados
            for client in clients_address:
                server_socket.sendto(encoded_package, client)

#Função para fechar o servidor
def close_server():
    global running
    running = False
    server_socket.close()
    print('porta fechada')

#inicia as threads para receber e transmitir mensagens
receive_tread = threading.Thread(target=receive_message)
broadcast_tread = threading.Thread(target=broadcast)

receive_tread.start()
broadcast_tread.start()

#Fechando as portas
try:
    while running:
        time.sleep(1)
except KeyboardInterrupt:
    close_server()
    receive_tread.join()
    broadcast_tread.join()
