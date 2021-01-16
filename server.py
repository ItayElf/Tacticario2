import socket
import threading as thr

from pyticario import protocol as ptr
from pyticario.network.common import receive, send

server = socket.socket()
IP = "0.0.0.0"
server.bind((IP, ptr.PORT))
server.listen()
lock = thr.Lock()

clients = {}
rooms = {}


def handle_map(client, room, addr):
    try:
        lock.acquire()
        try:
            rooms[room].append(addr)
        except KeyError:
            rooms[room] = [addr]
        lock.release()
        while True:
            lock.acquire()
            if len(rooms[room]) == 2:
                lock.release()
                send(client, 'DON')
                break
            lock.release()

        while True:
            res = receive(client)
            lock.acquire()
            print(res)
            for ad in rooms[room]:
                if ad is not addr:
                    send(clients[ad], res)
            lock.release()
    except OSError as e:
        rooms[room].remove(addr)
        del clients[addr]
        for ad in rooms[room]:
            if ad is not addr:
                send(clients[ad], f"FRT")
        raise OSError(e)


def handle_client(client, addr):
    while True:
        try:
            res = receive(client)
            print(res)
            if res.split('~')[0] == 'MAP':
                return handle_map(client, res.split('~')[1], addr)

            ptr.server_parse(res, client)
            x = ptr.server_parse(receive(client), client)
            if x:
                print(x)
        except OSError as e:
            print(e)
            quit()


while True:
    client, addr = server.accept()
    clients[addr] = client
    x = thr.Thread(target=handle_client, args=(client, addr))
    x.start()
