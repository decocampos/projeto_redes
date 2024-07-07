# Projeto de Redes de Computadores

## Descrição do Projeto

Este projeto implementa um sistema de comunicação em rede usando sockets UDP em Python. O sistema permite que múltiplos clientes se conectem a um servidor, enviem mensagens e recebam mensagens de outros usuários conectados. O projeto é dividido em dois principais componentes: o servidor e o cliente.

## Estrutura dos Arquivos

- `server.py`: Código do servidor que gerencia a comunicação entre os clientes.
- `client.py`: Código do cliente que permite aos usuários enviar e receber mensagens.

## Requisitos

- Python 3.x
- Bibliotecas externas: `socket`, `threading`, `random`, `zlib`, `struct`, `queue`, `time`
- Biblioteca própria: `suport` (contendo `database`, `get_time_data`, `convert_str_to_txt`, `default_output`)

## Instruções de Uso

### Configuração do Servidor

1. Certifique-se de que o servidor está configurado corretamente no arquivo `database.py` dentro da biblioteca `suport`.
   - Exemplo:
     ```python
     server_address_tuple = ('localhost', 12345)
     buffer_size = 1024
     header_size = 16
     ```
2. Execute o servidor:
   ```bash
   python server.py
   ```

### Configuração do Cliente

1. Certifique-se de que o cliente está configurado corretamente no arquivo `database.py` dentro da biblioteca `suport`.
   - Exemplo:
     ```python
     server_adress_1 = 12345
     packages_size = 1024
     ```
2. Execute o cliente:
   ```bash
   python client.py
   ```

## Funcionalidades

### Servidor

- **Receber Mensagens**: O servidor recebe mensagens dos clientes, verifica a integridade das mensagens usando CRC32, e coloca-as em uma fila de mensagens.
- **Broadcast**: O servidor envia mensagens para todos os clientes conectados.
- **Gerenciamento de Clientes**: Adiciona novos clientes à lista de clientes conectados e remove clientes desconectados.

### Cliente

- **Conexão com o Servidor**: Conecta-se ao servidor usando sockets UDP.
- **Envio de Mensagens**: Permite que o usuário envie mensagens que são divididas em pacotes, cada um contendo um cabeçalho com informações sobre o pacote.
- **Recepção de Mensagens**: Recebe e exibe mensagens de outros clientes conectados ao servidor.

## Exemplo de Uso

### Cliente

1. **Login**:
   ```
   hi, meu nome eh [seu_nome]
   ```

2. **Enviar Mensagem**:
   ```
   [sua_mensagem]
   ```

3. **Logout**:
   ```
   bye
   ```

## Considerações Finais

Este projeto demonstra a utilização de sockets UDP para comunicação em rede, tratamento de pacotes, e verificação de integridade de dados. Ele pode ser expandido para incluir mais funcionalidades, como criptografia de mensagens e autenticação de usuários.

## Estudantes
André Campos 	avcl@cin.ufpe.br

Felipe Santos	fss9@cin.ufpe.br

Arthur Santos	asms@cin.ufpe.br

Matheus Pessoa	mop2@cin.ufpe.br

Lucas Figueiredo	lfa5@cin.ufpe.br

Lucas Morais	llxm@cin.ufpe.br

