import cv2
import numpy as np
import json

from utils import *

def good_start(img, pos):
    return (pos[0] == 0 or is_black(img[pos[0] - 1][pos[1]])) and (pos[1] == 0 or is_black(img[pos[0]][pos[1] - 1]))

def is_border(img, pos):
    if pos[0] < 0 or pos[0] >= img.shape[0] or pos[1] < 0 or pos[1] >= img.shape[1]:
        return True
    return is_black(img[pos[0]][pos[1]])

def get_tile_to_right(pos, orientation):
    if orientation == 0:
        return (pos[0] + 1, pos[1])
    elif orientation == 1:
        return (pos[0], pos[1] + 1)
    elif orientation == 2:
        return (pos[0] - 1, pos[1])
    else:
        return (pos[0], pos[1] - 1)

def get_tile_in_front(pos, orientation):
    if orientation == 0:
        return (pos[0], pos[1] + 1)
    elif orientation == 1:
        return (pos[0] - 1, pos[1])
    elif orientation == 2:
        return (pos[0], pos[1] - 1)
    else:
        return (pos[0] + 1, pos[1])

def outline_section(img, start, visited):
    orientation = 3 # ENWS
    pos = start
    points = [pos]
    while True:
        visited.add(pos)
        right_pos = get_tile_to_right(pos, orientation)
        front_pos = get_tile_in_front(pos, orientation)

        if is_border(img, right_pos):
            if is_border(img, front_pos):
                points.append(get_tile_in_front(points[-1], orientation))
                orientation = (orientation + 1) % 4 # turning left.
            else:
                pos = front_pos
                points.append(get_tile_in_front(points[-1], orientation))
        else:
            orientation = (orientation - 1) % 4 # turning right.
            front_pos = get_tile_in_front(pos, orientation)
            pos = front_pos
        if points[-1] == start:
            break
    return points

def simplify_straight_lines(outline_pts):
    new_points = []
    for i in range(len(outline_pts)):
        if i and i < len(outline_pts) - 1:  # first and last points have to be the same I think.
            if (outline_pts[i - 1][0] == outline_pts[i][0] == outline_pts[i + 1][0]) or (outline_pts[i - 1][1] == outline_pts[i][1] == outline_pts[i + 1][1]):
                continue
        new_points.append(outline_pts[i])
    return new_points

def gen_json_base():
    d = {}
    d["type"] = "FeatureCollection"
    d["features"] = []
    return d

def gen_coord_list(outline_pts, scalar):
    l = []
    for pt in outline_pts:
        # reverses pts to get an x, y instead of row, col.
        # also scales down so can fit on world map.
        # also does negative for the y coord, if positive it would render upside down, maybe :)
        x_coord = pt[1] * scalar
        y_coord = pt[0] * scalar * -1
        l.append([x_coord, y_coord])
    return l

def multipolygon_convert_sectioned_to_geojson(input_path, output_path):
    d = gen_json_base()
    sectioned_img = cv2.imread(input_path)
    visited = set()
    same_colored_sections = {}

    for i in range(sectioned_img.shape[0]):
        for j in range(sectioned_img.shape[1]):

            if is_black(sectioned_img[i][j]) or is_white(sectioned_img[i][j]):
                continue
            pos = (i, j)
            if pos in visited:
                continue
            if not good_start(sectioned_img, pos):
                continue

            outline_points = outline_section(sectioned_img, pos, visited)
            simplified_points = simplify_straight_lines(outline_points)
            coord_list = gen_coord_list(simplified_points, 0.01)

            color = tuple(sectioned_img[i][j])
            if color in same_colored_sections:
                same_colored_sections[color].append(coord_list)
            else:
                same_colored_sections[color] = [coord_list]

    for specific_color in same_colored_sections:
        new_feature = {"type": "Feature",
                       "properties": {},
                       "geometry": {
                           "type": "MultiPolygon", "coordinates": []}}
        for shape in same_colored_sections[specific_color]:
            new_feature["geometry"]["coordinates"].append( [ shape ] )

        d["features"].append(new_feature)

    with open(output_path, "w") as fi:
        json.dump(d, fi)