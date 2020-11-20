import socket
import threading as thr
from pyticario.network.common import receive
from pyticario import protocol as ptr

server = socket.socket()
IP = socket.gethostbyname(socket.gethostname())
server.bind((IP, ptr.PORT))
server.listen()


def handle_client(client, addr):
    while True:
        try:
            res = receive(client)
            print(res)
            ptr.server_parse(res, client)
            x = ptr.server_parse(receive(client), client)
            if x:
                print(x)
        except OSError:
            quit()


while True:
    client, addr = server.accept()
    x = thr.Thread(target=handle_client, args=(client, addr))
    x.start()
