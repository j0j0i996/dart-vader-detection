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
        
        src_pts = np.float32([self.rel_pts["center"], self.rel_pts["left"], self.rel_pts["right"], self.rel_pts["top"], self.rel_pts["bottom"]])
        dest_pts = np.float32([self.std_pts["center"], self.std_pts["left"], self.std_pts["right"], self.std_pts["top"], self.std_pts["bottom"]])

        h, status = cv2.findHomography(src_pts, dest_pts)
        
        return h

    def get_std_pts(self):
        # Conceptual implementation
        width = 1000
        height = 1000
        std_pts = {
            "center": [width/2,height/2], 
            "left": [width/4,height/2],
            "right": [width/4*3,height/2],
            "top": [width/2,height/4],
            "bottom": [width/2,height/4*3]
            }
        return std_pts

    def get_score(self, rel_carth_pos):
            std_carth_pos = self.rel_carth_pos_to_std_carth_pos(rel_carth_pos)
            std_polar_pos = self.std_carth_pos_to_std_polar_pos(std_carth_pos)
            score = self.std_polar_pos_to_score(std_polar_pos)
            return score

    def rel_carth_pos_to_std_carth_pos(self, pos_src):
        # [x_src,y_scr,1]
        pos_src = np.append(pos_src,1)

        # [x_dest*t,y_dest*t,t] = H x [x_src,y_src,1]
        pos_dest = np.dot(self.h,pos_src)

        # [x_dest,y_dest] = [x_dest*t,y_dest*t] * (1/t)
        pos_dest = np.dot(pos_dest[:-1],1/pos_dest[-1])

        return pos_dest

    def std_carth_pos_to_std_polar_pos(self, std_cath_pos):
        x = std_cath_pos[0] - self.std_pts["center"][0]
        y = self.std_pts["center"][1] - std_cath_pos[1]
        rho = np.sqrt(x**2 + y**2)
        phi = np.arctan2(y, x)/(2*np.pi)*360 + 360/20/2  # 0 degree is intersect between 6 and 10

        #arctan is mapping between -180 and 180, but we want an angle between 0 and 360 to simplify later tasks
        phi = phi % 360

        return [rho,phi]

    def std_polar_pos_to_score(self, std_polar_pos):
        # possible single scores of the dartboard, starting from 6 (phi = 0 for polar coordinate)
        fields = [6,13,4,18,1,20,5,12,9,14,11,8,16,7,19,3,17,2,15,10]

        # map angle to single score
        single_score = fields[int(std_polar_pos[1]/360*20)]

        # map radius to multipliers or exceptions (bullseye)
        r_in_mm = std_polar_pos[0]/np.abs(self.std_pts['top'][1]-self.std_pts['center'][1])*170

        if r_in_mm < 6.35: 
            score = 50
        elif r_in_mm < 15.9:
            score = 25
        elif r_in_mm < 99 or (r_in_mm > 107 and r_in_mm < 162):
            score = single_score
        elif r_in_mm > 99 and r_in_mm < 107:
             score = 3 * single_score
        elif r_in_mm > 162 and r_in_mm < 170:
             score = 2 * single_score
        else:
            score = 0

        print(score)
        return score