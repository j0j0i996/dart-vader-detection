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
            self.score = self.board.get_score(self.rel_carth_pos)

    def __repr__(self):
        return 'RelCarth Pos: {} \n\nStd Carth Pos: {} \n'\
            .format(self.rel_carth_pos, self.std_carth_pos)

    def is_dart(self):
        # Fake implementation to test other functions
        return True

    def get_rel_pos(self):
        img_bf = cv2.imread(self.img_before_link)
        img_af = cv2.imread(self.img_after_link)
        diff = cv2.absdiff(img_af, img_bf)

        # transform to gray scale
        diffGray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        # add blur
        diffBlur = cv2.GaussianBlur(diffGray,(7,7),2)

        # apply Canny edge detector
        diffCanny = cv2.Canny(diffBlur, 0, 100)
        
        width, height = diffCanny.shape[:2]

        # find most top pixel which is white
        found = False
        for y in range(0,height):
            for x in range(0,width):
                if diffCanny[y,x] == 255: #x and y are inverted for opencv img
                    found = True
                    break
            if found:
                break
        
        return [x,y]
