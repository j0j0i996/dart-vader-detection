import numpy as np

class Board:
    def __init__(self, pts = None, std = False):
        if pts is None:
            self.pts = []
        elif pts.shape == (5,2):
            self.pts = pts
        else:
            raise TypeError("A nd array of 5 coordinates is expected")

        if std = True:
            set_standard_pts(self)

    def __repr__(self):
        return str(self.pts)

    def get_center(self):
        #Fake implementation to test:
        return np.float([0,0])

    def set_standard_pts(self):
        