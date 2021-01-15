import re
import ctypes
import os
import socket
import subprocess
import tkinter as tk
from functools import partial
from tkinter import *
from tkinter import messagebox

from pyticario import protocol as ptr
from pyticario.network.common import receive, send

IP = ''
NAME = ''
ROOM = ''
PLAYER_NUMBER = ''
PID = -55
u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080
client = socket.socket()


class ScrollableFrame(tk.Frame):
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


def client_send(soc, msg):
    try:
        send(soc, msg)
        res = receive(client)
        print(f"MSG: {msg}, RES: {res}")
        return ptr.client_parse(res, client)
    except ConnectionRefusedError:
        messagebox.showerror("Connection Error", "Server seems to be shut down.")
        print("Server seems to be shut down.")
    except ConnectionAbortedError:
        messagebox.showerror("Connection Error", "Server seems to be shut down.")
        print("Server seems to be shut down.")


def convert(font):
    return int(font * ratio)


def font(size):
    return "Calibri Light", convert(size)


def setup():
    root = tk.Tk()
    root.title("Tacticario2")
    root.geometry(f"{convert(1920)}x{convert(1080)}")
    root.protocol("WM_DELETE_WINDOW", partial(on_closing, root))

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
        try:
            item.grid_forget()
        except AttributeError:
            pass


def on_closing(r, pid=-55):
    global client
    try:
        res = messagebox.askquestion("Quit", "Do you want to quit?")
        if res == "yes":
            if pid > 0:
                os.kill(pid, 9)
            client_send(client, "DIS")
            r.destroy()

    except OSError:
        r.destroy()


def start(r):
    def goto_login():
        return login(r)

    def goto_register():
        return register(r)

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
        global client, NAME, IP
        try:
            client = socket.socket()
            client.settimeout(3)
            client.connect((ip.get(), ptr.PORT))
            client.settimeout(None)
        except socket.gaierror:
            messagebox.showerror("Invalid IP", "IP is not valid.")
            print("IP is not valid.")
        except TimeoutError:
            messagebox.showerror("Connection Error", "Server seems to be shut down.")
            print("Server seems to be shut down.")
        except socket.timeout:
            messagebox.showerror("Connection Error", "Server seems to be shut down.")
            print("Server seems to be shut down.")
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Server seems to be shut down.")
            print("Server seems to be shut down.")

        IP = ip.get()
        ans = client_send(client, f"IPV~{name.get()}~{password.get()}")
        if not ans:
            messagebox.showerror("Incorrect Username or Password", "Incorrect Username or Password.")
            print("Incorrect username or password.")
            client_send(client, "DIS")
            return login(r)
        NAME = name.get()
        return home(r)

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


