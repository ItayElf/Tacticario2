import time

from pyticario.network.common import receive, send
from pyticario import protocol as ptr
from pyticario.graphics.Map import Map
import threading as thr
import pygame
import socket
import ctypes
import sys
import os
try:
    IP = sys.argv[1]
    ROOM = sys.argv[2]
    PLAYER_NUMBER = int(sys.argv[3])
except IndexError:
    IP, ROOM, PLAYER_NUMBER = '127.0.0.1', 'aa', 1
u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080
client = socket.socket()


def convert(font):
    return int(font * ratio)


def map_send(soc, msg):
    try:
        send(soc, msg)
        res = receive(client)
        print(f"(MAP) MSG: {msg}, RES: {res}")
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
    return pygame.display.set_mode((u.GetSystemMetrics(0) // 2, u.GetSystemMetrics(1)))


def create_map(screen, ratios):
    res = receive(client)
    print(res, PLAYER_NUMBER)
    if PLAYER_NUMBER == 1:
        a = Map(screen, [''] * (24 * 24))
        a.generate_tiles_from_ratio(*ratios)
        send(client, f"GMP~{str(a)}")
        time.sleep(0.5)
        return a
    else:
        tiles_arr = ptr.map_parse(receive(client), client)
        print(tiles_arr)
        return Map(screen, tiles_arr)


def draw():
    m.draw_tiles()

    pygame.display.update()


if __name__ == '__main__':
    screen = setup()
    m = create_map(screen, [0.25, 0.25, 0.25])

    print("drawn")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw()
