import random
import os

def convert_str_to_txt(user, str, backEnd=False):
    file_random_number = random.randint(1, 25000)
    file_append = f'{user}{file_random_number}'

    if backEnd:
        path_file = f"./arquivos_txt/server/{file_append}.txt"
    else:
        path_file = f"./arquivos_txt/client/{file_append}.txt"

    os.makedirs(os.path.dirname(path_file), exist_ok=True)

    with open(path_file, "a") as file:
        file.write(str)

    return path_file
