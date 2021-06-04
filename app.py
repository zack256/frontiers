import sys

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout

import opcv
import color_sections
import to_json
from testing import testing_directory

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

section_color_button = QPushButton("Section color")
section_color_button.clicked.connect(section_color_button_handler)

to_json_button = QPushButton("Convert to geojson")
to_json_button.clicked.connect(to_json_button_handler)

layout = QVBoxLayout()
layout.addWidget(section_color_button)
layout.addWidget(to_json_button)
window.setLayout(layout)

window.show()

sys.exit(app.exec_())