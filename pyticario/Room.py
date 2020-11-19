import sqlite3
import settings


class Room:
    def __init__(self, name, new=True):
        self.name = name
        if new:
            conn = sqlite3.connect(settings.DB)
            c = conn.cursor()
            c.execute(f"SELECT * FROM rooms WHERE name='{self.name}'")
            if c.fetchone():
                raise FileExistsError(f"The name {self.name} has already been taken.")
            c.execute(f"INSERT INTO rooms VALUES ('{self.name}', 1)")
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

    def remove_player(self):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT players FROM rooms WHERE name='{self.name}'")
        x = c.fetchone()
        if not x:
            conn.close()
            raise FileNotFoundError(f"Room {self.name} was not found.")
        elif x == 2:
            c.execute(f"UPDATE rooms SET players=1 WHERE name='{self.name}'")
        else:
            c.execute(f"DELETE FROM rooms WHERE name='{self.name}'")
