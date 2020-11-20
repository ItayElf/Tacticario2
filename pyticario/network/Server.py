from pyticario import Player
from pyticario import Unit
from pyticario import Room
from pyticario.network.common import send, receive

using_db = False


class Server:

    def commands(self):
        commands = {
            "DIS": self.disconnect,
            "SUT": self.send_unit,
            "SAU": self.send_all_units,
            "CRP": self.create_player,
            "DLP": self.delete_player,
            "RPL": self.reset_player,
            "AUT": self.add_unit,
            "RUT": self.remove_unit,
            "ATK": self.attack,
            "IDR": self.is_dead_or_ran,
            "IPV": self.is_password_valid,
            "CRR": self.create_room,
            "APR": self.add_player_to_room,
            "RPR": self.remove_player_from_room,
            'SAR': self.send_active_rooms,
            "SRP": self.send_active_rooms_points
        }

        return commands

    @staticmethod
    def disconnect(params):
        send(params[0], "DON")
        params[0].close()

    @staticmethod
    def send_unit(params):
        global using_db
        while using_db:
            pass
        using_db = True
        if params[2].isdigit():
            try:
                unt = Player.Player(params[1], False).get_unit(int(params[2])).as_tuple()
            except IndexError:
                Server.send_error(params[0], 3)
                using_db = False
                return
        else:
            try:
                unt = Unit.Unit.unit_by_name(params[2]).as_tuple()
            except FileNotFoundError:
                Server.send_error(params[0], 2)
                using_db = False
                return
        msg = "GUT~" + '~'.join([str(val) for val in unt])
        send(params[0], msg)
        using_db = False

    @staticmethod
    def send_all_units(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Player.Player(params[1], False)
            all_units = a.get_unit(-1)
            using_db = False
        except FileNotFoundError:
            Server.send_error(params[0], 5)
            using_db = False
            return

        send(params[0], f"GAU~{len(all_units)}")
        for unt in all_units:
            msg = "GUT~" + '~'.join([str(val) for val in unt.as_tuple()])
            send(params[0], msg)

    @staticmethod
    def create_player(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            Player.Player(params[1], True, params[2])
            send(params[0], "DON")
            using_db = False
        except FileExistsError:
            using_db = False
            Server.send_error(params[0], 4)

    @staticmethod
    def delete_player(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Player.Player(params[1], False)
            a.delete_player()
            send(params[0], 'DON')
            using_db = False
        except FileNotFoundError:
            using_db = False
            Server.send_error(params[0], 5)

    @staticmethod
    def reset_player(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Player.Player(params[1], False)
            a.reset_db()
            send(params[0], 'DON')
            using_db = False
        except FileNotFoundError:
            using_db = False
            Server.send_error(params[0], 5)

    @staticmethod
    def add_unit(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Player.Player(params[1], False)
            a.add_unit_by_name(params[2])
            send(params[0], 'DON')
            using_db = False
        except FileNotFoundError as e:
            using_db = False
            if "unit" in str(e):
                Server.send_error(params[0], 2)
            else:
                Server.send_error(params[0], 5)

    @staticmethod
    def remove_unit(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Player.Player(params[1], False)
            a.remove_unit_form_db(params[2])
            send(params[0], 'DON')
            using_db = False
        except FileNotFoundError:
            using_db = False
            Server.send_error(params[0], 2)

    @staticmethod
    def attack(params):
        global using_db
        while using_db:
            pass
        using_db = True
        p1 = Player.Player(params[1], False)
        p2 = Player.Player(params[3], False)
        ranged = bool(int(params[5]))
        flank = bool(int(params[6]))
        charge = bool(int(params[7]))
        front = bool(int(params[8]))
        advantage = float(params[9])
        try:
            d, c = p1.attack(int(params[2]), p2, int(params[4]), ranged, flank, charge, front, advantage)
            send(params[0], f"GDC~{d}~{c}")
            using_db = False
        except IndexError:
            using_db = False
            Server.send_error(params[0], 3)

    @staticmethod
    def is_dead_or_ran(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Player.Player(params[1], False)
            res = a.is_dead_or_ran(params[2])
            send(params[0], f"GTF~{int(res)}")
            using_db = False
        except FileNotFoundError:
            using_db = False
            Server.send_error(params[0], 5)
        except IndexError:
            using_db = False
            Server.send_error(params[0], 3)

    @staticmethod
    def is_password_valid(params):
        global using_db
        while using_db:
            pass
        using_db = True
        send(params[0], f"GTF~{int(Player.Player.check_password(params[1], params[2]))}")
        using_db = False

    @staticmethod
    def create_room(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            Room.Room(params[1], True, params[2])
            using_db = False
            send(params[0], "DON")
        except FileExistsError:
            using_db = False
            Server.send_error(params[0], 6)

    @staticmethod
    def add_player_to_room(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Room.Room(params[1], False)
            a.add_player()
            using_db = False
            send(params[0], 'DON')
        except FileNotFoundError:
            using_db = False
            Server.send_error(params[0], 7)
        except IndexError:
            using_db = False
            Server.send_error(params[0], 8)

    @staticmethod
    def remove_player_from_room(params):
        global using_db
        while using_db:
            pass
        using_db = True
        try:
            a = Room.Room(params[1], False)
            a.remove_player()
            using_db = False
            send(params[0], 'DON')
        except FileNotFoundError:
            using_db = False
            Server.send_error(params[0], 7)

    @staticmethod
    def send_active_rooms(params):
        global using_db
        while using_db:
            pass
        using_db = True
        a = Room.Room.get_active_rooms()
        using_db = False
        send(params[0], f"GAR~{len(a)}")
        for i in range(len(a)):
            send(params[0], f"{a[i]}")

    @staticmethod
    def send_active_rooms_points(params):
        global using_db
        while using_db:
            pass
        using_db = True
        a = Room.Room.get_active_rooms_points()
        using_db = False
        send(params[0], f"GAR~{len(a)}")
        for i in range(len(a)):
            send(params[0], f"{a[i]}")

    @staticmethod
    def send_error(client, error_number):
        send(client, f"ERR~{error_number}")
