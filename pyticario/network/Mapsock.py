from pyticario.network.common import send, receive, parse
import re


class Mapsock:
    def commands(self):
        commands = {
            "GMP": self.get_map
        }

        return commands

    @staticmethod
    def get_map(params):
        a = re.findall(r"\[.+?]", params[1])
        return [re.findall(r'\w+', chunk) for chunk in a]
