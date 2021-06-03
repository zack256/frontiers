import cv2
import numpy as np
import random

def r256():
    return random.randrange(256)

def is_white(cell):
    return sum(cell) == 765

def generate_random_color():
    return (r256(), r256(), r256())

def get_neighbor(img, pos, direction):
    # NESW
    if direction == 0:
        if pos[0] == 0:
            return None
        return (pos[0] - 1, pos[1])
    elif direction == 1:
        if pos[1] == img.shape[1] - 1:
            return None
        return (pos[0], pos[1] + 1)
    elif direction == 2:
        if pos[0] == img.shape[0] - 1:
            return None
        return (pos[0] + 1, pos[1])
    else:
        if pos[1] == 0:
            return None
        return (pos[0], pos[1] - 1)

def get_neighbors(img, pos):
    return [get_neighbor(img, pos, d) for d in range(4)]

def generate_unique_color(already):
    while True:
        color = generate_random_color()
        if is_white(color):
            continue
        if color not in already:
            return color

def color_section(img, start, color):
    to_visit = [start]
    img[start[0]][start[1]] = color
    while to_visit:
        current = to_visit.pop(0)
        neighbors = get_neighbors(img, current)
        for neighbor in neighbors:
            if neighbor and is_white(img[neighbor[0]][neighbor[1]]):
                img[neighbor[0]][neighbor[1]] = color
                to_visit.append(neighbor)

def color_image(read_path, write_path):
    img = cv2.imread(read_path)
    colors = set()
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if is_white(img[i][j]):
                color = generate_unique_color(colors)
                colors.add(color)
                color_section(img, (i, j), color)
    cv2.imwrite(write_path, img)