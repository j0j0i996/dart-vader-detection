from datetime import datetime
import configparser
import src.dropbox_integration as dbx_int
import sys
import numpy as np
import cv2
import time
from datetime import datetime
from src.boardClass import *
from src.dartThrowClass import *
from src.videoCapture import *
import sqlite3 

conn = sqlite3.connect('camera.db')
c = conn.cursor()

class Camera:
        
    def __init__(self, src = 0, closest_field = 20, width = 640, height = 480, rot = 0):

        self.cap = VideoStream(src = src, width = width, height = height, rot = rot)
        #self.cap.start()
        #time.sleep(2)
        #img = self.cap.read()
        #self.cap.stop()

        #Check if data is available in SQL
        #self.board = Board(h = ...self.base_img)

        self.base_img = 'static/jpg/base_img' + str(src) + '.jpg'
        self.board = Board(closest_field = closest_field, base_img_path = self.base_img)
        self.dartThrow = None


    def dart_motion_dect(self):
        
        self.cap.start()
        print('Waiting for motion')
        
        #Parameters
        t_rep = 0.16 # Take a picure every t_repeat seconds
        t_max = 0.48 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human
        min_ratio = 0.002 #Thresholds important - make accessible / dynamic - between 0 and 1
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
            img1 = self.cap.read()
            time.sleep(t_rep)
        else:
            img1 = start_image
        
        img2 = self.cap.read()
        img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

        while img_diff_ratio < min_ratio or img_diff_ratio > max_ratio:
            
            t = t + t_rep
            time.sleep(t_rep)
            img1 = img2
            img2 = self.cap.read()

            # Get ratio of difference pixels between first and second image
            img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

            ratio_max = max(ratio_max, img_diff_ratio)

        return img1, img2, ratio_max, t

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
        if ratio > 0.0001:
            print(ratio)

        return ratio

