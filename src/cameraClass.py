from datetime import datetime
import configparser
import src.dropbox_integration as dbx_int
import sys
import numpy as np
import cv2
import time
from src.boardClass import *
from src.dartThrowClass import *

class Camera:
        
    def __init__(self, name, rotation, width = 640, height = 480):
        self.name = name
        self.rotation = rotation
        self.width = width
        self.height = height
        self.rel_pts = self.calibration()
        self.bnds = self.set_camera_bnds()
        self.board = Board(rel_pts = self.rel_pts)
        self.dartThrow = None
        #self.dartThrow = dartThrow('test','test',self.board)

    def calibration(self):

        img = self.take_picture()
        cv2.imwrite('static/jpg/calibration.jpg', img)

        rel_pts = {
            "center": [313,299],
            "left": [93,294],
            "right": [536,304],
            "top": [304,164],
            "bottom": [317,367]
        }
        return rel_pts

    def dart_motion_dect(self):

        print('Waiting for motion')
        
        #Parameters
        t_rep = 0.025 # Take a picure every t_repeat seconds
        t_max = 0.1 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human
        min_ratio = 0.0005 #Thresholds important - make accessible / dynamic - between 0 and 1
        max_ratio = 0.035

        # Get output paths
        config = configparser.ConfigParser()
        config.read('config.ini')
        image_before_link = config['Paths']['image_before_link']
        image_after_link = config['Paths']['image_after_link']
        del config

        # Initialize loop
        dart_detected = False

        while not dart_detected:

            # Wait for motion
            img_before, img_start_motion, ratio_start_motion, _ = self.wait_for_img_diff_within_thresh(min_ratio, np.inf, t_rep)

            # Wait for motion to stop
            _, img_after, ratio_max_motion, t_motion = self.wait_for_img_diff_within_thresh(0, min_ratio, t_rep, start_image = img_start_motion)

            # Get maximum difference of motion
            ratio_max = max(ratio_start_motion, ratio_max_motion)

            # Get difference ratio of image befor motion and image after motion
            ratio_final = Camera.get_img_diff_ratio(img_before,img_after)
            
            # Criteria for being a dart:
            # time of motion, maximum object smaller max treshold, size of final object in thresholds
            if t_motion < t_max and ratio_max < max_ratio and \
                ratio_final < max_ratio and ratio_final > min_ratio:
                dart_detected = True
            else:
                print('Motion took too long or object to large')

        print('Dart detected')
        cv2.imwrite(image_before_link, img_before)
        cv2.imwrite(image_after_link, img_after)

        self.dartThrow = dartThrow(image_before_link,image_after_link,self.board)

    def wait_for_img_diff_within_thresh(self,min_ratio,max_ratio,t_rep, start_image = None):
        img_diff_ratio = -1
        
        # Intialize while loop
        t = 0
        ratio_max = 0
        if start_image is None:
            img1 = self.take_picture()
            time.sleep(t_rep)
        else:
            img1 = start_image
        
        img2 = self.take_picture()
        img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

        while img_diff_ratio < min_ratio or img_diff_ratio > max_ratio:
            
            t = t + t_rep
            time.sleep(t_rep)
            img1 = img2
            img2 = self.take_picture()

            # Get ratio of difference pixels between first and second image
            img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

            ratio_max = max(ratio_max, img_diff_ratio)

        return img1, img2, ratio_max, t

    # takes one picture and returns it
    def take_picture(self):

        try:
            # define a video capture object 
            cap = cv2.VideoCapture(0)
            
            #set the width and height
            cap.set(3,self.width)
            cap.set(4,self.height) 

            ret, img = cap.read() 
            img = cv2.rotate(img, cv2.ROTATE_180)  #Rotation important, make dynamic / accessible

            # Crop image around dart board
            if hasattr(self,'bnds'):
                img = img[self.bnds['top']:self.bnds['bottom'], self.bnds['left']:self.bnds['right']]

        except: 
            print('Camera failed to take a picture')
            print("Unexpected error:", sys.exc_info()[0])
            raise

        finally:
            cap.release()

        return img

    def set_camera_bnds(self):

        extend = 100
        bnds = {'top': max(self.rel_pts['top'][1] - extend, 0),
                'left': max(self.rel_pts['left'][0] - extend, 0),
                'right': min(self.rel_pts['right'][0] + extend, self.width),
                'bottom':min(self.rel_pts['bottom'][0] + extend, self.height)
                }

        # adjust relative points
        shift = [bnds['left'],bnds['top']]
        for k,v in self.rel_pts.items():
            self.rel_pts[k] = [a - b for a, b in zip(self.rel_pts[k], shift)]

        return bnds

    @staticmethod
    def get_img_diff_ratio(img1, img2):

        diff = cv2.absdiff(img2,img1)
        diff = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        diff = cv2.GaussianBlur(diff, (5, 5), 0)
        #blur = cv2.bilateralFilter(blur, 9, 75, 75)
        _, thresh = cv2.threshold(diff, 60, 255, 0)

        white_pixels = cv2.countNonZero(thresh)
        total_pixels = diff.size
        ratio = white_pixels/total_pixels
        if ratio > 0:
            print(ratio)

        return ratio

