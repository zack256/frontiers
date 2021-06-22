import cv2

import edit_json

class MapImage:
    def __init__(self, path = "", name = "", image = None):
        if image is not None:
            self.image = image
        else:
            self.image = cv2.imread(path)
        self.name = name if name else path
        self.sections = None
    def save(self, path):
        cv2.imwrite(path, self.image)
    def show(self):
        edit_json.show_image_workaround("Viewing {}".format(self.name), self.image)