def register(r):
    def go_back():
        return start(r)

    def on_press():
        global client, NAME
        try:
            client = socket.socket()
            client.settimeout(3)
            client.connect((ip.get(), ptr.PORT))
            client.settimeout(None)
        except socket.gaierror:
            messagebox.showerror("Invalid IP", "IP is not valid.")
            print("IP is not valid.")
        except TimeoutError:
            messagebox.showerror("Connection Error", "Server seems to be shut down.")
            print("Server seems to be shut down.")
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Server seems to be shut down.")
            print("Server seems to be shut down.")

        ans = client_send(client, f"CRP~{name.get()}~{password.get()}")
        if ans == 'ERR4':
            print("Name has already been taken.")
            client_send(client, "DIS")
            return register(r)
        NAME = name.get()
        return home(r)

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

    button = Button(f, text="Register", command=on_press)
    button.config(font=font(font_size))
    button.grid(row=3, column=1)
    button = Button(r, text="BACK", command=go_back)
    button.config(font=font(font_size // 2))
    button.grid(row=2, column=1)


def home(r):
    def host():
        return host_room(r)

    def join():
        return join_room(r)

    reset(r)
    font_size = 60
    f = Frame()
    f.place(relx=0.5, rely=0.5, anchor='center')
    l = Label(f, text=f"Welcome, {NAME}!")
    l.config(font=font(int(font_size * 1.5)))
    l.grid(row=0, column=0, columnspan=3)
    l = Label(f, text=f"What would you like to do?")
    l.config(font=font(int(font_size // 1.5)))
    l.grid(row=1, column=0, columnspan=3)

    button = Button(f, text="Host Room", command=host)
    button.config(font=font(int(font_size // 1.5)))
    button.grid(row=2, column=0)
    button = Button(f, text="Join Room", command=join)
    button.config(font=font(int(font_size // 1.5)))
    button.grid(row=2, column=2)
    button = Button(r, text="QUIT", command=partial(on_closing, root))
    button.config(font=font(font_size // 2))
    button.grid(row=2, column=1)


def host_room(r):
    def go_back():
        return home(r)

    def on_press():
        global ROOM, PLAYER_NUMBER
        try:
            if re.findall("^[A-Za-z0-9_-]+$", name.get())[0] != name.get():
                print("Invalid name.")
                return host_room(r)
        except IndexError:
            messagebox.showerror("Invalid Name", "Room name can only contain letters, numbers, underscores and dashes.")
            print("Invalid name.")
            return host_room(r)
        if not (points.get().isdigit() or points.get() == '-1'):
            messagebox.showerror("Invalid Points", "Points can only be a positive integer or '-1' for infinite points.")
            print("Invalid points")
            return host_room(r)
        ans = client_send(client, f"CRR~{name.get()}~{points.get()}~{NAME}")
        if ans == 'ERR6':
            messagebox.showerror("Invalid Name", "The name you've entered is being used by another room.")
            print("This name is being used by another room")
            return host_room(r)
        ROOM = name.get()
        PLAYER_NUMBER = '1'
        room_recruit(r)

    reset(r)
    font_size = 60
    f = Frame()
    f.place(relx=0.5, rely=0.5, anchor='center')
    l = Label(f, text="Host Room")
    l.config(font=font(font_size))
    l.grid(row=0, columnspan=3)
    l = Label(f, text="Room Name: ")
    l.config(font=font(font_size))
    l.grid(row=1)
    l = Label(f, text="Points: ")
    l.config(font=font(font_size))
    l.grid(row=2)
    name = Entry(f)
    name.config(font=font(font_size))
    name.grid(row=1, column=1, columnspan=2)
    points = Entry(f)
    points.config(font=font(font_size))
    points.grid(row=2, column=1, columnspan=2)
    button = Button(f, text="Host Room", command=on_press)
    button.config(font=font(font_size))
    button.grid(row=3, column=1)
    button = Button(r, text="BACK", command=go_back)
    button.config(font=font(font_size // 2))
    button.grid(row=2, column=1)


def join_room(r):
    def go_back():
        return home(r)

    def set_text(txt, _b):
        name.delete(0, END)
        name.insert(0, txt)

    def join():
        global ROOM, PLAYER_NUMBER
        ans = client_send(client, f"APR~{name.get()}~{NAME}")
        if ans == "ERR8":
            messagebox.showerror("Room is Full", "The room you tried to join is full.")
            print("Room is full")
        elif ans == "ERR7":
            messagebox.showerror("Room not Found", "The room you tried to join was not found. Try again.")
            print("room not found")
        else:
            ROOM = name.get()
            PLAYER_NUMBER = '2'
            room_recruit(r)

    reset(r)
    font_size = 60
    f = Frame()
    f.place(relx=0.5, rely=0.5, anchor='center')
    l = Label(f, text="Join Room")
    l.config(font=font(font_size))
    l.grid(row=0, columnspan=3)
    l = Label(f, text="Room Name: ")
    l.config(font=font(font_size))
    l.grid(row=1)
    name = Entry(f)
    name.config(font=font(font_size))
    name.grid(row=1, column=1)
    button = Button(f, text="Join", command=join)
    button.config(font=font(int(font_size // 1.5)))
    button.grid(row=1, column=3)
    button = Button(r, text="BACK", command=go_back)
    button.config(font=font(font_size // 2))
    button.grid(row=2, column=1)
    scroll_frame = ScrollableFrame(f)
    scroll_frame.scrollable_frame.config(bg="white", width=convert(800), height=convert(500))
    scroll_frame.canvas.config(bg="white", width=convert(800), height=convert(500))
    scroll_frame.grid(row=2, column=1)
    active_rooms = client_send(client, "SAR")
    active_points = client_send(client, 'SRP')
    for i, text in enumerate(active_rooms):
        point = f" - {active_points[i]} points." if int(active_points[i]) > 0 else " - No limit."
        l = Label(scroll_frame.scrollable_frame, text=(text + point), anchor='w')
        l.config(font=font(int(font_size // 1.5)), bg="white")
        l.bind("<Button-1>", partial(set_text, text))
        l.grid(row=i, sticky="ew")


def room_recruit(r):
    def go_back():
        res = messagebox.askquestion("Quit", "Do you want to quit?")
        if res == "yes":
            ans = client_send(client, f"RPR~{ROOM}~{NAME}")
            return home(r)

    def popup_unit(index):
        unitvar = all_units[index]
        fr = Toplevel()
        fr.title(unitvar.name)
        new_size = 15
        l = Label(fr, text=unitvar.name)
        l.config(font=font(new_size * 2))
        l.grid(row=0, column=0, columnspan=2)
        args = [var.replace('_', ' ').title() for var in
                ['category', 'name', 'description', 'class', 'subclass', 'cost', 'men', 'weight', 'hitpoints',
                 'armor', 'shield', 'morale', 'speed', 'melee_attack', 'defence', 'damage', 'ap', 'charge',
                 'ammunition', 'range', 'ranged_attack', 'ranged_damage', 'ranged_ap', 'attributes']]
        unitup = list(unitvar.as_tuple())[1:]
        unitup[1] = unitup[1].replace('.', '.\n')
        if unitup[1].endswith("\n"):
            unitup[1] = unitup[1][:-1]
        unitup[-1] = unitup[-1].replace(',', ', ')
        args.remove(args[0])
        for i, (cat, val) in enumerate(zip(args, unitup)):
            if (((type(val) == int or type(val) == float) and val > 0) or type(val) == str) and cat != 'Weight':
                l = Label(fr, text=f"{cat}:")
                l.config(font=font(new_size))
                l.grid(row=i + 1, column=0, sticky='ew')
                l = Label(fr, text=f"{val}")
                l.config(font=font(new_size))
                l.grid(row=i + 1, column=1, sticky='ew')
        fr.resizable(False, False)

    def remove_unit(unitnum):
        ans = client_send(client, f"RUT~{NAME}~{unitnum}")
        if ans and "ERR" in ans:
            print(ans)
        return room_recruit(r)

    def reset_army():
        client_send(client, f"RSP~{NAME}")
        return room_recruit(r)

    def recruit_click():
        return recruit(r)

    reset(r)
    font_size = 60
    f = Frame()
    f.place(relx=0.5, rely=0.5, anchor='center')
    l = Label(f, text=f"{ROOM}")
    l.config(font=font(int(font_size * 1.5)))
    l.grid(row=0, column=0, columnspan=3)
    all_units = client_send(client, f"SAU~{NAME}")
    scroll = ScrollableFrame(f)
    scroll.canvas.config(width=convert(850), height=convert(700))
    scroll.grid(row=2, column=0, columnspan=3, sticky='ew')
    l = Label(scroll.scrollable_frame, text="Remove")
    l.config(font=font(int(font_size // 1.5)))
    l.grid(row=0, column=0, sticky="ew")
    l = Label(scroll.scrollable_frame, text="ID")
    l.config(font=font(int(font_size // 1.5)))
    l.grid(row=0, column=1, sticky="ew")
    l = Label(scroll.scrollable_frame, text="Name")
    l.config(font=font(int(font_size // 1.5)))
    l.grid(row=0, column=2, sticky="ew")
    l = Label(scroll.scrollable_frame, text="Cost")
    l.config(font=font(int(font_size // 1.5)))
    l.grid(row=0, column=3, sticky="ew")
    l = Label(scroll.scrollable_frame, text="-" * 50)
    l.config(font=font(int(font_size // 1.5)))
    l.grid(row=1, column=0, columnspan=4)
    for i, unt in enumerate(all_units):
        button = Button(scroll.scrollable_frame, text="Remove", command=partial(remove_unit, i + 1))
        button.config(font=font(int(font_size // 2)))
        button.grid(row=i + 2, column=0, sticky='ew')
        l = Label(scroll.scrollable_frame, text=i + 1)
        l.config(font=font(int(font_size // 1.5)))
        l.grid(row=i + 2, column=1)
        b = Button(scroll.scrollable_frame, text=unt.name, command=partial(popup_unit, i))
        b.config(font=font(int(font_size // 1.5)))
        b.grid(row=i + 2, column=2)
        l = Label(scroll.scrollable_frame, text=unt.cost)
        l.config(font=font(int(font_size // 1.5)))
        l.grid(row=i + 2, column=3)
    points = client_send(client, f"SPO~{ROOM}")
    l = Label(f, text=f"Total Cost: {sum([val.cost for val in all_units])} {f'/ {points}' if points > 0 else ''}")
    l.config(font=font(int(font_size // 1.5)))
    l.grid(row=3, column=0, columnspan=3)
    button = Button(f, text="Recruit", command=recruit_click)
    button.config(font=font(int(font_size // 1.5)))
    button.grid(row=4, column=0)
    button = Button(f, text="Reset", command=reset_army)
    button.config(font=font(int(font_size // 1.5)))
    button.grid(row=4, column=1)
    button = Button(f, text="Continue", command=partial(game, r))
    button.config(font=font(int(font_size // 1.5)))
    button.grid(row=4, column=2)
    button = Button(r, text="Leave", command=go_back)
    button.config(font=font(font_size // 2))
    button.grid(row=2, column=1)


def recruit(r):
    def go_back():
        return room_recruit(r)

    def unit_page(classs):
        def ret():
            return recruit(r)

        def popup_unit(unitvar):
            def rec_win(unt):
                def rec(unt, num):
                    for _ in range(num.get()):
                        ans = client_send(client, f"AUT~{NAME}~{unt.name}")
                        if ans and "ERR" in ans:
                            print(ans)
                    top.destroy()

                top = Toplevel(fr)
                top.title("Recruit")
                x = Label(top, text="Number of units:")
                x.config(font=font(25))
                x.grid(columnspan=7, sticky="ew")
                number = IntVar(top)
                number.set(1)
                option = OptionMenu(top, number, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                option.config(font=font(25))
                option.grid(row=1, column=1, columnspan=5, sticky="ew")
                f = partial(rec, unt)
                b = Button(top, text='Recruit', command=partial(f, number))
                b.config(font=font(25))
                b.grid(row=2, column=2, columnspan=3, sticky="ew")

            fr = Toplevel(r)
            fr.title(unitvar.name)
            new_size = 15

            l = Label(fr, text=unitvar.name)
            l.config(font=font(new_size * 2))
            l.grid(row=1, column=0, columnspan=4)
            args = [var.replace('_', ' ').title() for var in
                    ['category', 'name', 'description', 'class', 'subclass', 'cost', 'men', 'weight', 'hitpoints',
                     'armor', 'shield', 'morale', 'speed', 'melee_attack', 'defence', 'damage', 'ap', 'charge',
                     'ammunition', 'range', 'ranged_attack', 'ranged_damage', 'ranged_ap', 'attributes']]
            unitup = list(unitvar.as_tuple())[1:]
            unitup[1] = unitup[1].replace('.', '.\n')
            if unitup[1].endswith("\n"):
                unitup[1] = unitup[1][:-1]
            unitup[-1] = unitup[-1].replace(',', ', ')
            args.remove(args[0])
            for i, (cat, val) in enumerate(zip(args, unitup)):
                if (((type(val) == int or type(val) == float) and val > 0) or type(val) == str) and cat != 'Weight':
                    l = Label(fr, text=f"{cat}:")
                    l.config(font=font(new_size))
                    l.grid(row=i + 2, column=0, columnspan=2, sticky='ew')
                    l = Label(fr, text=f"{val}")
                    l.config(font=font(new_size))
                    l.grid(row=i + 2, column=2, columnspan=2, sticky='ew')
            b = Button(fr, text='Recruit', command=partial(rec_win, unitvar))
            b.config(font=font(new_size))
            b.grid(row=1, column=3, sticky='e')
            fr.resizable(False, False)

        reset(r)
        units = [unt for unt in all_units if unt.category == classs]
        f2 = Frame()
        f2.place(relx=0.5, rely=0.5, anchor='center')
        l = Label(f2, text=classs)
        l.config(font=font(int(font_size * 1.5)))
        l.grid(row=0, column=0, columnspan=2)
        for i, unt in enumerate(units):
            row = i // 2 + 1
            col = i % 2
            b = Button(f2, text=unt.name, command=partial(popup_unit, unt))
            b.config(font=font(int(font_size // 2)))
            b.grid(row=row, column=col, sticky="ew")
        button = Button(r, text="BACK", command=ret)
        button.config(font=font(font_size // 2))
        button.grid(row=2, column=1)

    reset(r)
    font_size = 60
    f = Frame()
    f.place(relx=0.5, rely=0.5, anchor='center')
    l = Label(f, text="Recruit")
    l.config(font=font(int(font_size * 1.5)))
    l.grid(row=0, column=0, columnspan=2)
    all_units = client_send(client, "SAU~units")
    if "ERR" in all_units:
        print("ERROR")
        return room_recruit(r)
    order = {'Light': 1, 'Medium': 2, 'Heavy': 3, 'England': 4, "India": 5, "Japan": 6, "Mongolia": 7, "Norway": 8,
             "Russia": 9}
    categories = sorted(list(set([unt.category for unt in all_units])), key=lambda x: order[x.split()[0]])
    regulars = [clas for clas in categories if len(clas.split()) > 1]
    countries = [clas for clas in categories if len(clas.split()) == 1]
    for i, clas in enumerate(regulars):
        b = Button(f, text=clas, command=partial(unit_page, clas))
        b.config(font=font(int(font_size // 2)))
        b.grid(row=i + 1, column=0, sticky="ew")
    for i, clas in enumerate(countries):
        b = Button(f, text=clas, command=partial(unit_page, clas))
        b.config(font=font(int(font_size // 2)))
        b.grid(row=i + 1, column=1, sticky="ew")
    button = Button(r, text="BACK", command=go_back)
    button.config(font=font(font_size // 2))
    button.grid(row=2, column=1)


def game(r):
    def attack():
        def attacker_unit():
            all_units = client_send(client, f"SAU~{NAME}")
            l = Label(fr, text="Attack With:")
            l.config(font=font(font_size))
            l.grid(row=0, column=0, columnspan=2)
            scroll = ScrollableFrame(fr)
            scroll.canvas.config(width=convert(350), height=convert(350))
            scroll.grid(row=1, column=0, columnspan=2, sticky='ew')
            l = Label(scroll.scrollable_frame, text="ID")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=0, sticky="ew")
            l = Label(scroll.scrollable_frame, text="Name")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=1, sticky="ew")
            l = Label(scroll.scrollable_frame, text="Soldiers")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=2, sticky="ew")
            l = Label(scroll.scrollable_frame, text="Morale")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=3, sticky="ew")
            l = Label(scroll.scrollable_frame, text="-" * 50)
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=1, column=0, columnspan=4)
            for i, unt in enumerate(all_units):
                if unt.men == 0 or unt.morale == 0:
                    continue
                l = Label(scroll.scrollable_frame, text=i + 1)
                l.config(font=font(int(font_size // 1.5)))
                l.grid(row=i + 2, column=0)
                b = Button(scroll.scrollable_frame, text=unt.name, command=partial(opponent_unit, i + 1))
                b.config(font=font(int(font_size // 1.5)))
                b.grid(row=i + 2, column=1)
                l = Label(scroll.scrollable_frame, text=unt.men)
                l.config(font=font(int(font_size // 1.5)))
                l.grid(row=i + 2, column=2)
                l = Label(scroll.scrollable_frame, text=unt.morale)
                l.config(font=font(int(font_size // 1.5)))
                l.grid(row=i + 2, column=3)

        def opponent_unit(unit1_id):
            reset(fr)
            opp_units = client_send(client, f"SAU~{opponent}")
            l = Label(fr, text="Attack Target:")
            l.config(font=font(font_size))
            l.grid(row=0, column=0, columnspan=2)
            scroll = ScrollableFrame(fr)
            scroll.canvas.config(width=convert(350), height=convert(350))
            scroll.grid(row=1, column=0, columnspan=2, sticky='ew')
            l = Label(scroll.scrollable_frame, text="ID")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=0, sticky="ew")
            l = Label(scroll.scrollable_frame, text="Name")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=1, sticky="ew")
            l = Label(scroll.scrollable_frame, text="Soldiers")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=2, sticky="ew")
            l = Label(scroll.scrollable_frame, text="Morale")
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=0, column=3, sticky="ew")
            l = Label(scroll.scrollable_frame, text="-" * 50)
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=1, column=0, columnspan=4)
            for i, unt in enumerate(opp_units):
                if unt.men == 0 or unt.morale == 0:
                    continue
                l = Label(scroll.scrollable_frame, text=i + 1)
                l.config(font=font(int(font_size // 1.5)))
                l.grid(row=i + 2, column=0)
                b = Button(scroll.scrollable_frame, text=unt.name, command=partial(params, unit1_id, i + 1))
                b.config(font=font(int(font_size // 1.5)))
                b.grid(row=i + 2, column=1)
                l = Label(scroll.scrollable_frame, text=unt.men)
                l.config(font=font(int(font_size // 1.5)))
                l.grid(row=i + 2, column=2)
                l = Label(scroll.scrollable_frame, text='?' if unt.morale > 15 else '!')
                l.config(font=font(int(font_size // 1.5)))
                l.grid(row=i + 2, column=3)
            button = Button(fr, text="BACK", command=attacker_unit)
            button.config(font=font(font_size // 2))
            button.grid(row=2, column=1)

        def params(unit1_id, unit2_id):
            def ranged_click():
                if ranged_var.get():
                    flank.config(state=DISABLED)
                    flank_var.set(0)
                    charge.config(state=DISABLED)
                    charge_var.set(0)
                    front.config(state=NORMAL)
                else:
                    flank.config(state=NORMAL)
                    charge.config(state=NORMAL)
                    front.config(state=DISABLED)
                    front_var.set(0)

            def flank_charge_click():
                if flank_var.get() or charge_var.get():
                    ranged.config(state=DISABLED)
                    ranged_var.set(0)
                    front.config(state=DISABLED)
                    front_var.set(0)
                else:
                    ranged.config(state=NORMAL)

            def atk_cmd():
                damage, casualties = client_send(client,
                                                 f"ATK~{NAME}~{unit1_id}~{opponent}~{unit2_id}~{ranged_var.get()}~{flank_var.get()}~"
                                                 f"{charge_var.get()}~{front_var.get()}~{adv_var.get() - disadv_var.get()}")
                atk_unt = client_send(client, f"SUT~{NAME}~{unit1_id}")
                def_unt = client_send(client, f"SUT~{opponent}~{unit2_id}")
                messagebox.showinfo("Attack Result", f"Your {atk_unt.name} dealt {int(damage)} damage"
                                                     f"to your opponent's {def_unt.name}, resulting in {casualties} casualties.")
                fr.destroy()

            reset(fr)
            l = Label(fr, text="Modifiers:")
            l.config(font=font(font_size))
            l.grid(row=0, column=0, columnspan=2)
            ranged_var = IntVar()
            ranged = Checkbutton(fr, text="Ranged", variable=ranged_var, command=ranged_click)
            ranged.config(font=font(font_size))
            ranged.grid(row=1, column=0)
            front_var = IntVar()
            front = Checkbutton(fr, text="Front", variable=front_var)
            front.config(font=font(font_size), state=DISABLED)
            front.grid(row=2, column=0)
            flank_var = IntVar()
            flank = Checkbutton(fr, text="Flank", variable=flank_var, command=flank_charge_click)
            flank.config(font=font(font_size))
            flank.grid(row=1, column=1)
            charge_var = IntVar()
            charge = Checkbutton(fr, text="Charge", variable=charge_var, command=flank_charge_click)
            charge.config(font=font(font_size))
            charge.grid(row=2, column=1)
            adv_var = IntVar()
            adv = Checkbutton(fr, text="Advantage", variable=adv_var)
            adv.config(font=font(font_size))
            adv.grid(row=3, column=0)
            disadv_var = IntVar()
            disadv = Checkbutton(fr, text="Disadvantage", variable=disadv_var)
            disadv.config(font=font(font_size))
            disadv.grid(row=3, column=1)
            atk = Button(fr, text="Attack", command=atk_cmd)
            atk.config(font=font(font_size))
            atk.grid(row=4, column=0, columnspan=2)

        fr = Toplevel(r)
        fr.title("Attack")
        font_size = 25
        attacker_unit()

    def refresh(font_size):
        reset(r)
        all_units = client_send(client, f"SAU~{NAME}")
        f = Frame()
        f.place(relx=0.5, rely=0.5, anchor='center')
        l = Label(f, text="Game")
        l.config(font=font(int(font_size * 1.5)))
        l.grid(row=0, column=0, columnspan=3)
        scroll = ScrollableFrame(f)
        scroll.canvas.config(width=convert(850), height=convert(700))
        scroll.grid(row=1, column=0, columnspan=3, sticky='ew')
        l = Label(scroll.scrollable_frame, text="ID")
        l.config(font=font(int(font_size // 1.5)))
        l.grid(row=0, column=0, sticky="ew")
        l = Label(scroll.scrollable_frame, text="Name")
        l.config(font=font(int(font_size // 1.5)))
        l.grid(row=0, column=1, sticky="ew")
        l = Label(scroll.scrollable_frame, text="Soldiers")
        l.config(font=font(int(font_size // 1.5)))
        l.grid(row=0, column=2, sticky="ew")
        l = Label(scroll.scrollable_frame, text="Morale")
        l.config(font=font(int(font_size // 1.5)))
        l.grid(row=0, column=3, sticky="ew")
        l = Label(scroll.scrollable_frame, text="-" * 50)
        l.config(font=font(int(font_size // 1.5)))
        l.grid(row=1, column=0, columnspan=4)
        for i, unt in enumerate(all_units):
            if unt.men == 0 or unt.morale == 0:
                continue
            l = Label(scroll.scrollable_frame, text=i + 1)
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=i + 2, column=0)
            b = Button(scroll.scrollable_frame, text=unt.name, command=partial(popup_unit, unt))
            b.config(font=font(int(font_size // 1.5)))
            b.grid(row=i + 2, column=1)
            l = Label(scroll.scrollable_frame, text=unt.men)
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=i + 2, column=2)
            l = Label(scroll.scrollable_frame, text=unt.morale)
            l.config(font=font(int(font_size // 1.5)))
            l.grid(row=i + 2, column=3)
        ref = Button(f, text="Refresh", command=partial(refresh, font_size))
        ref.config(font=font(font_size))
        ref.grid(row=2, column=0)
        atk = Button(f, text="Attack", command=attack)
        atk.config(font=font(font_size))
        atk.grid(row=2, column=2)

    def popup_unit(unitvar):
        fr = Toplevel(r)
        fr.title(unitvar.name)
        new_size = 15

        l = Label(fr, text=unitvar.name)
        l.config(font=font(new_size * 2))
        l.grid(row=1, column=0, columnspan=4)
        args = [var.replace('_', ' ').title() for var in
                ['category', 'name', 'description', 'class', 'subclass', 'cost', 'men', 'weight', 'hitpoints',
                 'armor', 'shield', 'morale', 'speed', 'melee_attack', 'defence', 'damage', 'ap', 'charge',
                 'ammunition', 'range', 'ranged_attack', 'ranged_damage', 'ranged_ap', 'attributes']]
        unitup = list(unitvar.as_tuple())[1:]
        unitup[1] = unitup[1].replace('.', '.\n')
        if unitup[1].endswith("\n"):
            unitup[1] = unitup[1][:-1]
        unitup[-1] = unitup[-1].replace(',', ', ')
        args.remove(args[0])
        for i, (cat, val) in enumerate(zip(args, unitup)):
            if (((type(val) == int or type(val) == float) and val > 0) or type(val) == str) and cat != 'Weight':
                l = Label(fr, text=f"{cat}:")
                l.config(font=font(new_size))
                l.grid(row=i + 2, column=0, columnspan=2, sticky='ew')
                l = Label(fr, text=f"{val}")
                l.config(font=font(new_size))
                l.grid(row=i + 2, column=2, columnspan=2, sticky='ew')
        fr.resizable(False, False)

    font_s = 45
    refresh(font_s)
    r.geometry(f"{convert(1920) // 2}x{convert(1080)}")

    p = subprocess.Popen(["python", "Mclient.py", IP, ROOM, PLAYER_NUMBER])
    r.protocol("WM_DELETE_WINDOW", partial(on_closing, root, p.pid))
    opponent = client_send(client, f"SSP~{ROOM}~{NAME}")


if __name__ == '__main__':
    root = setup()
    start(root)
    root.mainloop()
