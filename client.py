import socket

from pyticario import protocol as ptr
from pyticario.network.common import receive, send

IP = socket.gethostbyname(socket.gethostname())

client = socket.socket()
client.connect((IP, ptr.PORT))

while True:
    name = input(">>> ")
    send(client, name)
    if name == "DIS":
        break
    res = receive(client)
    x = ptr.client_parse(res, client)
    if x:
        print(x)
