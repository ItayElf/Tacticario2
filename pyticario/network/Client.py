from pyticario import Unit
from pyticario.network.common import send, receive, parse


class Client:
    def commands(self):
        commands = {
            "DON": self.done,
            "GUT": self.get_unit,
            "GAU": self.get_all_units
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
        return all_units



    @staticmethod
    def send_error(client, error_number):
        send(client, f"ERR~{error_number}")
