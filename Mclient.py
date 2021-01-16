import ctypes
import os
import socket
import sys
import threading as thr
import time
import tkinter
import tkinter.messagebox

import pygame

from pyticario import protocol as ptr
from pyticario.graphics.Button import Button
from pyticario.graphics.Gunit import Unit
from pyticario.graphics.Map import Map
from pyticario.network.common import receive, send

try:
    IP = sys.argv[1]
    ROOM = sys.argv[2]
    PLAYER_NUMBER = int(sys.argv[3])
except IndexError:
    IP, ROOM, PLAYER_NUMBER = '127.0.0.1', 'aa', 1
u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080
client = socket.socket()
lock = thr.Lock()


def convert(font):
    return int(font * ratio)


def error_msg(title, body):
    w = tkinter.Tk()
    # w.wm_withdraw()
    w.geometry("1x1+" + str(w.winfo_screenwidth() // 2) + "+" + str(w.winfo_screenheight() // 2))
    tkinter.messagebox.showerror(title=title, message=body, parent=w)


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


def handle_msgs(c):
    while True:
        res = ptr.map_parse(receive(c), c)
        change_units(True, res, 0)


def get_tile_from_pixels(x_pixels, y_pixels):
    return x_pixels // m.tile_size, (y_pixels - (u.GetSystemMetrics(1) // 2 - m.size // 2)) // m.tile_size


# ------------------------ UNITS -----------------------------------

def change_units(server, unt_arr, index):
    def send_to_server():
        send(client, f"GUA~{len(m.units)}")
        for unt in m.units:
            send(client, f"GSU~{str(unt)}")

    lock.acquire()
    if server:
        m.units = unt_arr
    else:
        if unt_arr is None:
            try:
                m.units.remove(m.units[index])
            except ValueError:
                return
        else:
            try:
                m.units[index] = unt_arr[0]
            except IndexError:
                m.units.append(unt_arr[0])
        send_to_server()

    lock.release()


def add_unit(unt):
    thr.Thread(target=change_units, args=(False, [unt], len(m.units) + 1)).start()


def update_unt(unt, index):
    thr.Thread(target=change_units, args=(False, [unt], index)).start()


def delete_unt(index):
    thr.Thread(target=change_units, args=(False, None, index)).start()


# ------------------------ MODES -----------------------------------

def delete_click():
    global delete_var, add_var, number_var
    delete_var = not delete_var
    add_var = False
    number_var = False
    add_button.clicked = False
    number_button.clicked = False


def add_click():
    global delete_var, add_var, number_var
    delete_var = False
    add_var = not add_var
    number_var = False
    delete_button.clicked = False
    number_button.clicked = False


def number_click():
    global delete_var, add_var, number_var
    delete_var = False
    add_var = False
    number_var = not number_var
    delete_button.clicked = False
    add_button.clicked = False


# ------------------------------------------------------------------

def draw():
    m.draw_map()
    delete_button.draw()
    add_button.draw()
    number_button.draw()
    pygame.display.update()


if __name__ == '__main__':
    screen = setup()
    m = create_map(screen, [0.25, 0.25, 0.25])
    thr.Thread(target=handle_msgs, args=(client,), daemon=True).start()

    delete_var = False
    delete_button = Button(screen, (convert(160), convert(30)), "Delete", convert(32), delete_click)

    add_var = False
    add_button = Button(screen, (convert(800), convert(30)), 'Add', convert(32), add_click)

    number_var = False
    number_button = Button(screen, (convert(480), convert(30)), 'Change Number', convert(32), number_click)

    running = True
    while running:
        if m.units is None:
            running = False
            error_msg("You Are Alone", "The other player has disconnected or forfeited.\n You are free to click on forfeit to go back to the main screen.")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = get_tile_from_pixels(*pygame.mouse.get_pos())
                if pygame.mouse.get_pressed(3)[0]:
                    m.selected_unit = m.get_unit_at(x, y)
                    delete_button.handle_button()
                    add_button.handle_button()
                    number_button.handle_button()

                    if m.selected_unit is not None:
                        offset = m.units[m.selected_unit].x - x, m.units[m.selected_unit].y - y

                elif pygame.mouse.get_pressed(3)[1]:
                    if m.tiles_in_row >= x >= 0 and m.tiles_in_row >= y >= 0:
                        if add_var:
                            add_unit(Unit(x, y, m.number_of_units(PLAYER_NUMBER) + 1, PLAYER_NUMBER, 0, 0))
                        elif delete_var:
                            try:
                                delete_unt(m.get_unit_at(x, y))
                            except TypeError:
                                pass
                        elif number_var:
                            try:
                                unt = m.units[m.get_unit_at(x, y)]
                                text = ''
                                while not text.endswith('\n'):
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.KEYDOWN:
                                            if ev.key == pygame.K_RETURN:
                                                text += '\n'
                                            elif ev.key == pygame.K_BACKSPACE:
                                                text = text[:-1]
                                            elif ev.unicode.isdigit():
                                                text += ev.unicode
                                update_unt(Unit(unt.x, unt.y, int(text), unt.player, unt.rotation, unt.active),
                                           m.get_unit_at(x, y))
                            except TypeError:
                                pass
                        else:
                            try:
                                unt = m.units[m.get_unit_at(x, y)]
                                update_unt(
                                    Unit(unt.x, unt.y, unt.number, unt.player, unt.rotation, int(not unt.active)),
                                    m.get_unit_at(x, y))
                            except TypeError:
                                pass

                elif pygame.mouse.get_pressed(3)[2]:
                    try:
                        unt = m.units[m.get_unit_at(x, y)]
                        update_unt(Unit(unt.x, unt.y, unt.number, unt.player, unt.rotation + 1, unt.active),
                                   m.get_unit_at(x, y))
                    except TypeError:
                        pass

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed(3)[0]:
                    x, y = get_tile_from_pixels(*pygame.mouse.get_pos())
                    if m.selected_unit is not None:
                        m.units[m.selected_unit].x = x + offset[0]
                        m.units[m.selected_unit].y = y + offset[1]
                elif m.selected_unit is not None:
                    unt = m.units[m.selected_unit]
                    update_unt(Unit(unt.x, unt.y, unt.number, unt.player, unt.rotation, unt.active),
                               m.selected_unit)
                    m.selected_unit = None

        draw()
