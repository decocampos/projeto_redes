import random

def convert_str_to_txt(user, str, backEnd=False):
    file_random_number = random.randint(1, 25000)
    file_append = f'{user}{file_random_number}' # nome do arquivo == usuário + número aleatório entre 1 e 25000

    if backEnd: #se foi gerado pelo backEnd
        path_file = f"./entrega_1/arquivos_txt/server/{file_append}.txt"
    else: #se foi gerado pelo usuário
        path_file = f"./entrega_1/arquivos_txt/client/{file_append}.txt"


    file = open(path_file, "a") # "a" == append / "w" == write / "r" == read
    file.write(str)

    #retornando o caminho do arquivo
    return path_file