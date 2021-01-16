import ctypes
import os
import random

import pygame as pg

u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080

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
    m = Map(None, [])
    m.generate_tiles_from_ratio(0.25, 0.2, 0.3)
    print(m.tiles)
