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
        #h = cv2.getPerspectiveTransform(self.rel_pts, self.std_pts)
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
        y = self.std_pts["center"][1] - std_cath_pos[1] # because carthesian coordinate system of open vc images is flipped on the y-axis
        rho = np.sqrt(x**2 + y**2)
        phi = np.arctan2(y, x)/(2*np.pi)*360
        print(rho,phi)
        return [rho,phi]

    def std_polar_pos_to_score(self):
        # to be implemented
        return 60