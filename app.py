import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QGridLayout, QLineEdit, QMainWindow
import cv2
import os

import color_sections
import to_json
import edit_json
from testing import testing_directory
import utils

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

def back_to_main_handler():
    ej_window.hide()
    main_window.show()

def edit_json_button_handler():
    global merge_inp_1, merge_inp_2, section_colors, editing_image
    read_file = testing_directory + "/sectioned.png"
    editing_image = cv2.imread(read_file)
    if not os.path.isfile(read_file):
        print("needs to be sectioned first.")
        return
    section_colors = edit_json.gather_sections_from_sectioned_image(editing_image)
    #delete_all_widgets(layout)
    btns = []
    num_cols = 5 * 2
    section_rows = (len(section_colors) * 2) // num_cols + 1
    for i in range(len(section_colors)):
        btn = QPushButton("view #" + str(i))
        btn.clicked.connect(lambda x, i=i : show_section_with_context(editing_image, section_colors, i))  # i=i to prevent closure
        btns.append(btn)
        ej_layout.addWidget(btn, (2 * i) // num_cols, (2 * i) % num_cols)

        color_box = QPushButton()
        color_box.setStyleSheet("background-color: rgb" + str(utils.bgr_to_rgb(section_colors[i][0])))
        ej_layout.addWidget(color_box, (2 * i + 1) // num_cols, (2 * i + 1) % num_cols)

    merge_lab_1 = QLabel("Keep:")
    merge_inp_1 = QLineEdit()
    merge_lab_2 = QLabel("Merge:")
    merge_inp_2 = QLineEdit()

    ej_layout.addWidget(merge_lab_1, section_rows, 0)
    ej_layout.addWidget(merge_inp_1, section_rows, 1)
    ej_layout.addWidget(merge_lab_2, section_rows, 2)
    ej_layout.addWidget(merge_inp_2, section_rows, 3)

    merge_button = ej_layout.add_button("Merge Sections", merge_button_handler, section_rows, 4)
    save_button = ej_layout.add_button("Save", save_button_handler, section_rows, 5)
    view_image_button = ej_layout.add_button("View Image", view_image_handler, section_rows + 1, 0)
    back_button = ej_layout.add_button("Back (doesn't save)", back_to_main_handler, section_rows + 1, 1)

    main_window.hide()
    ej_window.show()

merge_button = None
merge_inp_1 = merge_inp_2 = None
editing_image = None
section_colors = None

class Window(QWidget):
    def __init__(self, title, layout):
        super().__init__()
        self.setWindowTitle(title)
        self.setLayout(layout)

class Layout(QGridLayout):
    def __init__(self):
        super().__init__()
    def add_button(self, label, click_function, row = -1, col = -1):
        button = QPushButton(label)
        button.clicked.connect(click_function)
        if row != -1 and col != -1:
            self.addWidget(button, row, col)
        else:
            self.addWidget(button)
        return button

app = QApplication(sys.argv)

main_layout = Layout()
section_color_button = main_layout.add_button("Section color", section_color_button_handler)
to_json_button = main_layout.add_button("Convert to geojson", to_json_button_handler)
edit_json_button = main_layout.add_button("Edit sections", edit_json_button_handler)

main_window = Window("Frontiers", main_layout)
main_window.setGeometry(60, 15, 280, 80)

ej_layout = Layout()
ej_window = Window("Editing Sections", ej_layout)

main_window.show()

sys.exit(app.exec_())