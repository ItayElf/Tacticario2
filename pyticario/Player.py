import sqlite3

import settings
from pyticario import Unit

unit_args = ['category', 'name', 'description', 'class', 'subclass', 'cost', 'men', 'weight', 'hitpoints',
             'armor', 'shield', 'morale', 'speed', 'melee_attack', 'defence', 'damage', 'ap', 'charge',
             'ammunition', 'range', 'ranged_attack', 'ranged_damage', 'ranged_ap', 'attributes']

unit_args_types = ['text', 'text', 'text', 'text', 'text', 'integer', 'integer', 'real', 'integer',
                   'integer', 'real', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer', 'integer',
                   'integer', 'integer', 'integer', 'integer', 'integer', 'text']


class Player:
    def __init__(self, name, new=True, password=None):
        self.name = name
        if new:
            if not password:
                raise TypeError("Password must be supplied to new players.")
            self.units = 0
            conn = sqlite3.connect(settings.DB)
            try:
                text = f"CREATE TABLE {name} ("
                for col, typ in zip(unit_args, unit_args_types):
                    text += f"{col} {typ},"
                text = text[:-1] + ')'
                conn.cursor().execute(text)
                conn.commit()
            except sqlite3.OperationalError:
                conn.close()
                raise FileExistsError(f"The name {name} has already been taken.")

            conn.cursor().execute(f"INSERT INTO players VALUES ('{name}', '{password}')")
            conn.commit()
            conn.close()
        else:
            self.units = len(self.get_unit(-1))

    def delete_player(self):
        try:
            conn = sqlite3.connect(settings.DB)
            conn.cursor().execute(f"DROP TABLE {self.name}")
            conn.cursor().execute(f"DELETE FROM players WHERE name = '{self.name}'")
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            try:
                conn.close()
            except NameError:
                pass
            raise FileNotFoundError(f"User {self.name} was not found.")

    def add_unit_by_name(self, unit_name):
        def get_unit_from_db(conn):
            c = conn.cursor()
            c.execute(f"SELECT * FROM units WHERE name='{unit_name}'")
            tup = c.fetchone()
            if not tup:
                conn.close()
                raise FileNotFoundError(f"The unit {unit_name} was not found on DB.")
            return tup

        def insert_to_player_db(conn, vals):
            try:
                text = f"INSERT INTO {self.name} VALUES ("
                for value in vals:
                    if type(value) == str:
                        value = f'"{value}"'
                    text += f"{value},"
                text = text[:-1] + ')'
                conn.cursor().execute(text)
                conn.commit()
            except sqlite3.OperationalError:
                raise FileNotFoundError(f"Player {self.name} was not found.")

        self.units += 1
        conn = sqlite3.connect(settings.DB)
        data = get_unit_from_db(conn)
        insert_to_player_db(conn, data)
        conn.close()

    def add_unit_by_tuple(self, tup):
        self.units += 1
        conn = sqlite3.connect(settings.DB)
        text = f"INSERT INTO {self.name} VALUES ("
        for value in tup:
            if type(value) == str:
                value = f'"{value}"'
            text += f"{value},"
        text = text[:-1] + ')'
        conn.cursor().execute(text)
        conn.commit()
        conn.close()

    def remove_unit_form_db(self, unit_id):
        conn = sqlite3.connect(settings.DB)
        try:
            for i in range(unit_id + 1, self.units):
                self.update_unit(i - 1, self.get_unit(i).as_tuple())
            conn.cursor().execute(f"DELETE FROM {self.name} WHERE rowid = (SELECT MAX(rowid) FROM {self.name})")
            conn.commit()
            self.units -= 1
        except sqlite3.OperationalError:
            raise FileNotFoundError(f"Unit number {unit_id} was not found on {self.name}'s DB.")

    def reset_db(self):
        conn = sqlite3.connect(settings.DB)
        try:
            conn.cursor().execute(f"DROP TABLE {self.name}")
        except sqlite3.OperationalError:
            conn.close()
            raise FileNotFoundError(f"User {self.name} was not found.")
        text = f"CREATE TABLE {self.name} ("
        for col, typ in zip(unit_args, unit_args_types):
            text += f"{col} {typ},"
        text = text[:-1] + ')'
        conn.cursor().execute(text)
        conn.commit()
        conn.close()

    def get_unit(self, num):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        if num < 0:
            try:
                c.execute(f"SELECT * FROM {self.name}")
                lst = list(c.fetchall())
                conn.close()
                return [Unit.Unit(val) for val in lst]
            except sqlite3.OperationalError:
                raise FileNotFoundError(f"Player {self.name} was not found.")
        else:
            try:
                c.execute(f"SELECT * FROM {self.name} WHERE rowid = {num}")
                unt = Unit.Unit(c.fetchone())
                conn.close()
                return unt
            except sqlite3.OperationalError:
                raise IndexError(f"Unit id {num} was not found.")

    def update_unit(self, uname_id, tupl):
        conn = sqlite3.connect(settings.DB)
        text = f"UPDATE {self.name} SET "
        for col, value in zip(unit_args, tupl):
            if type(value) == str:
                value = f'"{value}"'
            text += f"{col} = {value},"
        text = text[:-1] + f' WHERE rowid = {uname_id}'
        conn.cursor().execute(text)
        conn.commit()
        conn.close()

    def attack(self, unit_id, other, other_id, ranged=False, flank=False, charge=False, front=True, advantage=0):
        unt = self.get_unit(unit_id)
        otr = other.get_unit(other_id)
        damage, casualties = unt.resolve(otr, ranged, flank, charge, front, advantage)
        self.update_unit(unit_id, unt.as_tuple())
        other.update_unit(other_id, otr.as_tuple())
        return damage, casualties

    def is_dead_or_ran(self, unit_id):

        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        try:
            c.execute(f"SELECT men, morale FROM {self.name} WHERE rowid = {unit_id}")
            men, morale = c.fetchone()
            conn.close()
            if men > 0 and morale > 0:
                return True
            return False
        except sqlite3.OperationalError:
            conn.close()
            raise FileNotFoundError
        except TypeError:
            conn.close()
            raise IndexError

    @staticmethod
    def check_password(name, password):
        conn = sqlite3.connect(settings.DB)
        c = conn.cursor()
        c.execute(f"SELECT * FROM players WHERE name='{name}' AND password='{password}'")
        if c.fetchall():
            return True
        return False


if __name__ == '__main__':
    a = Player("Itay", False)
