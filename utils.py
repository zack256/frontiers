import random

def is_black(cell):
    return sum(cell) == 0

def is_white(cell):
    return sum(cell) == 765

def r256():
    return random.randrange(256)

def generate_random_color():
    return (r256(), r256(), r256())

def generate_unique_color(already):
    while True:
        color = generate_random_color()
        if is_white(color) or is_black(color):
            continue
        if color not in already:
            return color

def bgr_to_rgb(bgr):
    return bgr[::-1]