#IMPORTAÇÃO DE BIBLIOTECAS EXTERNAS
import math
import socket
import threading
import random

#IMPORTAÇÃO DA BIBLIOTECA AUTORAL DO PROJETO
from suport import database           #buffer_size, server_add e default_output_size
from suport import convert_str_to_txt #função que converte a mensagem para um arquivo .txt
from suport import create_package     #função que cria o pacote de 1024 bytes

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
    #caso 1: Logar novo usuário
    #caso 2: Deslogar usuário
    #caso 3: Usuário logado quer mandar mensagem

    global username
    onChat = True
    while onChat:
        command_or_message = input()
        if command_or_message.startswith("hi, meu nome eh "): #caso 1
                                                    # °caso 1.1 = não está conectado
                                                    # ºcaso 1.2 = está conectado
            if not username: #caso 1.1
                username = command_or_message[16:]                #o que vem depois de "hi, meu nome eh "

            else:            #caso 1.2
                print(f'Você já está conectado, pode chatear, {username}')

        elif command_or_message == "bye":                     # caso 2
                                                     # °caso 2.1 = não está conectado
                                                     # ºcaso 2.2 = está conectado
            if not username: #caso 2.1
                print("Você precisa estar conectado para se desconectar")

            else:            #caso 2.2
                client_socket.sendto(command_or_message.encode(), (database.server_address))
                print(f'Bye bye, {username}')
                onChat = False

        elif username:                              # caso 3
            txt_path_file = convert_str_to_txt.convert_str_to_txt(username, command_or_message) #crio um txt contendo
                                                    #o conteúdo de "command_or_message", que no caso, é uma "message"
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
            print("---------------------Seu comando é inválido!---------------------\n"
                  "=================================================================\n"
                  "->Caso ainda não se logou, escreva 'hi, meu nome eh' + seu_nome\n"
                  "->Caso já tenha logado e queira chatear, apenas envie mensagens.\n"
                  "->Caso já esteja logado e queira sair do chat, apenas escreva 'bye'\n"
                  "==================================================================")

client()
