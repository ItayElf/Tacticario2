from pyticario.network.Server import Server
from pyticario.network.Client import Client
from pyticario.network.common import parse

PORT = 1664

errors = {
    '1': "Command was not found.",
    '2': "Unit was not found.",
    '3': "Index was not valid.",
    '4': "Name has already been taken.",
    '5': "User was not found."
}


def server_parse(msg, client):
    cmd, params = parse(msg)
    params.insert(0, client)
    try:
        return Server().commands()[cmd](params)
    except KeyError:
        if cmd == 'ERR':
            return params[1]
        elif cmd == 'DON':
            return 0
        Server.send_error(client, 1)
    except IndexError:
        Server.send_error(client, 1)


def client_parse(msg, client):
    cmd, params = parse(msg)
    params.insert(0, client)
    try:
        return Client().commands()[cmd](params)
    except KeyError:
        if cmd == 'ERR':
            return f"ERR{params[1]}"
        elif cmd == 'DON':
            return 0
        Client.send_error(client, 1)
    except IndexError:
        Client.send_error(client, 1)


if __name__ == '__main__':
    pass
