def default_output_message():

    toConect = ['Para conectar-se, digite: ', 'hi, meu nome eh <nome_do_usuario>']
    toQuit = ['Para sair da sala, digite:', 'bye']

    message = (f'==========================================================================\n'
               '{:^1} {:>46}\n' .format(*toConect) +
               '==========================================================================\n'
               '{:^1} {:>16}'.format(*toQuit) +
               '\n==========================================================================')

    return message

print(default_output_message())