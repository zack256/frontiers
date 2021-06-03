import sys

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout

import opcv

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("Frontiers")
window.setGeometry(60, 15, 280, 80)

def show_image_func():
    opcv.display_img()

btn = QPushButton('Show the image!')
btn.clicked.connect(show_image_func)

layout = QVBoxLayout()
layout.addWidget(btn)
window.setLayout(layout)

window.show()

sys.exit(app.exec_())