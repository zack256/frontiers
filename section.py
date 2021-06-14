class GJSection:
    def __init__(self, color, extrema, name = ""):
        self.color = color
        self.extrema = extrema
        self.name = name
    def update_extrema(self, new_y, new_x):
        self.extrema[0] = min(new_y, self.extrema[0])
        self.extrema[1] = max(new_y, self.extrema[1])
        self.extrema[2] = min(new_x, self.extrema[2])
        self.extrema[3] = max(new_x, self.extrema[3])
    def merge_extrema(self, other_extrema):
        self.update_extrema(other_extrema[0], other_extrema[2])
        self.update_extrema(other_extrema[1], other_extrema[3])
