import cv2

import edit_json

class MapImage:
    def __init__(self, path = "", name = "", image = None):
        if image is not None:
            self.image = image
        else:
            self.image = cv2.imread(path)
        self.name = name if name else path
        self.sections = edit_json.gather_sections_from_sectioned_image(self)
    def save(self, path):
        cv2.imwrite(path, self.image)
    def show(self):
        edit_json.show_image_workaround("Viewing {}".format(self.name), self.image)
    def remove_merged_sections(self):
        z = 0
        while (z < len(self.sections)):
            if self.sections[z]:
                z += 1
            else:
                self.sections.pop(z)