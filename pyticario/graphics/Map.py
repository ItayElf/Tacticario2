import ctypes
import json
import os
import random

import pygame as pg

u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080
config = os.path.join(os.path.dirname(__file__), "tilesconfig.json")

tiles = {
    "dirt": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'dirt.png'),
    "forest": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'forest.png'),
    "water": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'water.png'),
    "wall_left": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_left.png'),
    "wall_right": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_right.png'),
    "wall_up": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_up.png'),
    "wall_down": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_down.png')
}


def convert(font):
    return int(font * ratio)


def rotate(arr, rotation):
    mapper = {"dirt": "dirt", "forest": "forest", "water": "water", "wall_up": "wall_right", "wall_right": "wall_down",
              "wall_down": "wall_left", "wall_left": "wall_up"}
    if rotation == 0:
        return arr
    a = [list(val) for val in list(zip(*arr[::-1]))]
    c = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    for i, row in enumerate(a):
        for j, group in enumerate(row):
            for k, item in enumerate(group):
                c[i][j].append(mapper[item])
    return rotate(c, rotation - 1)


class Map:
    def __init__(self, screen, tiles_arr, units_arr=[]):
        self.screen = screen
        self.tiles = tiles_arr
        self.units = units_arr
        self.size = u.GetSystemMetrics(0) // 2
        self.tiles_in_row = int(len(self.tiles) ** 0.5)
        self.tile_size = self.size // self.tiles_in_row

        self._selected_unit = None

    def tile(self, x, y):
        # get tiles starting at (1,1)
        return self.tiles[25 * (y - 1) + (x - 1)]

    def generate_tiles_from_ratio(self, forest, water, walls):
        size = len(self.tiles)
        wall_types = ["wall_up", "wall_down", "wall_left", "wall_right"]
        forest_tiles = int(size * forest)
        water_tiles = int(size * water)
        wall_tiles = int(size * walls)
        dirt_tiles = size - forest_tiles - wall_tiles - water_tiles
        tiles = []
        for i in range(forest_tiles):
            tiles.append(["forest"])
        for i in range(water_tiles):
            tiles.append(["water"])
        for i in range(dirt_tiles + wall_tiles):
            tiles.append(["dirt"])
        for i in range(wall_tiles):
            rand_pos = random.randint(0, size - 1)
            rand_wall = wall_types[random.randint(0, len(wall_types) - 1)]
            tiles[rand_pos].append(rand_wall)
        self.tiles = list(map(lambda x: list(set(x)), random.sample(tiles, len(tiles))))

    def generate_tiles_from_config(self):
        def get_chunks():
            chunks = []
            keys = list(data.keys())
            while len(chunks) != 36:
                rand = random.randint(0, len(keys) - 1)
                chunks.append((data[keys[rand]], random.randint(0, 3)))
                keys.remove(keys[rand])
                if not keys:
                    keys = list(data.keys())
            random.shuffle(chunks)
            return chunks

        with open(config) as f:
            data = json.load(f)
        chunks = [rotate(val[0], val[1]) for val in get_chunks()]
        a = []
        for i in range(6):
            current = chunks[i * 6:i * 6 + 6]
            for k in range(4):
                for chunk in current:
                    a += chunk[k]
        self.tiles = a

    def draw_tiles(self):
        middle = u.GetSystemMetrics(1) // 2
        map_size = self.size
        top_y = middle - map_size // 2
        for i in range(self.tiles_in_row ** 2):
            x = (i % self.tiles_in_row) * convert(self.tile_size)
            y = (i // self.tiles_in_row) * convert(self.tile_size) + top_y
            imgs = []

            if "forest" in self.tiles[i]:
                imgs.append(tiles["forest"])
            elif "water" in self.tiles[i]:
                imgs.append(tiles["water"])
            else:
                imgs.append(tiles["dirt"])
            if "wall_right" in self.tiles[i]:
                imgs.append(tiles["wall_right"])
            if "wall_left" in self.tiles[i]:
                imgs.append(tiles["wall_left"])
            if "wall_down" in self.tiles[i]:
                imgs.append(tiles["wall_down"])
            if "wall_up" in self.tiles[i]:
                imgs.append(tiles["wall_up"])
            for img in imgs:
                pic = pg.transform.scale(pg.image.load(img), (self.tile_size, self.tile_size))
                self.screen.blit(pic, (x, y))

    def draw_map(self):
        self.draw_tiles()
        if self.units:
            for unt in self.units:
                unt.draw_unit(self.screen, convert(self.tile_size), self.size)

    def number_of_units(self, player_number):
        return len([val for val in self.units if val.player == player_number]) if self.units else 0

    def get_unit_at(self, x, y):
        if self.units:
            for i, unt in enumerate(self.units):
                if unt.x == x and unt.y == y:
                    return i
        return None

    def __str__(self):
        return str(self.tiles).replace("'", "").replace(" ", "")[1:-1]

    @property
    def selected_unit(self):
        return self._selected_unit

    @selected_unit.setter
    def selected_unit(self, val):
        if self._selected_unit is not None:
            self.units[self._selected_unit].selected = False
        self._selected_unit = val
        if self._selected_unit is not None:
            self.units[self._selected_unit].selected = True


if __name__ == '__main__':
    # m = Map(None, [])
    # m.generate_tiles_from_ratio(0.25, 0.2, 0.3)
    # print(m.tiles)
    a = [[['forest'], ['forest'], ['dirt'], ['dirt']], [['dirt'], ['forest'], ['forest', 'wall_down'], ['forest', 'wall_left', 'wall_down']], [['dirt'], ['dirt'], ['dirt', 'wall_up'], ['forest', 'wall_left', 'wall_up']], [['dirt'], ['dirt'], ['dirt'], ['dirt']]]
    for val in rotate2(a, 1):
        print(val)
