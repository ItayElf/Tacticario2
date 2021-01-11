from pyticario.network.common import receive, send
from pyticario import protocol as ptr
import threading as thr
import pygame
import socket
import ctypes
import sys
import os

IP = sys.argv[1]
ROOM = sys.argv[2]
PLAYER_NUMBER = int(sys.argv[3])
u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080
client = socket.socket()


def convert(font):
    return int(font * ratio)


def map_send(soc, msg):
    try:
        send(soc, msg)
        res = receive(client)
        return ptr.map_parse(res, client)
    except ConnectionRefusedError:
        print("Server seems to be shut down.")
    except ConnectionAbortedError:
        print("Server seems to be shut down.")


def setup():
    global client
    # socket
    try:
        client = socket.socket()
        client.settimeout(3)
        client.connect((IP, ptr.PORT))
        client.settimeout(None)
        send(client, f"MAP~{ROOM}")
    except socket.gaierror:
        print("IP is not valid.")
        return setup()
    except TimeoutError:
        print("Server seems to be shut down.")
        return setup()
    except socket.timeout:
        print("Server seems to be shut down.")
        return setup()
    except ConnectionRefusedError:
        print("Server seems to be shut down.")
        return setup()

    # window
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (u.GetSystemMetrics(0) // 2, 0)
    pygame.init()
    return pygame.display.set_mode((u.GetSystemMetrics(0) // 2, u.GetSystemMetrics(1)), pygame.NOFRAME)


if __name__ == '__main__':

    screen = setup()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
