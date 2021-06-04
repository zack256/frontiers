import cv2
import numpy as np
import json
import random

from utils import *

def se(struc, idx, compare_with, do_max):    # set extreme
    if do_max:
        struc[idx] = max(compare_with, struc[idx])
    else:
        struc[idx] = min(compare_with, struc[idx])

def gather_sections_from_sectioned_image(image, dims):
    section_colors = {}
    sections = []
    for i in range(dims[0]):
        for j in range(dims[1]):
            cell = tuple(image[i][j])
            if is_black(cell):
                continue
            if cell in section_colors:
                se(section_colors[cell], 0, i, False)
                se(section_colors[cell], 1, i, True)
                se(section_colors[cell], 2, j, False)
                se(section_colors[cell], 3, j, True)
            else:
                section_colors[cell] = [i, i, j, j, (i, j)]  # northernmost pt, south, west, east. also includes a point in the image for sample.
    for k in section_colors:
        sections.append((k, section_colors[k]))
    return sections

def show_specific_section(image, sections, idx):
    margin = 20 # for context
    extrema = sections[idx][1]
    cropped_image = image[extrema[0] - margin : extrema[1] + margin, extrema[2] - margin : extrema[3] + margin]
    show_image_workaround("Section #{}".format(idx), cropped_image)

def black_out_section(image_to_edit, point, new_color = None):
    if not new_color:
        new_color = (0, 0, 0)   # default blacking out
    color = image_to_edit[point[0]][point[1]].copy()
    cnt = 0
    to_do = [(point[0], point[1])]
    image_to_edit[point[0]][point[1]] = np.array(new_color)

    while to_do:
        pt = to_do.pop(0)
        cnt += 1
        neighbors = [(pt[0] + 1, pt[1]), (pt[0] - 1, pt[1]), (pt[0], pt[1] - 1), (pt[0], pt[1] + 1)]
        for neighbor in neighbors:
            if image_to_edit[neighbor[0]][neighbor[1]] == color:
                image_to_edit[neighbor[0]][neighbor[1]] = np.array(new_color)

    print(cnt, "painted tiles")

