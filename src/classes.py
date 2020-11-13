import numpy as np

class Coordinate:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class EllipsisDef:
    def __init__(self, pts = None):
        if pts is None:
            self.pts = []
        elif pts.shape == (5,2):
            self.pts = pts
        else:
            raise TypeError("A nd array of 5 coordinates is expected")

    def __repr__(self):
        return str(self.pts)