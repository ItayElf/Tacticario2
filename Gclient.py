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


def start(r):
    def goto_login():
        return login(r)

    def goto_register():
        pass

    reset(r)
    font_size = 60
    f = Frame()
    f.place(relx=0.5, rely=0.5, anchor='center')
    l = Label(f, text="Welcome To Tacticario")
    l.config(font=font(font_size))
    l.grid(row=1, column=1, columnspan=2)
    button = Button(f, text="Log In", command=goto_login)
    button.config(font=font(font_size))
    button.grid(row=2, column=1)
    button = Button(f, text="Register", command=goto_register)
    button.config(font=font(font_size))
    button.grid(row=2, column=2)


def login(r):
    def go_back():
        return start(r)

    def on_press():
        global client
        try:
            client = socket.socket()
            client.settimeout(3)
            client.connect((ip.get(), ptr.PORT))
            client.settimeout(None)
        except socket.gaierror:
            print("IP is not valid.")
            return login(r)
        except TimeoutError:
            print("Server seems to be shut down.")
            return login(r)
        except ConnectionRefusedError:
            print("Server seems to be shut down.")
            return login(r)

        ans = client_send(client, f"IPV~{name.get()}~{password.get()}")
        if not ans:
            print("Incorrect username or password.")
            client_send(client, "DIS")
            return login(r)
        print("Logged in.")

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
    l = Label(f, text="PASSWORD: ")
    l.config(font=font(font_size))
    l.grid(row=2)

    ip = Entry(f)
    ip.config(font=font(font_size))
    ip.grid(row=0, column=1, columnspan=2)
    name = Entry(f)
    name.config(font=font(font_size))
    name.grid(row=1, column=1, columnspan=2)
    password = Entry(f)
    password.config(font=font(font_size))
    password.grid(row=2, column=1, columnspan=2)

    button = Button(f, text="Log In", command=on_press)
    button.config(font=font(font_size))
    button.grid(row=3, column=1)
    button = Button(r, text="BACK", command=go_back)
    button.config(font=font(font_size // 2))
    button.grid(row=2, column=1)


if __name__ == '__main__':
    root = setup()
    start(root)
    root.mainloop()
