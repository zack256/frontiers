import cv2
import numpy as np
import random

from utils import *
from map_image import MapImage

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

def color_image(mi, new_mi_name):
    img = mi.image.copy()
    colors = set()
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if is_white(img[i][j]):
                color = generate_unique_color(colors)
                colors.add(color)
                color_section(img, (i, j), color)
    new_mi = MapImage(image = img, name = new_mi_name)
    return new_mi