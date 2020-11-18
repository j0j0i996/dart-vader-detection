import cv2
import numpy as np

class dartThrow:

    def __init__(self, img_before_link, img_after_link, board) :
        self.img_before_link = img_before_link
        self.img_after_link = img_after_link
        self.board = board
        self.is_dart = self.is_dart()

        if self.is_dart:
            self.rel_carth_pos = self.get_rel_pos()
            self.std_carth_pos = self.board.rel_carth_pos_to_std_carth_pos(self.rel_carth_pos)

        self.std_polar_pos = None
        self.score = None

    def __repr__(self):
        return 'RelCarth Pos: {} \n\nStd Carth Pos: {} \n'\
            .format(self.rel_carth_pos, self.std_carth_pos)

    def is_dart(self):
        # Fake implementation to test other functions
        return True

    def get_rel_pos(self):
        # Fake implementation to test other functions
        return [443,277]

    def get_score(self, camera):
        if self.score == None:
            self.set_score(self, relBoard, stdBoard)
        return self.score

    def set_score(self, camera):
        self.rel_carth_pos_to_std_carth_pos(camera)
        self.std_carth_pos_to_std_polar_pos()
        self.std_polar_pos_to_score()
    
