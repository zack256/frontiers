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
from map_image import MapImage

def simple_function_wrapper(text_inps, func, **click_function_kwargs):
    texts = []; n = len(text_inps)
    for i in range(n):
        text = text_inps[i].text()
        texts.append(text)
        text_inps[i].clear()
    for i in range(n):  # fix to deal with non-files
        if texts[i] == "":
            print("no file specified."); return
    func(texts, **click_function_kwargs)

def simple_function_row(layout, label_texts, button_text, click_function, row = -1, **click_function_kwargs):
    n = len(label_texts)
    labels = []; inps = []
    for i in range(n):
        label = layout.add_label(label_texts[i], row, 2 * i)
        inp = layout.add_text_input(row, 2 * i + 1)
        labels.append(label); inps.append(inp)
    wrapped_func = lambda : simple_function_wrapper(inps, click_function, **click_function_kwargs)
    button = layout.add_button(button_text, lambda : wrapped_func(), row, 2 * n)
    return inps, labels, button

def section_color_button_handler(inps):
    new_mi_name = inps[0]
    new_mi = color_sections.color_image(mi, new_mi_name)
    mis[new_mi_name] = new_mi

def to_json_button_handler(filenames):
    write_file = testing_directory + filenames[0]
    sections = mi.sections
    if not sections:
        color_to_section_dict = None
    else:
        color_to_section_dict = {}
        for section in sections:
            color_to_section_dict[section.color] = section
    to_json.multipolygon_convert_sectioned_to_geojson(mi, write_file, color_to_section_dict)

def delete_all_widgets(layout):
    num_children = layout.count()
    for i in range(num_children - 1, -1, -1):
        layout.itemAt(i).widget().setParent(None)

def show_section_with_context(img, sections, idx):
    if not sections[idx]:
        print("section has been merged already!")
        return
    edit_json.show_specific_section(img, sections, idx)

def merge_button_handler(input_texts):
    sections = mi.sections
    merge_keep, merge_merge = map(int, input_texts)
    if not (sections[merge_merge] and (merge_keep == -1 or sections[merge_keep])):
        print("cant merge non existant section(s)")
        return

    merge_from_color = sections[merge_merge].color
    if merge_keep == -1:
        merge_to_color = utils.colors["WHITE"]
    else:
        merge_to_color = sections[merge_keep].color

    edit_json.change_sections_of_specific_color(mi.image, merge_from_color, merge_to_color)
    if merge_keep != -1:
        sections[merge_keep].merge_extrema(sections[merge_merge].extrema)
    sections[merge_merge] = None

def back_to_main_handler():
    mi.remove_merged_sections()
    ej_window.hide()
    main_window.show()

def set_name_handler(input_texts):
    section_idx = int(input_texts[0]); new_name = input_texts[1]
    mi.sections[section_idx].name = new_name

def edit_json_button_handler(_inps):
    ej_layout = ej_window.layout()
    delete_all_widgets(ej_layout)
    sections = mi.sections
    btns = []
    num_cols = 5 * 2
    section_rows = (len(sections) * 2) // num_cols + 1
    for i in range(len(sections)):
        btn = QPushButton("view #" + str(i))
        btn.clicked.connect(lambda x, i=i : show_section_with_context(mi.image, sections, i))  # i=i to prevent closure
        btns.append(btn)
        ej_layout.addWidget(btn, (2 * i) // num_cols, (2 * i) % num_cols)

        color_box = QPushButton()
        color_box.setStyleSheet("background-color: rgb" + str(utils.bgr_to_rgb(sections[i].color)))
        ej_layout.addWidget(color_box, (2 * i + 1) // num_cols, (2 * i + 1) % num_cols)

    view_image_button = ej_layout.add_button("View Image", show_img_handler, section_rows + 3, 0)
    back_button = ej_layout.add_button("Back", back_to_main_handler, section_rows + 3, 1)

    merge_row = simple_function_row(ej_layout, ["Keep:", "Merge:"], "Merge Sections", merge_button_handler, section_rows)
    set_name_row = simple_function_row(ej_layout, ["Section # to rename:", "Name:"], "Set Name", set_name_handler, section_rows + 1)
    save_row = simple_function_row(ej_layout, ["Save to:"], "Save", save_img_handler, section_rows + 2)

    main_window.hide()
    ej_window.show()

def show_img_handler(_inps = None):
    mi.show()

def save_img_handler(inps):
    path = testing_directory + inps[0]
    mi.save(path)

def load_new_mi_handler(input_texts):
    global mi
    path = testing_directory + input_texts[0]
    name = input_texts[1]
    mi = MapImage(path, name)
    mis[name] = mi
    load_main_window()

def load_existing_mi_handler(_input_texts, mi_name):
    global mi
    mi = mis[mi_name]
    load_main_window()

def load_main_window():
    start_window.hide()
    main_window.setWindowTitle("Working with {}".format(mi.name))
    main_window.show()

def back_to_start_handler(_filenames):
    global mi
    mi = None
    delete_all_widgets(start_window.layout())
    load_image_row = simple_function_row(start_window.layout(), ["Read", "Name"], "Load Image", load_new_mi_handler, 0)
    keys =  sorted(mis.keys())
    for i in range(len(mis)):
        mi_name = mis[keys[i]].name
        row = simple_function_row(start_window.layout(), [], "Open {}".format(mi_name), load_existing_mi_handler, i + 1, mi_name = mi_name)
    main_window.hide()
    start_window.show()

mi = None
mis = {}

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

main_window = ej_window = start_window = None

def init_windows():
    global main_window, ej_window, start_window

    start_layout = Layout()
    main_layout = Layout()

    load_image_row = simple_function_row(start_layout, ["Read", "Name"], "Load Image", load_new_mi_handler, 0)

    section_color_bw_row = simple_function_row(main_layout, ["New image name"], "Section color from BW", section_color_button_handler, 0)
    to_json_row = simple_function_row(main_layout, ["Write"], "Convert to GeoJson", to_json_button_handler, 1)
    edit_json_button = simple_function_row(main_layout, [], "Edit sections", edit_json_button_handler, 2)
    show_img_button = simple_function_row(main_layout, [], "Show Image", show_img_handler, 3)
    save_img_button = simple_function_row(main_layout, ["Write"], "Save image", save_img_handler, 4)
    back_to_start_button = simple_function_row(main_layout, [], "Back", back_to_start_handler, 5)

    main_window = Window("Frontiers", main_layout)
    main_window.setGeometry(60, 15, 280, 80)

    ej_layout = Layout()
    ej_window = Window("Editing Sections", ej_layout)

    start_window = Window("Frontiers", start_layout)
    start_window.setGeometry(60, 15, 280, 80)

    start_window.show()

init_windows()

sys.exit(app.exec_())