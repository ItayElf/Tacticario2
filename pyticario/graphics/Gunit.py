import ctypes
import os

import pygame

u = ctypes.windll.user32
ratio = u.GetSystemMetrics(1) / 1080

imgs = {
    "P1": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_1.png'),
    'P2': os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_2.png'),
    'P1S': os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_1_Selected.png'),
    'P2S': os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_2_Selected.png'),
    'P1U': os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_1_Used.png'),
    'P2U': os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_2_Used.png'),
    'P1US': os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_1_Used_Selected.png'),
    'P2US': os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'units', 'Player_2_Used_Selected.png')
}


class Unit:
    def __init__(self, x, y, number, player, rotation, active):
        self.x = int(x)
        self.y = int(y)
        self.number = int(number)
        self.player = int(player)
        self.rotation = int(rotation) % 4
        self.active = bool(int(active))
        self.selected = False

    def draw_unit(self, screen, tile_size, map_size):
        middle = u.GetSystemMetrics(1) // 2
        top_y = middle - map_size // 2
        size = int(tile_size * 0.9)

        img = imgs[f"P{self.player}{'U' * int(self.active)}{'S' * int(self.selected)}"]
        x = self.x * tile_size + int(0.05 * tile_size)
        y = self.y * tile_size + int(0.05 * tile_size) + top_y
        pic = pygame.transform.scale(pygame.image.load(img), (size, size))
        screen.blit(pic, (x, y))

        font = pygame.font.Font(None, int(size // 1.185))
        text = font.render(str(self.number), True, (0, 0, 0))
        text = pygame.transform.rotate(text, -90 * self.rotation)
        text_rect = text.get_rect()
        text_rect.center = (x + size // 2, y + size // 2)
        screen.blit(text, text_rect)

    def __str__(self):
        return ','.join([str(self.x), str(self.y), str(self.number), str(self.player), str(self.rotation), str(int(self.active))])
