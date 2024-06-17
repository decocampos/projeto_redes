def default_output_message(action):

    toConect = ['Para conectar-se, digite: ', 'hi, meu nome eh <nome_do_usuario>']
    toQuit = ['Para sair da sala, digite:', 'bye']

    if action == "DEFAULT":

        message = (f'==========================================================================\n'
                   '{:^1} {:>46}\n' .format(*toConect) +
                   '==========================================================================\n'
                   '{:^1} {:>16}'.format(*toQuit) +
                   '\n==========================================================================')
        return message

    elif action == "ERRO":
        message = ("---------------------Seu comando é inválido!---------------------\n"
                         "=================================================================\n"
                         "->Caso ainda não se logou, escreva 'hi, meu nome eh' + seu_nome\n"
                         "->Caso já tenha logado e queira chatear, apenas envie mensagens.\n"
                         "->Caso já esteja logado e queira sair do chat, apenas escreva 'bye'\n"
                         "==================================================================")
        return message
