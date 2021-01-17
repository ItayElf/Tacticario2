import json
import os

import pygame

tiles_arr = [['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'],
             ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt']]

tiles = {
    "dirt": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'dirt.png'),
    "forest": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'forest.png'),
    "water": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'water.png'),
    "wall_left": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_left.png'),
    "wall_right": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_right.png'),
    "wall_up": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_up.png'),
    "wall_down": os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs", 'tiles', 'wall_down.png')
}


def get_tile_from_pixels(x_pixels, y_pixels):
    return x_pixels // 40, y_pixels // 40


def tile(x, y):
    return tiles_arr[4 * y + x]


def draw_tiles(tile_arr):
    tiles_in_row = int(len(tile_arr) ** 0.5)
    for i in range(tiles_in_row ** 2):
        x = (i % tiles_in_row) * 40
        y = (i // tiles_in_row) * 40
        imgs = []

        if "forest" in tile_arr[i]:
            imgs.append(tiles["forest"])
        elif "water" in tile_arr[i]:
            imgs.append(tiles["water"])
        else:
            imgs.append(tiles["dirt"])
        if "wall_right" in tile_arr[i]:
            imgs.append(tiles["wall_right"])
        if "wall_left" in tile_arr[i]:
            imgs.append(tiles["wall_left"])
        if "wall_down" in tile_arr[i]:
            imgs.append(tiles["wall_down"])
        if "wall_up" in tile_arr[i]:
            imgs.append(tiles["wall_up"])
        for img in imgs:
            pic = pygame.transform.scale(pygame.image.load(img), (40, 40))
            screen.blit(pic, (x, y))
    pygame.display.update()


def rotated(tile_arr, rotation):
    mapper = {
        "dirt": "dirt",
        "forest": "forest",
        "water": "water",
        "wall_up": "wall_right",
        "wall_right": "wall_down",
        "wall_down": "wall_left",
        "wall_left": "wall_up"
    }
    n = tile_arr
    tiles_in_row = rows = int(len(n) ** 0.5)
    for _ in range(rotation % 4):
        a = [[list(map(lambda x: mapper[x], n[val + i])) for val in range(tiles_in_row * (rows - 1), -1, -4)] for i in range(0, 4)]
        n = [val for sublist in a for val in sublist]
    return n


def add_to_config(tile_arr):
    tile_arr = [tile_arr[i*4:i*4 + 4] for i in range(0, 4)]
    name = input("Name: ")
    if not name:
        return

    with open("tilesconfig.json", "r+") as f:
        data = json.load(f)
    if name in data.keys():
        print("Name already exists")
        return
    data[name] = tile_arr

    with open("tilesconfig.json", 'w') as f:
        json.dump(data, f)
    print("Saved")


if __name__ == '__main__':
    screen = pygame.display.set_mode((160, 160))
    index = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    add_to_config(tiles_arr)
                elif event.key == pygame.K_r:
                    tiles_arr = [['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'],
                                 ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt'], ['dirt']]
                elif event.key == pygame.K_p:
                    tiles_arr = rotated(tiles_arr, 1)
                elif event.key == pygame.K_d:
                    tiles_arr[index] = ["dirt"]
                elif event.key == pygame.K_f:
                    tiles_arr[index] = ["forest"]
                elif event.key == pygame.K_w:
                    tiles_arr[index] = ["water"]
                elif event.key == pygame.K_UP:
                    try:
                        tiles_arr[index].remove("wall_up")
                    except ValueError:
                        tiles_arr[index].append("wall_up")
                elif event.key == pygame.K_DOWN:
                    try:
                        tiles_arr[index].remove("wall_down")
                    except ValueError:
                        tiles_arr[index].append("wall_down")
                elif event.key == pygame.K_LEFT:
                    try:
                        tiles_arr[index].remove("wall_left")
                    except ValueError:
                        tiles_arr[index].append("wall_left")
                elif event.key == pygame.K_RIGHT:
                    try:
                        tiles_arr[index].remove("wall_right")
                    except ValueError:
                        tiles_arr[index].append("wall_right")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = get_tile_from_pixels(*pygame.mouse.get_pos())
                index = 4 * y + x

        draw_tiles(tiles_arr)
