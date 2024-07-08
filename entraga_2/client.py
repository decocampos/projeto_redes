#IMPORTAÇÃO DE BIBLIOTECAS EXTERNAS
import math
import socket
import threading
import random
from zlib import crc32
import struct

#IMPORTAÇÃO DA BIBLIOTECA AUTORAL DO PROJETO
from suport import database, convert_str_to_txt, default_output

#Criando a socket do client e conectando-a ao servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
random_door = random.randint(1025, 24999)
client_socket.bind(('', random_door))
SERVER_ADDRESS_INT = database.server_adress_1
PACKAGE_SIZE = database.packages_size

ACK = False
NACK = False
sent = False
sequence_number = None

def define_sequence():
    global sequence_number
    print(sequence_number)
    if sequence_number is not None:
        print("hello" + str(sequence_number))
        sequence_number = (sequence_number + 1) % 2
    else:
        sequence_number = 0
    return sequence_number



def receive_message():
    global ACK, NACK, sequence_number
    while True:
        message_garbage, _ = client_socket.recvfrom(1024)
        message = message_garbage.decode("ISO-8859-1")
        print(message)
        if message == '//ACK//':
            ACK = True
            NACK = False
        elif message == '//NACK//':
            ACK = False
            NACK = True
        else:
            ACK = False
            NACK = False

def corrupt_data(byte_data):
    # Convert data to a list of bytes
    # Randomly flip a bit in a byte
    index = random.randint(0, len(byte_data) - 1)
    bit = 1 << random.randint(0, 7)
    byte_data[0] ^= bit

    return byte_data


def client():
    conection_with_server = False
    global username, ACK, NACK, sequence_number

    #======================================================================================
    #caso 1: Logar novo usuário
    #caso 2: Deslogar usuário
    #caso 3: Usuário logado quer mandar mensagem
    #=============================LOOP PRINCIPAL===========================================
    while True:
        command_or_message = input("")

        # =========================================CASO 1=============================================

        if command_or_message.startswith("hi, meu nome eh "): #caso 1
                                                              # °caso 1.1 = não está conectado
                                                              # ºcaso 1.2 = está conectado

            if conection_with_server == False: #caso 1.1
                username = command_or_message[16:]                #o que vem depois de "hi, meu nome eh "
                client_socket.sendto(f"*$*{username} caiu de paraquedas no server!".encode("ISO-8859-1"), ('localhost', SERVER_ADDRESS_INT))
                conection_with_server = True

            elif conection_with_server == True:            #caso 1.2
                print(f'Você já estava conectado, pode chatear, {username}')

        # ===========================================CASO 2===========================================

        elif command_or_message == "bye":                     # caso 2

            if conection_with_server == False:
                print("Você precisa estar conectado para se desconectar")

            else:
                client_socket.sendto(f"*#*{username}  nao esta mais entre nos. :(".encode("ISO-8859-1"), ('localhost', SERVER_ADDRESS_INT))
        # =============================================CASO 3=========================================

        elif conection_with_server:
            txt_path_file = convert_str_to_txt.convert_str_to_txt(username, command_or_message) #crio um txt contendo o conteúdo de
                                                                                                #"command_or_message", que no caso, é uma "message"

            txt_file = open(txt_path_file)
            charactesrs = txt_file.read()
            encoded_characters = charactesrs.encode("ISO-8859-1")
            package_quantity = math.ceil(len(charactesrs)/PACKAGE_SIZE)
            package_index = 0
            ACK = False
            NACK = False
            message_bytearray = bytearray()
            hashVerify = crc32(encoded_characters[:PACKAGE_SIZE])

            message_bytearray.extend(encoded_characters[:PACKAGE_SIZE])
            package_header = struct.pack(f'!IIIII', PACKAGE_SIZE, package_index, package_quantity, hashVerify, define_sequence())
            package = package_header + corrupt_data(message_bytearray)

            client_socket.sendto(package, database.server_address_tuple)  # envia o pacote pro backend


            while charactesrs:
                if ACK:
                    encoded_characters = encoded_characters[PACKAGE_SIZE:]
                    charactesrs = charactesrs[PACKAGE_SIZE:] #retira os pacotes enviados
                    package_index = package_index + 1 #pula pra proximo pacote
                    if charactesrs:
                        message_bytearray = bytearray()
                        hashVerify = crc32(encoded_characters[:PACKAGE_SIZE])

                        message_bytearray.extend(encoded_characters[:PACKAGE_SIZE])
                        package_header = struct.pack(f'!IIIII', PACKAGE_SIZE, package_index, package_quantity,
                                                     hashVerify, define_sequence())
                        package = package_header + message_bytearray

                        client_socket.sendto(package, database.server_address_tuple) #envia o pacote pro backend
                    ACK = False
                elif NACK:
                    message_bytearray = bytearray()
                    hashVerify = crc32(encoded_characters[:PACKAGE_SIZE])

                    message_bytearray.extend(encoded_characters[:PACKAGE_SIZE])
                    package_header = struct.pack(f'!IIIII', PACKAGE_SIZE, package_index, package_quantity, hashVerify,
                                                 define_sequence())
                    package = package_header + message_bytearray

                    client_socket.sendto(package, database.server_address_tuple)  # envia o pacote pro backend
                    NACK = False


        else:
            print(default_output.default_output_message())

receive_thread = threading.Thread(target=receive_message) #cria um thread para a funcao receive_message
receive_thread.start() #starta a thread

client()
