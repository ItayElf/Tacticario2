from pyticario import Player
from pyticario import Unit
from pyticario.network.common import send


class Server:

    def commands(self):
        commands = {
            "SUT": self.send_unit,
            "CRP": self.create_player,
            "DLP": self.delete_player
        }

        return commands

    @staticmethod
    def send_unit(params):
        if params[2].isdigit():
            try:
                unt = Player.Player(params[1], False).get_unit(int(params[2])).as_tuple()
            except IndexError:
                Server.send_error(params[0], 3)
                return
        else:
            try:
                unt = Unit.Unit.unit_by_name(params[2]).as_tuple()
            except FileNotFoundError:
                Server.send_error(params[0], 2)
                return
        msg = "GUT~" + '~'.join([str(val) for val in unt])
        send(params[0], msg)

    @staticmethod
    def create_player(params):
        try:
            Player.Player(params[1])
            send(params[0], "DON")
        except FileExistsError:
            Server.send_error(params[0], 4)

    @staticmethod
    def delete_player(params):
        try:
            a = Player.Player(params[0], False)
            a.delete_player()
            send(params[0], 'DON')
        except FileNotFoundError:
            Server.send_error(params[0], 5)

    @staticmethod
    def reset_player(params):
        try:
            a = Player.Player(params[0], False)
            a.reset_db()
            send(params[0], 'DON')
        except FileNotFoundError:
            Server.send_error(params[0], 5)

    @staticmethod
    def send_error(client, error_number):
        send(client, f"ERR~{error_number}")
