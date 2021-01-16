import re

from pyticario.graphics.Gunit import Unit
from pyticario.network.common import receive, parse


class Mapsock:
    def commands(self):
        commands = {
            "GMP": self.get_map,
            'GUA': self.get_units_array
        }

        return commands

    @staticmethod
    def get_map(params):
        a = re.findall(r"\[.+?]", params[1])
        return [re.findall(r'\w+', chunk) for chunk in a]

    @staticmethod
    def get_units_array(params):
        arr = []
        for i in range(int(params[1])):
            cmd, p = parse(receive(params[0]))
            arr.append(Unit(*p[0].split(',')))
        return arr

    @staticmethod
    def forfeit(params):
        return "ERR~10"
