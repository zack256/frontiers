import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QGridLayout, QLineEdit
import cv2
import os

import color_sections
import to_json
import edit_json
from testing import testing_directory
import utils
from section import GJSection

def simple_function_wrapper(text_inps, func):
    texts = []; n = len(text_inps)
    for i in range(n):
        text = text_inps[i].text()
        texts.append(text)
        text_inps[i].clear()
    for i in range(n):
        if texts[i] == "":
            print("no file specified."); return
    func(texts)

def simple_function_row(layout, label_texts, button_text, click_function, row = -1):
    n = len(label_texts)
    labels = []; inps = []
    for i in range(n):
        label = layout.add_label(label_texts[i], row, 2 * i)
        inp = layout.add_text_input(row, 2 * i + 1)
        labels.append(label); inps.append(inp)
    wrapped_func = lambda : simple_function_wrapper(inps, click_function)
    button = layout.add_button(button_text, lambda : wrapped_func(), row, 2 * n)
    return inps, labels, button

def section_color_button_handler(filenames):
    read_file = testing_directory + "/" + filenames[0]
    write_file = testing_directory + "/" + filenames[1]
    color_sections.color_image(read_file, write_file)

def to_json_button_handler(filenames):
    if not sections:
        print("need to make sections first."); return
    read_file = testing_directory + "/" + filenames[0]
    write_file = testing_directory + "/" + filenames[1]
    color_to_section_dict = {}
    for section in sections:
        color_to_section_dict[section.color] = section
    to_json.multipolygon_convert_sectioned_to_geojson(read_file, write_file, color_to_section_dict)

def delete_all_widgets(layout):
    num_children = layout.count()
    for i in range(num_children - 1, -1, -1):
        layout.itemAt(i).widget().setParent(None)

def show_section_with_context(img, sections, idx):
    if not sections[idx]:
        print("section has been merged already!")
        return
    edit_json.show_specific_section(img, sections, idx)

def merge_button_handler(merge_inp_1, merge_inp_2):
    global sections

    merge_keep = int(merge_inp_1.text()); merge_merge = int(merge_inp_2.text())
    merge_inp_1.clear(); merge_inp_2.clear()

    if not (sections[merge_merge] and (merge_keep == -1 or sections[merge_keep])):
        print("cant merge non existant section(s)")
        return

    merge_from_color = sections[merge_merge].color
    if merge_keep == -1:
        merge_to_color = utils.colors["WHITE"]
    else:
        merge_to_color = sections[merge_keep].color

    edit_json.change_sections_of_specific_color(editing_image, merge_from_color, merge_to_color)

    if merge_keep != -1:
        sections[merge_keep].merge_extrema(sections[merge_merge].extrema)

    sections[merge_merge] = None

def ej_save_button_handler(save_file_inp):
    #path = testing_directory + "/better_sectioned.png"
    filename = save_file_inp.text()
    if filename == "":
        print("no save file specified!"); return
    path = testing_directory + "/" + filename
    save_file_inp.clear()
    cv2.imwrite(path, editing_image)

def view_image_handler():
    #path = testing_directory + "/better_sectioned.png"
    edit_json.show_image_workaround("Viewing image", editing_image)

def back_to_main_handler():
    ej_window.hide()
    main_window.show()

def set_name_handler(set_name_inp_1, set_name_inp_2):
    global sections
    section_idx = int(set_name_inp_1.text()); new_name = set_name_inp_2.text()
    set_name_inp_1.clear(); set_name_inp_2.clear()
    sections[section_idx].name = new_name

