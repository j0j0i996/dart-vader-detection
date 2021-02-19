import cv2
import numpy as np
import datetime
import sys

class dartThrow:

    def __init__(self, img_before, img_after, src):
        self.img_before = img_before
        self.img_after = img_after
        self.src = src

    def get_pos(self):

        success = True
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
        #ret, binary_img = cv2.threshold(diffBlur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        ret, binary_img = cv2.threshold(diffBlur, 16,255,cv2.THRESH_BINARY)
        kernel = np.ones((3,3),np.float32)
        #binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)

        bnd_rect = self.get_bnd_rect(binary_img)

        box_x0, box_y0, box_w, box_h = bnd_rect
        
        # Skeltonize image
        img = binary_img[box_y0:box_y0 + box_h, box_x0:box_x0 + box_w]
        size = np.size(img)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
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

        #lines = cv2.HoughLines(skel,1,np.pi/180, int(h*0.5))
        lines = cv2.HoughLinesP(skel,  1, 1*np.pi/180, 30, minLineLength=int(box_h*0.4), maxLineGap=int(box_h*0.2))

        if lines is None:
            raise Exception('Info: Cam {} did not find dart line \n'.format(self.src), sys.exc_info()[0])
        
        x1, y1, x2, y2 = lines[0][0]

        vy_temp = y2 - y1
        vx_temp = x2 - x1
        vy = vy_temp / (np.sqrt(vy_temp**2 + vx_temp**2))
        vx = vx_temp / (np.sqrt(vy_temp**2 + vx_temp**2))

        if vy == 0:
            raise Exception('Info: Cam {}: No line returned as vy == 0 causes division by 0 \n'.format(self.src), sys.exc_info()[0])

        x0 = x1 + box_x0
        y0 = y1 + box_y0
        top_x = float((-y0 * vx / vy) + x0)
        bottom_x = float((height - y0) * vx / vy + x0)

        p1 = np.array([top_x,0])
        p2 = np.array([bottom_x, height - 1])
        line_pts = [p1, p2]

        # Estimate tip pos by upper intersect of line and box. This is a rough estimation where the tip of the dart is. Is used for priorization of lines
        single_pt = [int((box_y0 - y0) * vx / vy + x0), box_y0]

        """
        #testing
        rec_img = imgAf
        cv2.line(rec_img,(int(top_x),0),(int(bottom_x),height - 1),(255,0,255),1)
        cv2.circle(rec_img,(single_pt[0], single_pt[1]), 2, (200,0,255),2)
        cv2.imwrite("static/jpg/dart_line{}.jpg".format(self.src),rec_img)
        """
        

        t2 = datetime.datetime.now()
        #print('Cam {}: Recognition time: {}'.format(self.src, t2-t1))

        return single_pt, line_pts

    def get_bnd_rect(self, binary_img):

        height, width = binary_img.shape[:2]

        min_size = height * 0.03 * width * 0.03

        # Get contours
        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #Concatenate all cnt points, if contour is large enough
        cnt_pts = None
        for cnt in contours:
            if cv2.contourArea(cnt) > min_size:
                if cnt_pts is None:
                    cnt_pts = cnt
                else:
                    cnt_pts = np.concatenate((cnt_pts,cnt), axis=0)
        
        if cnt_pts is None:
            raise Exception("Info: Cam {} not able to find bounding box \n".format(self.src), sys.exc_info()[0])

        # Create bounding box
        bnd_rect = cv2.boundingRect(cnt_pts)
        
        #testing
        img = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)
        x, y, w, h = bnd_rect
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

        success = True
        return bnd_rect

if __name__ == '__main__':
    #dart = dartThrow('static/jpg/before.jpg', 'static/jpg/after.jpg')
    #p1, p2 = dart.get_position(format = 'line')
    pass