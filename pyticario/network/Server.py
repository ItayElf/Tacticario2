import threading
from pyticario import Player
from pyticario import Unit
from pyticario import Room
from pyticario.network.common import send, receive

lock = threading.Lock()


class Server:

    def commands(self):
        commands = {
            "DIS": self.disconnect,
            "SUT": self.send_unit,
            "SAU": self.send_all_units,
            "CRP": self.create_player,
            "DLP": self.delete_player,
            "RSP": self.reset_player,
            "AUT": self.add_unit,
            "RUT": self.remove_unit,
            "ATK": self.attack,
            "IDR": self.is_dead_or_ran,
            "IPV": self.is_password_valid,
            "CRR": self.create_room,
            "APR": self.add_player_to_room,
            "RPR": self.remove_player_from_room,
            'SAR': self.send_active_rooms,
            "SRP": self.send_active_rooms_points,
            "SPO": self.send_points_of_room,
            'SSP': self.send_second_player,
            'SAB': self.send_attribute
        }

        return commands

    @staticmethod
    def disconnect(params):
        send(params[0], "DON")
        params[0].close()

    @staticmethod
    def send_unit(params):
        lock.acquire()
        if params[2].isdigit():
            try:
                unt = Player.Player(params[1], False).get_unit(int(params[2])).as_tuple()
            except IndexError:
                Server.send_error(params[0], 3)
                lock.release()
                return
        else:
            try:
                unt = Unit.Unit.unit_by_name(params[2]).as_tuple()
            except FileNotFoundError:
                Server.send_error(params[0], 2)
                lock.release()
                return
        msg = "GUT~" + '~'.join([str(val) for val in unt])
        send(params[0], msg)
        lock.release()

    @staticmethod
    def send_all_units(params):
        lock.acquire()
        try:
            a = Player.Player(params[1], False)
            all_units = a.get_unit(-1)
            lock.release()
        except FileNotFoundError:
            Server.send_error(params[0], 5)
            lock.release()
            return

        send(params[0], f"GAU~{len(all_units)}")
        for unt in all_units:
            msg = "GUT~" + '~'.join([str(val) for val in unt.as_tuple()])
            send(params[0], msg)

    @staticmethod
    def create_player(params):
        lock.acquire()
        try:
            Player.Player(params[1], True, params[2])
            send(params[0], "DON")
            lock.release()
        except FileExistsError:
            lock.release()
            Server.send_error(params[0], 4)

    @staticmethod
    def delete_player(params):
        lock.acquire()
        try:
            a = Player.Player(params[1], False)
            a.delete_player()
            send(params[0], 'DON')
            lock.release()
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 5)

    @staticmethod
    def reset_player(params):
        lock.acquire()
        try:
            a = Player.Player(params[1], False)
            a.reset_db()
            send(params[0], 'DON')
            lock.release()
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 5)

    @staticmethod
    def add_unit(params):
        lock.acquire()
        try:
            a = Player.Player(params[1], False)
            a.add_unit_by_name(params[2])
            send(params[0], 'DON')
            lock.release()
        except FileNotFoundError as e:
            lock.release()
            if "unit" in str(e):
                Server.send_error(params[0], 2)
            else:
                Server.send_error(params[0], 5)

    @staticmethod
    def remove_unit(params):
        lock.acquire()
        try:
            a = Player.Player(params[1], False)
            a.remove_unit_form_db(int(params[2]))
            send(params[0], 'DON')
            lock.release()
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 2)

    @staticmethod
    def attack(params):
        lock.acquire()
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
            lock.release()
        except IndexError:
            lock.release()
            Server.send_error(params[0], 3)

    @staticmethod
    def is_dead_or_ran(params):
        lock.acquire()
        try:
            a = Player.Player(params[1], False)
            res = a.is_dead_or_ran(params[2])
            send(params[0], f"GTF~{int(res)}")
            lock.release()
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 5)
        except IndexError:
            lock.release()
            Server.send_error(params[0], 3)

    @staticmethod
    def is_password_valid(params):
        lock.acquire()
        send(params[0], f"GTF~{int(Player.Player.check_password(params[1], params[2]))}")
        lock.release()

    @staticmethod
    def create_room(params):
        lock.acquire()
        try:
            Room.Room(params[1], True, params[2])
            lock.release()
            send(params[0], "DON")
        except FileExistsError:
            lock.release()
            Server.send_error(params[0], 6)

    @staticmethod
    def add_player_to_room(params):
        lock.acquire()
        try:
            a = Room.Room(params[1], False)
            a.add_player(params[2])
            lock.release()
            send(params[0], 'DON')
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 7)
        except IndexError:
            lock.release()
            Server.send_error(params[0], 8)

    @staticmethod
    def remove_player_from_room(params):
        lock.acquire()
        try:
            a = Room.Room(params[1], False)
            a.remove_player(params[2])
            lock.release()
            send(params[0], 'DON')
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 7)
        except ValueError:
            lock.release()
            Server.send_error(params[0], 5)

    @staticmethod
    def send_active_rooms(params):
        lock.acquire()
        a = Room.Room.get_active_rooms()
        lock.release()
        send(params[0], f"GAR~{len(a)}")
        for i in range(len(a)):
            send(params[0], f"{a[i]}")

    @staticmethod
    def send_active_rooms_points(params):
        lock.acquire()
        a = Room.Room.get_active_rooms_points()
        lock.release()
        send(params[0], f"GAR~{len(a)}")
        for i in range(len(a)):
            send(params[0], f"{a[i]}")

    @staticmethod
    def send_points_of_room(params):
        lock.acquire()
        try:
            points = Room.Room.get_points_of(params[1])
            lock.release()
            send(params[0], f"GIT~{str(points[0])}")
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 7)

    @staticmethod
    def send_second_player(params):
        lock.acquire()
        try:
            pnames = Room.Room.get_pnames(params[1])
            lock.release()
            pnames = pnames[0].split(',')
            if len(pnames) != 2:
                Server.send_second_player(params)
            pnames = [val for val in pnames if val != params[2]]
            send(params[0], f"GST~{pnames[0]}")
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 7)

    @staticmethod
    def send_attribute(params):
        lock.acquire()
        try:
            atr = Unit.Unit.get_attribute(params[1])
            lock.release()
            send(params[0], f"GAB~{atr[0]}~{atr[1]}")
        except FileNotFoundError:
            lock.release()
            Server.send_error(params[0], 9)

    @staticmethod
    def send_error(client, error_number):
        send(client, f"ERR~{error_number}")
