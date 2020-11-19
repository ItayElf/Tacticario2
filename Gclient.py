from pyticario import protocol as ptr
from pyticario.network.common import receive, send
import tkinter as tk
from tkinter import *
import ctypes
import socket

u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080
client = socket.socket()

def client_send(soc, msg):
    send(soc, msg)
    res = receive(client)
    return ptr.client_parse(res, client)

def convert(font):
    return int(font * ratio)


def font(size):
    return "Calibri Light", convert(size)


def setup():
    root = tk.Tk()
    root.title = "Tacticario2"
    root.geometry(f"{convert(1920)}x{convert(1080)}")

    return root


def reset(r):
    def all_children(window):
        _list = window.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        return _list

    widget_list = all_children(r)
    for item in widget_list:
        item.grid_forget()


def login(r):
    def on_press():
        try:
            client.settimeout(3)
            client.connect((ip.get(), ptr.PORT))
            client.settimeout(None)
        except socket.gaierror:
            print("IP is not valid.")
        except TimeoutError:
            print("Server seems to be shut down.")
        except ConnectionRefusedError:
            print("Server seems to be shut down.")

        ans = client_send(client, f"CRP~{name.get()}")
        if ans == "ERR4":
            print("Name has already been taken.")
        print(ans)



    reset(r)
    font_size = 60
    f = Frame()
    f.place(relx=0.5, rely=0.5, anchor='center')
    l = Label(f, text="IP: ")
    l.config(font=font(font_size))
    l.grid(row=0)
    l = Label(f, text="NAME: ")
    l.config(font=font(font_size))
    l.grid(row=1)

    ip = tk.Entry(f)
    ip.config(font=font(font_size))
    ip.grid(row=0, column=1, columnspan=2)
    name = tk.Entry(f)
    name.config(font=font(font_size))
    name.grid(row=1, column=1, columnspan=2)

    button = Button(f, text="Log In", command=on_press)
    button.config(font=font(font_size))
    button.grid(row=2, column=1)


if __name__ == '__main__':
    root = setup()
    login(root)
    root.mainloop()
