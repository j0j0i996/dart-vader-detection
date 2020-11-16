import cv2
import numpy as np
from boardClass import * # is required?

class dartThrow:
    def __init__(self, img_before_link, img_after_link):
        self.img_before_link = img_before_link
        self.img_after_link = img_after_link
        self.is_dart = self.is_dart(self)
        if self.is_dart:
            self.pixel_pos = self.get_pixel_position()
        
        self.std_carth_pos = None
        self.std_polar_pos = None
        self.score = None

    def is_dart(self):
        # Fake implementation to test other functions
        return True

    def set_pixel_position(self):
        # Fake implementation to test other functions
        self.pixel_pos = np.float32([0,0]])

    def set_score(self, relBoard, stdBoard):
        self.std_carth_pos = self.transform_rel_pos_to_std_pos(
            self.pixel_pos,relBoard, stdBoard)
        self.std_polar_pos = self.set_pixel_position(std_carth_pos, stdBoard.get_center())
        self.score = self.std_polar_pos_to_score(std_polar_pos)
        

    def get_score(self, relBoard, stdBoard)
        if self.score = None:
            self.set_score(self, relBoard, stdBoard)
        return self.score

    @staticmethod
    def transform_rel_pos_to_std_pos(pixel_pos,relBoard, stdBoard)
        # to be implemented
        return

    @staticmethod
    def set_polar_pos(std_pixel_pos)
        # to be implemented
        return

    @staticmethod
    def std_polar_pos_to_score(std_polar_pos)
        # to be implemented
        return 60
    
