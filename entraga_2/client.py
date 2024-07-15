# IMPORTAÇÃO DE BIBLIOTECAS EXTERNAS
import math
import socket
import threading
import random
from zlib import crc32
import struct

# IMPORTAÇÃO DA BIBLIOTECA AUTORAL DO PROJETO
from suport import database, convert_str_to_txt, default_output

# Criando a socket do client e conectando-a ao servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
random_door = random.randint(1025, 24999)
client_socket.bind(('', random_door))
SERVER_ADDRESS_INT = database.server_adress_1
PACKAGE_SIZE = database.packages_size

ACK = False
NACK = False
sequence_number = None
running = True

def define_sequence():
    global sequence_number
    if sequence_number is not None:
        sequence_number = (sequence_number + 1) % 2
    else:
        sequence_number = 0
    return sequence_number

def receive_message():
    global ACK, NACK, running
    while running:
        try:
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
        except socket.error:
            break 

def corrupt_data(byte_data):
    index = random.randint(0, len(byte_data) - 1)
    bit = 1 << random.randint(0, 7)
    byte_data[0] ^= bit
    return byte_data

def client():
    conection_with_server = False
    global username, ACK, NACK, sequence_number, running

    while running:
        command_or_message = input("")

        if command_or_message.startswith("hi, meu nome eh "):
            if not conection_with_server:
                username = command_or_message[16:]
                client_socket.sendto(f"*$*{username} caiu de paraquedas no server!".encode("ISO-8859-1"), ('localhost', SERVER_ADDRESS_INT))
                conection_with_server = True
            else:
                print(f'Você já estava conectado, pode chatear, {username}')

        elif command_or_message == "bye":
            if not conection_with_server:
                print("Você precisa estar conectado para se desconectar")
            else:
                client_socket.sendto(f"*#*{username} nao esta mais entre nos. :(".encode("ISO-8859-1"), ('localhost', SERVER_ADDRESS_INT))
                running = False

        elif conection_with_server:
            txt_path_file = convert_str_to_txt.convert_str_to_txt(username, command_or_message)
            txt_file = open(txt_path_file)
            charactesrs = txt_file.read()
            encoded_characters = charactesrs.encode("ISO-8859-1")
            package_quantity = math.ceil(len(charactesrs) / PACKAGE_SIZE)
            package_index = 0
            ACK = False
            NACK = False

            while charactesrs:
                message_bytearray = bytearray()
                hashVerify = crc32(encoded_characters[:PACKAGE_SIZE])
                message_bytearray.extend(encoded_characters[:PACKAGE_SIZE])
                encoded_characters = encoded_characters[PACKAGE_SIZE:]
                package_header = struct.pack(f'!IIIII', PACKAGE_SIZE, package_index, package_quantity, hashVerify, define_sequence())
                package = package_header + message_bytearray

                while True:
                    client_socket.sendto(package, database.server_address_tuple)
                    print(f'Pacote com seq_num: {sequence_number} enviado.')

                    client_socket.settimeout(2)
                    try:
                        ack_message, _ = client_socket.recvfrom(1024)
                        ack_message = ack_message.decode("ISO-8859-1")
                        if ack_message == '//ACK//':
                            print(f'ACK para seq_num: {sequence_number} recebido.')
                            break
                        elif ack_message == '//NACK//':
                            print(f'NACK recebido. Reenviando pacote seq_num: {sequence_number}.')
                    except socket.timeout:
                        print(f'Tempo esgotado para seq_num: {sequence_number}. Reenviando pacote...')

                package_index += 1
                charactesrs = charactesrs[PACKAGE_SIZE:]

        else:
            print(default_output.default_output_message())

def close_client():
    global running
    running = False
    client_socket.close()
    print('porta fechada')

receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

try:
    client()
finally:
    close_client()
    receive_thread.join()
