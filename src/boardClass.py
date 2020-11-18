import numpy as np
import cv2

class Board:

    def __init__(self, rel_pts = None):
        if rel_pts is None:
            self.rel_pts = []
        else:
            self.rel_pts = rel_pts
        
        self.std_pts = self.get_std_pts()

        self.h = self.get_homography_matrix()

    def __repr__(self):
        return 'Relative board position: \n{} \nStandard board position: \n{} \nHomography matrix \n {} \n'\
            .format(self.rel_pts, self.std_pts, self.h)


    def get_homography_matrix(self):
        h, status = cv2.findHomography(self.rel_pts, self.std_pts)
        #h = cv2.getPerspectiveTransform(self.rel_pts, self.std_pts)
        return h

    def get_std_pts(self):
        # Conceptual implementation
        width = 1000
        height = 1000
        center = [width/2,height/2]; left = [width/4,height/2]
        right = [width/4*3,height/2]; top = [width/2,height/4]
        bottom = [width/2,height/4*3]
        return np.float32([center, left, top, right, bottom])

    def rel_carth_pos_to_std_carth_pos(self, pos_src):
        # [x1,y1,1] = H x [x2,y2,1]
        pos_src = np.append(pos_src,1)
        #pos_src = np.float32([[pos_src],[pos_src]])
        print('vector in {}'.format(pos_src))
        pos_dest = np.dot(self.h,pos_src)
        #pos_dest = cv2.perspectiveTransform(pos_src,self.h)
        print('vector out {}'.format(pos_dest))
        pos_dest = np.dot(pos_dest[:-1],1/pos_dest[-1])
        print('vector out {}'.format(pos_dest))
        return pos_dest

    def std_carth_pos_to_std_polar_pos(self):
        # to be implemented
        return

    def std_polar_pos_to_score(self):
        # to be implemented
        return 60