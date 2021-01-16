import sqlite3

import settings


class Room:
    def __init__(self, name, new=True, points=-1, pnames=''):
        self.name = name
        if new:
            conn = sqlite3.connect(settings.DB)
            c = conn.cursor()
            c.execute(f"SELECT * FROM rooms WHERE name='{self.name}'")
            if c.fetchone():
                conn.close()
                raise FileExistsError(f"The name {self.name} has already been taken.")
            c.execute(f"INSERT INTO rooms VALUES ('{self.name}', 1, {points},'{pnames}')")
            conn.commit()
            conn.close()

    def delete(self):
        try:
            conn = sqlite3.connect(settings.DB)
            conn.cursor().execute(f"DELETE FROM rooms WHERE name = '{self.name}'")
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            try:
                conn.close()
            except NameError:
                pass
            raise FileNotFoundError(f"Room {self.name} was not found.")

    def remove_player(self, pname):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT players, pnames FROM rooms WHERE name='{self.name}'")
        x = c.fetchone()
        if not x:
            conn.close()
            raise FileNotFoundError(f"Room {self.name} was not found.")
        elif x[0] == 2 and len(x[1].split(',')) == 2:
            pnames = x[1].split(',')
            try:
                pnames.remove(pname)
                pnames = ','.join(pnames)
            except ValueError:
                raise ValueError(f"Player {pname} was not found.")
            c.execute(f"UPDATE rooms SET players=1, pnames='{pnames}' WHERE name='{self.name}'")
            conn.commit()
            conn.close()
        else:
            c.execute(f"DELETE FROM rooms WHERE name='{self.name}'")
            conn.commit()
            conn.close()

    def add_player(self, pname):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT players, pnames FROM rooms WHERE name='{self.name}'")
        x = c.fetchone()
        if not x:
            conn.close()
            raise FileNotFoundError(f"Room {self.name} was not found.")
        elif x[0] == 1:
            pnames = ','.join([x[1], pname])
            c.execute(f"UPDATE rooms SET players=2, pnames='{pnames}' WHERE name='{self.name}'")
            conn.commit()
            conn.close()
        else:
            raise IndexError(f"Room {self.name} is full.")

    @staticmethod
    def get_points_of(name):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT points FROM rooms WHERE name='{name}'")
        x = c.fetchone()
        if not x:
            raise FileNotFoundError(f"Room {name} was not found.")
        conn.close()
        return x

    @staticmethod
    def get_active_rooms():
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT name FROM rooms WHERE players=1")
        x = c.fetchall()
        conn.close()
        return [val[0] for val in x]

    @staticmethod
    def get_active_rooms_points():
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT points FROM rooms WHERE players=1")
        x = c.fetchall()
        conn.close()
        return [val[0] for val in x]

    @staticmethod
    def get_pnames(name):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT pnames FROM rooms WHERE name='{name}'")
        x = c.fetchone()
        if not x:
            raise FileNotFoundError(f"Room {name} was not found.")
        conn.close()
        return x
