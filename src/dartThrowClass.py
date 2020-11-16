import cv2
import numpy as np
from boardClass import * # is required?

class dartThrow:

    def __init__(self, img_before_link, img_after_link):
        self.img_before_link = img_before_link
        self.img_after_link = img_after_link
        self.set_is_dart(self)

        if self.is_dart:
            self.set_rel_pos()
        else: 
            self.rel_carth_pos = None

        self.std_carth_pos = None
        self.std_polar_pos = None
        self.score = None

    def is_dart(self):
        # Fake implementation to test other functions
        self.is_dart = True

    def set_rel_position(self):
        # Fake implementation to test other functions
        self.rel_carth_pos = np.float32([0,0]])

    def get_score(self, camera)
        if self.score = None:
            self.set_score(self, relBoard, stdBoard)
        return self.score

    def set_score(self, camera):
        self.rel_carth_pos_to_std_carth_pos(camera)
        self.std_carth_pos_to_std_polar_pos()
        self.std_polar_pos_to_score()
        
    def rel_carth_pos_to_std_carth_pos(self, camera)
        # to be implemented
        return

    def std_carth_pos_to_std_polar_pos(self)
        # to be implemented
        return

    def std_polar_pos_to_score(self)
        # to be implemented
        return 60
    
