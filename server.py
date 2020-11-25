import socket
import threading as thr
from pyticario.network.common import receive
from pyticario import protocol as ptr

server = socket.socket()
IP = "0.0.0.0"
server.bind((IP, ptr.PORT))
server.listen()


def handle_client(client, _addr):
    while True:
        try:
            res = receive(client)
            print(res)
            ptr.server_parse(res, client)
            x = ptr.server_parse(receive(client), client)
            if x:
                print(x)
        except OSError as e:
            print(e)
            quit()


while True:
    client, addr = server.accept()
    x = thr.Thread(target=handle_client, args=(client, addr))
    x.start()
