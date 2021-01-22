import cv2
import numpy as np
import datetime

class dartThrow:

    def __init__(self, img_before, img_after, src):
        self.img_before = img_before
        self.img_after = img_after
        self.src = src

    def __repr__(self):
        return 'RelCarth Pos: {} \n\nStd Carth Pos: {} \n'\
            .format(self.rel_carth_pos, self.std_carth_pos)

    def get_pos(self):

        t1 = datetime.datetime.now()

        imgBf = self.img_before
        imgAf = self.img_after

        diff = cv2.absdiff(imgBf, imgAf)
        height, width = diff.shape[:2]

         # transform to gray scale
        diff_gray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
        diffBlur = diff_gray

        # add blur
        kernel = np.ones((3,3),np.float32)/9
        diffBlur = cv2.filter2D(diff_gray,-1,kernel)
    
        # Get binary image
        ret, binary_img = cv2.threshold(diffBlur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        # Skeltonize image
        img = binary_img
        size = np.size(img)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS ,(5,5))
        skel = np.zeros(img.shape,np.uint8)
        done = False
        while( not done):
            eroded = cv2.erode(img,element)
            temp = cv2.dilate(eroded,element)
            temp = cv2.subtract(img,temp)
            skel = cv2.bitwise_or(skel,temp)
            img = eroded.copy()
        
            zeros = size - cv2.countNonZero(img)
            if zeros==size:
                done = True

        # get coordinates of white pixels 
        skel_pts = np.argwhere(skel == 255)

        # filter pixels - we don't want to consider the flight
        dart_height = skel_pts[-1][0]-skel_pts[0][0]
        max_y = skel_pts[0][0] + 0.6 * dart_height 
        skel_pts = skel_pts[skel_pts[:,0] < max_y]
        skel_pts = np.flip(skel_pts, axis=1)


        #fit line
        [vx, vy, x0, y0] = cv2.fitLine(skel_pts, cv2.DIST_HUBER, 0, 0.1, 0.1) #dist_L1 cost function is p(r)=r, dist_L2 cost function is p(r)=r^2
        line = [vx, vy, x0, y0]
        top_x = float((-y0 * vx / vy) + x0)
        bottom_x = float((height - y0) * vx / vy + x0)

        p1 = np.array([top_x,0])
        p2 = np.array([bottom_x, height - 1])
        line_pts = [p1, p2]

        # get most top pt. This is a rough estimation where the tip of the dart is. Is used for priorization of lines
        top_pt = skel_pts[0]

        #testing
        #rec_img = imgAf
        #cv2.line(rec_img,(int(top_x),0),(int(bottom_x),height - 1),(255,0,255),1)

        #cv2.circle(rec_img,(top_pt[0], top_pt[1]), 2, (200,0,255),2)

        #cv2.imwrite("static/jpg/dart_line{}.jpg".format(self.src),rec_img)

        t2 = datetime.datetime.now()

        print('Cam {}: Recognition time: {}'.format(self.src, t2-t1))

        return top_pt, line_pts

if __name__ == '__main__':
    dart = dartThrow('static/jpg/before.jpg', 'static/jpg/after.jpg')
    p1, p2 = dart.get_position(format = 'line')
    print(p1)
    print(p2)