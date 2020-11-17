from pyticario import Unit
from pyticario.network.common import send


class Client:
    def commands(self):
        commands = {
            "DON": self.done,
            "GUT": self.get_unit
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
    def send_error(client, error_number):
        send(client, f"ERR~{error_number}")
