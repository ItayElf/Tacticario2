from pyticario.network.Server import Server
from pyticario.network.Client import Client
from pyticario.network.Mapsock import Mapsock
from pyticario.network.common import parse
import sqlite3

PORT = 1664


def server_parse(msg, client):
    cmd, params = parse(msg)
    params.insert(0, client)
    try:
        return Server().commands()[cmd](params)
    except KeyError:
        if cmd == 'ERR':
            return f"ERR{params[1]}"
        elif cmd == 'DON':
            return 'DON0'
        Server.send_error(client, 1)
    except IndexError:
        Server.send_error(client, 1)
    except sqlite3.OperationalError:
        print("Database is blocked.")
        return server_parse(msg, client)


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


def map_parse(msg, client):
    cmd, params = parse(msg)
    params.insert(0, client)
    try:
        return Mapsock().commands()[cmd](params)
    except KeyError:
        if cmd == 'ERR':
            return f"ERR{params[1]}"
        elif cmd == 'DON':
            return 0
    # except IndexError:
    #     return f"ERR{params[1]}"


if __name__ == '__main__':
    pass
