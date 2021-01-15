from pyticario import Unit
from pyticario.network.common import send, receive, parse


class Client:
    def commands(self):
        commands = {
            "DON": self.done,
            "GUT": self.get_unit,
            "GAU": self.get_all_units,
            "GDC": self.get_damage_and_casualties,
            "GTF": self.get_true_or_false,
            "GAR": self.get_active_rooms,
            "GIT": self.get_integer,
            'GST': self.get_string
        }

        return commands

    @staticmethod
    def done(params):
        send(params[0], "DON")

    @staticmethod
    def get_unit(params):
        Client.done(params)
        return Unit.Unit(params[1:])

    @staticmethod
    def get_all_units(params):
        all_units = []
        for _ in range(int(params[1])):
            cmd, p = parse(receive(params[0]))
            while not cmd:
                cmd, p = parse(receive(params[0]))
            all_units.append(Unit.Unit(p))
        Client.done(params)
        return all_units

    @staticmethod
    def get_damage_and_casualties(params):
        Client.done(params)
        return [float(params[1]), int(params[2])]

    @staticmethod
    def get_true_or_false(params):
        return bool(int(params[1]))

    @staticmethod
    def get_active_rooms(params):
        active_rooms = []
        for i in range(int(params[1])):
            active_rooms.append(receive(params[0]))
        Client.done(params)
        return active_rooms

    @staticmethod
    def get_integer(params):
        return int(params[1])

    @staticmethod
    def get_string(params):
        return params[1]

    @staticmethod
    def send_error(client, error_number):
        send(client, f"ERR~{error_number}")
