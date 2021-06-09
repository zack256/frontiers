import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QGridLayout, QLineEdit
import cv2
import os

import color_sections
import to_json
import edit_json
from testing import testing_directory
import utils

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Frontiers")
window.setGeometry(60, 15, 280, 80)

def section_color_button_handler():
    read_file = testing_directory + "/bw.png"
    write_file = testing_directory + "/sectioned.png"
    color_sections.color_image(read_file, write_file)

def to_json_button_handler():
    read_file = testing_directory + "/sectioned.png"
    write_file = testing_directory + "/gj.json"
    to_json.multipolygon_convert_sectioned_to_geojson(read_file, write_file)

def delete_all_widgets(layout):
    num_children = layout.count()
    for i in range(num_children - 1, -1, -1):
        layout.itemAt(i).widget().setParent(None)

def show_section_with_context(img, sections, idx):
    if not sections[idx]:
        print("section has been merged already!")
        return
    edit_json.show_specific_section(img, sections, idx)

def merge_button_handler():
    global section_colors

    merge_keep = int(merge_inp_1.text()); merge_merge = int(merge_inp_2.text())
    merge_inp_1.clear(); merge_inp_2.clear()
    #sample_point = section_colors[merge_merge][1][4]

    if not (section_colors[merge_merge] and (merge_keep == -1 or section_colors[merge_keep])):
        print("cant merge non existant section(s)")
        return

    merge_from_color = section_colors[merge_merge][0]
    if merge_keep == -1:
        merge_to_color = utils.colors["WHITE"]
    else:
        merge_to_color = section_colors[merge_keep][0]

    edit_json.change_sections_of_specific_color(editing_image, merge_from_color, merge_to_color)

    if merge_keep != -1:
        edit_json.se(section_colors[merge_keep][1], 0, section_colors[merge_merge][1][0], False)
        edit_json.se(section_colors[merge_keep][1], 1, section_colors[merge_merge][1][1], True)
        edit_json.se(section_colors[merge_keep][1], 2, section_colors[merge_merge][1][2], False)
        edit_json.se(section_colors[merge_keep][1], 3, section_colors[merge_merge][1][3], True)

    section_colors[merge_merge] = None

def save_button_handler():
    path = testing_directory + "/better_sectioned.png"
    cv2.imwrite(path, editing_image)

def view_image_handler():
    #path = testing_directory + "/better_sectioned.png"
    edit_json.show_image_workaround("Viewing image", editing_image)

def edit_json_button_handler():
    global merge_inp_1, merge_inp_2, section_colors, editing_image
    read_file = testing_directory + "/sectioned.png"
    editing_image = cv2.imread(read_file)
    if not os.path.isfile(read_file):
        print("needs to be sectioned first.")
        return
    section_colors = edit_json.gather_sections_from_sectioned_image(editing_image)
    delete_all_widgets(layout)
    btns = []
    num_cols = 5 * 2
    num_rows_displaying_sections = (len(section_colors) * 2) // num_cols + 1
    for i in range(len(section_colors)):
        btn = QPushButton("view #" + str(i))
        btn.clicked.connect(lambda x, i=i : show_section_with_context(editing_image, section_colors, i))  # i=i to prevent closure
        btns.append(btn)
        layout.addWidget(btn, (2 * i) // num_cols, (2 * i) % num_cols)

        color_box = QPushButton()
        color_box.setStyleSheet("background-color: rgb" + str(utils.bgr_to_rgb(section_colors[i][0])))
        layout.addWidget(color_box, (2 * i + 1) // num_cols, (2 * i + 1) % num_cols)

    merge_lab_1 = QLabel("Keep:")
    merge_inp_1 = QLineEdit()
    merge_lab_2 = QLabel("Merge:")
    merge_inp_2 = QLineEdit()

    layout.addWidget(merge_lab_1, num_rows_displaying_sections, 0)
    layout.addWidget(merge_inp_1, num_rows_displaying_sections, 1)
    layout.addWidget(merge_lab_2, num_rows_displaying_sections, 2)
    layout.addWidget(merge_inp_2, num_rows_displaying_sections, 3)

    merge_button = QPushButton("Merge Sections")
    merge_button.clicked.connect(merge_button_handler)
    layout.addWidget(merge_button, num_rows_displaying_sections, 4)

    save_button = QPushButton("Save")
    save_button.clicked.connect(save_button_handler)
    layout.addWidget(save_button, num_rows_displaying_sections, 5)

    view_image_button = QPushButton("View Image")
    view_image_button.clicked.connect(view_image_handler)
    layout.addWidget(view_image_button, num_rows_displaying_sections + 1, 0)

section_color_button = QPushButton("Section color")
section_color_button.clicked.connect(section_color_button_handler)

to_json_button = QPushButton("Convert to geojson")
to_json_button.clicked.connect(to_json_button_handler)

edit_json_button = QPushButton("Edit sections")
edit_json_button.clicked.connect(edit_json_button_handler)

merge_button = None
merge_inp_1 = merge_inp_2 = None
editing_image = None

layout = QGridLayout()
layout.addWidget(section_color_button)
layout.addWidget(to_json_button)
layout.addWidget(edit_json_button)
window.setLayout(layout)

section_colors = None

window.show()

sys.exit(app.exec_())