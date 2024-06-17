#TO-DO: Broadcast

#IMPORTAÇÃO DE BIBLIOTECAS EXTERNAS
import socket
import struct
import threading
import queue
import time
import io

#IMPORTAÇÃO DA BIBLIOTECA AUTORAL DO PROJETO
from suport import database
from suport import get_time_data
from suport import convert_str_to_txt

#Definições de parâmetros fixos
SERVER_ADDRESS = database.server_address
BUFFER_SIZE = database.buffer_size
HEADER_SIZE = database.header_size

clients_usernames = []
clients_address = []

#Definindo que as mensagens serão armazenadas numa fila
messages_queue = queue.Queue()

#Criando socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_ADDRESS))

#disconnect_user -> Função que desconecta um usuário
#receive_message
#send_to_all

def reconstruct_message(received_message_list):
    buffer = io.BytesIO()
    for package in received_message_list:
        buffer.write(package)
    return buffer.getvalue()
def receive_message():
    received_packages = 0
    received_message_list = []

    while True:
        try: #Conectar, Desconectar ou Mandar mensagem
            initial_message, ip_client = server_socket.recvfrom(BUFFER_SIZE)

            sign_up = initial_message.decode().startswith('*$*')
            disconnect = initial_message.decode().startswith('*#*')

            #COMANDO
            if sign_up or disconnect:
                messages_queue.put((initial_message, ip_client))

            #MENSAGEM
            else:
                #Separando o header da mensagem
                header = initial_message[:16]
                message_received_bytes = initial_message[16:]

                #Descompactando o header
                packageSize, packageIndex, packagesQuantity, checksum = struct.unpack('!IIII', header)

                if len(received_message_list) < packagesQuantity:
                    extend = int(packageIndex - len(received_message_list))
                    received_message_list.extend([''] * extend)

                received_message_list[packageIndex] = message_received_bytes
                received_packages += 1

                if received_packages == packagesQuantity: #atenção
                    reconstrcted_message = reconstruct_message(received_message_list)
                    reconstrcted_message.decode()
                    for address in clients_address:
                        if address == ip_client:
                            client_index = clients_address.index(address)
                            name = clients_usernames[client_index]
                            file = convert_str_to_txt.convert_str_to_txt(name, reconstrcted_message, backEnd=True)
                            with open(file, 'r', ) as txt:
                                message = f'{name}: {txt.read()}'.encode()
                            messages_queue.put((message, ip_client))

                            received_message_list = []
                            received_packages = 0
                            break

                elif (packageIndex == packagesQuantity-1) and (received_packages < packagesQuantity):
                    for address in clients_address:
                        if address == ip_client:
                            client_index = clients_address.index(address)
                            name = clients_usernames[client_index]

                            print(f'Algum pacote do usuário {name} foi perdido')
                            received_packages = 0
                            received_message_list = []

        except UnicodeDecodeError:
            print("Erro de decodificação: A mensagem não está no formato UTF-8.")
            #Lida com o erro de decodificação da mensagem (por exemplo, ignora a mensagem)

        except struct.error:
            print("Erro de desempacotamento: O cabeçalho da mensagem está corrompido.")
            #Lida com o erro de desempacotamento do cabeçalho (por exemplo, ignora a mensagem)

        except socket.timeout:
            print("Tempo limite excedido: Não foi possível receber a mensagem completa.")
            #Lida com o erro de timeout (por exemplo, tenta receber novamente)

def disconnetct_client(client_to_remove_address):
    client_to_remove_index = int(clients_address.index(client_to_remove_address))
    clients_address.remove(client_to_remove_index)
    clients_usernames.pop(client_to_remove_index)



