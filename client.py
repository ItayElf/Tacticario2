import socket
from pyticario.network.common import receive, send
from pyticario import protocol as ptr

IP = socket.gethostbyname(socket.gethostname())

client = socket.socket()
client.connect((IP, ptr.PORT))

while True:
    name = input(">>> ")
    send(client, f"SUT~units~{name}")
    res = receive(client)
    x = ptr.client_parse(res, client)
    if x:
        print(x)
