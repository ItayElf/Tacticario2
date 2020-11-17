from pyticario import Player
from pyticario import Unit
import socket

HEADER = 6
DELIMITER = '~'


class Server:

    def commands(self):
        commands = {
            "SUT": self.send_unit
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
    def send_error(client, error_number):
        send(client, f"ERR~{error_number}")


def send(soc, msg):
    msg_len = str(len(msg)).zfill(HEADER).encode()
    soc.send(msg_len + msg.encode())


def receive(soc):
    length = soc.recv(HEADER)
    if length:
        length = int(length)
        return soc.recv(length).decode()
    return ''


def parse(msg):
    cmd = msg.split(DELIMITER)[0]
    params = msg.split(DELIMITER)[1:]
    return cmd, params


def server_parse(msg, client):
    cmd, params = parse(msg)
    params.insert(0, client)
    try:
        Server().commands()[cmd](params)
    except KeyError:
        Server.send_error(client, 1)


if __name__ == '__main__':
    server_parse("SUT~units~Medium Spearman", 1)
    server_parse("SUT~Itay~1", 1)
