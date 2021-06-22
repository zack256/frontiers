import cv2
import numpy as np
import json

from utils import *

from section import GJSection

def gather_sections_from_sectioned_image(mi):
    image = mi.image
    section_colors = {}
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            cell = tuple(image[i][j])
            if is_black(cell) or is_white(cell):
                continue
            if cell in section_colors:
                section_colors[cell].update_extrema(i, j)
            else:
                new_section = GJSection(color = cell, extrema = [i, i, j, j])
                section_colors[cell] = new_section
    return list(section_colors.values())

def show_image_workaround(title, image):
    # investigate further!!!
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

def show_specific_section(image, sections, idx):
    margin = 20 # for context
    extrema = sections[idx].extrema; section_name = sections[idx].name
    cropped_image = image[max(0, extrema[0] - margin) : min(image.shape[0], extrema[1] + margin), max(0, extrema[2] - margin) : min(image.shape[1], extrema[3] + margin)]
    if section_name:
        show_image_workaround("Section #{} ({})".format(idx, section_name), cropped_image)
    else:
        show_image_workaround("Section #{}".format(idx), cropped_image)
    #cv2.imshow("Section #{}".format(idx), cropped_image)

def color_specific_section(image, new_color, point):
    old_color = tuple(image[point[0]][point[1]])
    cnt = 0
    to_do = [(point[0], point[1])]
    image[point[0]][point[1]] = np.array(new_color)

    while to_do:
        pt = to_do.pop(0)
        cnt += 1
        neighbors = [(pt[0] + 1, pt[1]), (pt[0] - 1, pt[1]), (pt[0], pt[1] - 1), (pt[0], pt[1] + 1)]
        for neighbor in neighbors:
            if tuple(image[neighbor[0]][neighbor[1]]) == old_color:
                image[neighbor[0]][neighbor[1]] = new_color
                to_do.append((neighbor[0], neighbor[1]))
    print(cnt, "painted tiles")

def change_sections_of_specific_color(image_to_edit, old_color, new_color):
    cnt = 0
    for i in range(image_to_edit.shape[0]):
        for j in range(image_to_edit.shape[1]):
            if tuple(image_to_edit[i][j]) == old_color:
                color_specific_section(image_to_edit, new_color, (i, j))
                cnt += 1
    print("colored {} sections!".format(cnt))
