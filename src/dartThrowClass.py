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

        diff = cv2.absdiff(img_bf, img_af)
        height, width = diff.shape[:2]

        # transform to gray scale
        diffGray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        # add blur
        kernel = np.ones((5,5),np.float32)/25
        diffBlur = cv2.filter2D(diffGray,-1,kernel)

        # First step: Find dart -> Use contours to find bounding box around dart
        # Find contours
        diffCnts = diffBlur.copy()
        ret, thresh = cv2.threshold(diffCnts, 35, 255, 0) #Important threshold
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        diffCnts = cv2.cvtColor(diffBlur, cv2.COLOR_GRAY2BGR)
        img = cv2.drawContours(diffCnts, contours, -1, (255,255,255), 2)

        bnd_left, bnd_top = width, height
        bnd_right = bnd_bottom = 0

        # computes the bounding box for all contours
        for contour in contours:
            (x,y,w,h) = cv2.boundingRect(contour)
            bnd_left, bnd_right = min(x, bnd_left), max(x+w, bnd_right)
            bnd_top, bnd_bottom = min(y, bnd_top), max(y+h, bnd_bottom)

        #For testing
        if bnd_right - bnd_left > 0 and bnd_bottom - bnd_top > 0:
            cv2.rectangle(diffCnts, (bnd_left, bnd_top), (bnd_right, bnd_bottom), (255, 0, 0), 2)
        
        #2. Step: Sensible feature detection inside the detecting bounding box
        inc_heigth = 50 #Important threshold
        diffFeat = diffBlur.copy()[bnd_top-inc_heigth:bnd_bottom,bnd_left:bnd_right]
        
        features = cv2.goodFeaturesToTrack(diffFeat, 640, 0.0008, 1, mask=None, blockSize=3, useHarrisDetector=1, k=0.06)

        # Find most top feature -> is dart
        min_y = height
        corr_x = None  # Corresponding coordinate
        # Find most top feature
        for feature in features:
            x,y = feature.ravel()
            if y < min_y:
                min_y = y
                corr_x = x

        x_out, y_out = bnd_left + corr_x, bnd_top-inc_heigth+min_y

        #For testing
        cv2.circle(diffFeat,(corr_x,min_y),5,100,-1)

        #For testing
        for feature in features:
            x,y = feature.ravel()
            cv2.circle(diffFeat,(x,y),3,255,-1)

        path_out = 'static/jpg/'
        cv2.drawMarker(img_af, (int(x_out), int(y_out)), color=(0, 76, 252))

        cv2.imwrite(path_out + 'rec_dart.jpg',img_af)
        cv2.imwrite(path_out + 'contours.jpg',diffCnts)
        cv2.imwrite(path_out + 'features.jpg',diffFeat)
        print(x_out, y_out)

        return [x_out, y_out]
