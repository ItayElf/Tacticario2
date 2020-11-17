import socket
from pyticario.network.common import receive
from pyticario import protocol as ptr

server = socket.socket()
IP = socket.gethostbyname(socket.gethostname())
server.bind((IP, ptr.PORT))
server.listen()
client, addr = server.accept()
while True:
    res = receive(client)
    ptr.server_parse(res, client)
    x = ptr.server_parse(receive(client), client)
    if x:
        print(x)