def edit_json_button_handler():
    global sections, editing_image
    ej_layout = ej_window.layout()
    read_file = testing_directory + "/sectioned.png"
    editing_image = cv2.imread(read_file)
    if not os.path.isfile(read_file):
        print("needs to be sectioned first.")
        return
    sections = edit_json.gather_sections_from_sectioned_image(editing_image)
    #delete_all_widgets(layout)
    btns = []
    num_cols = 5 * 2
    section_rows = (len(sections) * 2) // num_cols + 1
    for i in range(len(sections)):
        btn = QPushButton("view #" + str(i))
        btn.clicked.connect(lambda x, i=i : show_section_with_context(editing_image, sections, i))  # i=i to prevent closure
        btns.append(btn)
        ej_layout.addWidget(btn, (2 * i) // num_cols, (2 * i) % num_cols)

        color_box = QPushButton()
        color_box.setStyleSheet("background-color: rgb" + str(utils.bgr_to_rgb(sections[i].color)))
        ej_layout.addWidget(color_box, (2 * i + 1) // num_cols, (2 * i + 1) % num_cols)

    merge_lab_1 = ej_layout.add_label("Keep:", section_rows, 0)
    merge_lab_2 = ej_layout.add_label("Merge:", section_rows, 2)
    set_name_lab_1 = ej_layout.add_label("Section # to rename:", section_rows + 1, 0)
    set_name_lab_2 = ej_layout.add_label("Name:", section_rows + 1, 2)
    save_lab = ej_layout.add_label("Save to:", section_rows + 2, 0)

    merge_inp_1 = ej_layout.add_text_input(section_rows, 1)
    merge_inp_2 = ej_layout.add_text_input(section_rows, 3)
    set_name_inp_1 = ej_layout.add_text_input(section_rows + 1, 1)
    set_name_inp_2 = ej_layout.add_text_input(section_rows + 1, 3)
    save_inp = ej_layout.add_text_input(section_rows + 2, 1)

    merge_button = ej_layout.add_button("Merge Sections", lambda : merge_button_handler(merge_inp_1, merge_inp_2), section_rows, 4)
    set_name_button = ej_layout.add_button("Set Name", lambda : set_name_handler(set_name_inp_1, set_name_inp_2), section_rows + 1, 4)
    save_button = ej_layout.add_button("Save", lambda : ej_save_button_handler(save_inp), section_rows + 2, 2)
    view_image_button = ej_layout.add_button("View Image", view_image_handler, section_rows + 3, 0)
    back_button = ej_layout.add_button("Back (doesn't save)", back_to_main_handler, section_rows + 3, 1)

    main_window.hide()
    ej_window.show()

editing_image = None
sections = None

class Window(QWidget):
    def __init__(self, title, layout):
        super().__init__()
        self.setWindowTitle(title)
        self.setLayout(layout)

class Layout(QGridLayout):
    def __init__(self):
        super().__init__()
    def add_widget_to_grid(self, widget, row = -1, col = -1):
        if row != -1 and col != -1:
            self.addWidget(widget, row, col)
        else:
            self.addWidget(widget)
        return widget
    def add_button(self, label, click_function, row = -1, col = -1):
        button = QPushButton(label)
        button.clicked.connect(click_function)
        return self.add_widget_to_grid(button, row, col)
    def add_label(self, text, row = -1, col = -1):
        label = QLabel(text)
        return self.add_widget_to_grid(label, row, col)
    def add_text_input(self, row = -1, col = -1):
        inp = QLineEdit()
        return self.add_widget_to_grid(inp, row, col)

app = QApplication(sys.argv)

main_window = ej_window = None

def init_windows():
    global main_window, ej_window

    main_layout = Layout()

    section_color_row = simple_function_row(main_layout, ["Read", "Write"], "Section color", section_color_button_handler, 0)
    to_json_row = simple_function_row(main_layout, ["Read", "Write"], "Convert to GeoJson", to_json_button_handler, 1)

    edit_json_button = main_layout.add_button("Edit sections", edit_json_button_handler)

    main_window = Window("Frontiers", main_layout)
    main_window.setGeometry(60, 15, 280, 80)

    ej_layout = Layout()
    ej_window = Window("Editing Sections", ej_layout)

    main_window.show()

init_windows()

sys.exit(app.exec_())