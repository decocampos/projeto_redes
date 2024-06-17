#IMPORTAÇÃO DE BIBLIOTECAS EXTERNAS
import math
import socket
import threading
import random

#IMPORTAÇÃO DA BIBLIOTECA AUTORAL DO PROJETO
from suport import database           #buffer_size, server_add e default_output_size
from suport import convert_str_to_txt #função que converte a mensagem para um arquivo .txt
from suport import create_package     #função que cria o pacote de 1024 bytes
from suport import default_output

#Criando a socket do client e conectando-a ao servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind((database.server_address, random.randint(1025, 24999)))

def receive_message():
    while True:
        try:
            message_data, _ = client_socket.recvfrom(database.buffer_size)
            print(message_data.decode())
        except:
            print("Ocorreu algum erro.\nLinha 15-22, File: client.py")
            pass

receive_thread = threading.Thread(target=receive_message) #cria um thread para a funcao receive_message
receive_thread.start() #starta a thread
def client():
    conection_with_server = False
    global username
    onChat = True

    #======================================================================================
    #caso 1: Logar novo usuário
    #caso 2: Deslogar usuário
    #caso 3: Usuário logado quer mandar mensagem
    #=============================LOOP PRINCIPAL===========================================
    while onChat:
        client_address = client_socket.getpeername()[0]
        command_or_message = input()

        # =========================================CASO 1=============================================

        if command_or_message.startswith("hi, meu nome eh "): #caso 1
                                                              # °caso 1.1 = não está conectado
                                                              # ºcaso 1.2 = está conectado

            if conection_with_server == False: #caso 1.1
                username = command_or_message[16:]                #o que vem depois de "hi, meu nome eh "
                client_socket.sendto(f"*$*: {username} caiu de paraquedas no server!", (client_address, 25000))
                conection_with_server = True

            elif conection_with_server == True:            #caso 1.2
                print(f'Você já estava conectado, pode chatear, {username}')

        # ===========================================CASO 2===========================================

        elif command_or_message == "bye":                     # caso 2
                                                     # °caso 2.1 = não está conectado
                                                     # ºcaso 2.2 = está conectado
            if conection_with_server == False: #caso 2.1
                print("Você precisa estar conectado para se desconectar")

            else:            #caso 2.2
                client_socket.sendto(command_or_message.encode(), (database.server_address))
                print(f'*#*: {username} não está mais entre nós :(')
                onChat = False
                conection_with_server = True

        # =============================================CASO 3=========================================

        elif conection_with_server:
            txt_path_file = convert_str_to_txt.convert_str_to_txt\
                (username, command_or_message) #crio um txt contendo o conteúdo de
                                               #"command_or_message", que no caso, é uma "message"

            txt_file = open(txt_path_file, 'rb') #'rb' = read_bytes, ou seja, o código lê o arquivo txt byte a byte.
            charactesrs = txt_file.read()
            package_quantity = math.ceil(len(charactesrs))
            package_size = 8
            package_index = 0
            while charactesrs:
                package = create_package.create_package(charactesrs ,package_size, package_index, package_quantity)
                client_socket.sendto(package, database.server_address) #envia o pacote pro backend
                charactesrs = charactesrs[package_size:] #retira os pacotes enviados
                package_index = package_index + 1 #pula pra proximo pacote

        else:
            print(default_output.default_output_message('ERRO'))

client()
