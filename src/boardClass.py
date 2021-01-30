import numpy as np
import cv2
import json

class Board:

    STD_CENTER = [400, 400]
    PX_PER_MM = 2

    def __init__(self, h = None, src = 0):
        self.h = h
        self.src = src

    @classmethod
    def get_score(cls, std_pos):

            std_polar_pos = cls.carth2pol(std_pos)
            score, multiplier = cls.pol2score(std_polar_pos)
            return score, multiplier

    def rel2std(self, pos_src):
        # [x_src,y_scr,1]
        pos_src = np.append(pos_src,1)

        # [x_dest*t,y_dest*t,t] = H x [x_src,y_src,1]
        pos_dest = np.dot(self.h,pos_src)

        # [x_dest,y_dest] = [x_dest*t,y_dest*t] * (1/t)
        pos_dest = np.dot(pos_dest[:-1],1/pos_dest[-1])

        return pos_dest

    @classmethod
    def carth2pol(cls, std_cath_pos):

        x = std_cath_pos[0] - cls.STD_CENTER[0]
        y = cls.STD_CENTER[1] - std_cath_pos[1]
        r = np.sqrt(x**2 + y**2) / cls.PX_PER_MM
        phi = np.arctan2(y, x)/(2*np.pi)*360 - 90 + 360/20/2  # 0 degree is intersect between 20 and 1

        #arctan is mapping between -180 and 180, but we want an angle between 0 and 360 to simplify later tasks
        phi = phi % 360

        return [r,phi]

    @staticmethod
    def pol2score(std_polar_pos):

        # possible single scores of the dartboard, starting from 6 (phi = 0 for polar coordinate)
        fields = [20,5,12,9,14,11,8,16,7,19,3,17,2,15,10,6,13,4,18,1]

        # map angle to single score
        number = fields[int(std_polar_pos[1]/360*20)]

        # map radius to multipliers or exceptions (bullseye)
        r_in_mm = std_polar_pos[0]

        if r_in_mm < 6.35: 
            number = 25
            multiplier = 2
        elif r_in_mm < 15.9:
            number = 25
            multiplier = 1
        elif r_in_mm < 99 or (r_in_mm > 107 and r_in_mm < 162):
            multiplier = 1
        elif r_in_mm > 99 and r_in_mm < 107:
             multiplier = 3
        elif r_in_mm > 162 and r_in_mm < 170:
             multiplier = 2
        else:
            multiplier = 0

        print(number * multiplier)
        return number, multiplier

    def calibration(self, img, closest_field = 20):
        src = self.get_src_points(img, closest_field = closest_field)
        dest = self.get_dest_points()
        h, status = cv2.findHomography(src, dest)

        cv2.imwrite('static/jpg/calibration_{}.jpg'.format(self.src), img)
        warp_img = cv2.warpPerspective(img, h, (self.STD_CENTER[0]*2,self.STD_CENTER[1]*2))
        warp_img = self.draw_board(warp_img)

        cv2.imwrite('static/jpg/calibration_warp_{}.jpg'.format(self.src), warp_img)

        self.h = h
    
    def manual_calibration(self):

        with open('static/db/src_pts.json') as f:
            data = json.load(f)
        
        data = data['src_' + str(self.src)]
        
        src_pts = []
        for pt in data.values():
            src_pts.append(np.array([pt['x'],pt['y']]))
        
        # get destination points
        dest_pts = []
        r_list = [170]
        r_list = [x * self.PX_PER_MM for x in r_list]

        angle_list = [81, -9, 261, 171]
        for r in r_list:
            for phi in angle_list:
                pt = self.pol2cath(r, phi)
                dest_pts.append(np.array(self.pol2cath(r, phi)))
            
        h, status = cv2.findHomography(np.array(src_pts), np.array(dest_pts))
        self.h = h

        #Testing
        img = cv2.imread('static/jpg/last_{}.jpg'.format(self.src))
        warp_img = cv2.warpPerspective(img, h, (self.STD_CENTER[0]*2,self.STD_CENTER[1]*2))
        warp_img = self.draw_board(warp_img)
        cv2.imwrite('static/jpg/calibration_warp_{}.jpg'.format(self.src), warp_img)

        

    def get_src_points(self, img, closest_field):
        #For now just outer circle
        ellipses = self.get_ellipses(img)
        rel_center = ellipses[0][0]
        mask_black = np.zeros_like(img)
        mask = cv2.ellipse(mask_black,ellipses[1] ,color=(255,255,255), thickness=-1)
        result_circle_complete = cv2.bitwise_and(img,mask)
        lines = self.get_lines(result_circle_complete, rel_center)
        
        src_points = np.empty([len(lines)*2,2])
        src_pos = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            src_points[src_pos,:] = np.array([x2,y2])
            src_points[src_pos+len(lines),:] = np.array([x1,y1])
            src_pos += 1

        # Shift src points depending on pos of camera
        # Convention: clockwise start from point between 20 and 1
        fields = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
        idx = fields.index(closest_field)
        src_points = np.roll(src_points, idx, axis=0)

        for pt in src_points:
            img = cv2.circle(img, (int(pt[0]),int(pt[1])), 2, 255, 2)
        cv2.imwrite('static/jpg/calibration_{}.jpg'.format(self.src), img)

        return src_points

    @classmethod
    def pol2cath(cls, r, phi):
        x0 = cls.STD_CENTER[0]
        y0 = cls.STD_CENTER[1]
        x = r * np.cos(phi * (np.pi/180)) + x0
        y = y0 - r * np.sin(phi * (np.pi/180))
        return [x,y]

    @classmethod
    def get_dest_points(cls):
        dest_points = np.empty([20,2])
        r = 170 * cls.PX_PER_MM # Important -> outer edge of triple ring
        for i in range(20):
            angle = 90 - 180/20 - i * 360 / 20
            dest_points[i] = np.array(cls.pol2cath(r, angle))
        return dest_points

    @classmethod
    def draw_board(cls , img = None):
        if img is None:
            img = np.zeros((cls.STD_CENTER[0] * 2, cls.STD_CENTER[1] * 2))
        r_list = [16, 99, 107, 162, 170]
        r_list = [x * cls.PX_PER_MM for x in r_list]
        for r in r_list:
            cv2.circle(img, (cls.STD_CENTER[0], cls.STD_CENTER[1]), r, (255, 255, 255), 2)
        
        r = 170 * cls.PX_PER_MM
        for phi in range(9,360,18):
            x,y = cls.pol2cath(r, phi)
            cv2.line(img, (cls.STD_CENTER[0], cls.STD_CENTER[1]), (int(x),int(y)), (255, 255, 255), 1)

        return img

    def get_lines(self, img, rel_center):

        gray_img_dark = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bil = cv2.bilateralFilter(gray_img_dark, 8, 70, 70)
        canny = cv2.Canny(bil, 80, 130)
        kernel = np.ones((2,2),np.float32)
        dilation = cv2.dilate(canny,kernel,iterations = 1)

        lines = cv2.HoughLinesP(dilation,  1, 1*np.pi/180, 45, minLineLength=70, maxLineGap=200)
        mask_black = np.zeros_like(img)

        # Line Cleaning
        line_list = []
        angles = []
        min_angle = 3 # min angle between 2 lines
        x_list = []
        y_list = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            p1 = np.array([x1,y1])
            p2 = np.array([x2,y2])
            #cv2.line(gray_img_dark,(x1,y1), (x2, y2),0, 3)

            dist2center = abs(np.cross(p2-p1,rel_center-p1)/np.linalg.norm(p2-p1))
            
            if dist2center < 2:
                angle = np.rad2deg(np.arctan((y2-y1)/(x2-x1)))
                
                if angles == []:
                    angles.append(angle)
                    line_list.append(line)
                else:
                    diff_angles = np.abs(angles - angle)
                    smallest_diff = min(diff_angles)

                    if smallest_diff > min_angle:
                        angles.append(angle)    
                        line_list.append(line)

        if len(line_list) == 10:
            #Sort after angle
            sorted_lines = [x for _,x in sorted(zip(angles,line_list), reverse = False)] # sort clockwise
            return sorted_lines
        else:
            return None

    def get_ellipses(self, img):

        hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # create white image
        img_white = np.zeros_like(img)
        img_white.fill(255)

        #Thresholds
        low_green = np.array([36, 74, 45])
        high_green = np.array([94, 255, 255])
        green_mask = cv2.inRange(hsv_frame, low_green, high_green)
        green = cv2.bitwise_and(img_white, img_white, mask=green_mask)
        
        # Range for lower red
        low_red = np.array([0, 55, 212])
        high_red = np.array([25,117, 255])  
        mask1 = cv2.inRange(hsv_frame, low_red, high_red)

        # Range for upper red
        low_red_2 = np.array([139, 25, 111])
        high_red_2 = np.array([255, 180, 255])
        mask2 = cv2.inRange(hsv_frame, low_red_2, high_red_2)

        red_mask = mask1 + mask2
        red = cv2.bitwise_and(img_white, img_white, mask=red_mask)
        masked_img = cv2.add(red,green)

        gray_img_dark = cv2.cvtColor(masked_img,cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(gray_img_dark, 150, 255, cv2.THRESH_BINARY)
        thresh = cv2.bilateralFilter(thresh, 8, 100, 100)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cntsSorted = sorted(contours, key=cv2.contourArea, reverse=True)

        # Ellipse Cleaning
        ellipses = []
        if len(cntsSorted) > 10:
            cntsSorted = cntsSorted[:10]
        for cnt in cntsSorted:
            center, [width, height], angle = cv2.fitEllipse(cnt)
            width = width - 3
            height = height - 3
            ellipse = center, [width, height], angle

            if cv2.pointPolygonTest(cntsSorted[0],(ellipse[0][0],ellipse[0][1]),False) >= 0:
                ellipses.append(ellipse)

        # get smallest and third smallest ellipses
        sizes = [x[1][0] * x[1][1] for x in ellipses]
        index = np.argsort(sizes)
        ellipses = [ellipses[index[0]], ellipses[index[4]]]
        
        return ellipses



if __name__ == '__main__':
    img = Board.draw_board()
    cv2.imwrite('static/jpg/draw_board.jpg', img)

