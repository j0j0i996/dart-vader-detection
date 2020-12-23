from datetime import datetime
import configparser
import sys
import numpy as np
import cv2
import time
from datetime import datetime
from boardClass import *
from dartThrowClass import *
from videoCapture import *
import db_handler as db
import sqlite3 
import json

class Camera:
        
    def __init__(self, src = 0, width = 640, height = 480, rot = 0):

        self.src = src
        self.cap = VideoStream(src = src, width = width, height = height, rot = rot)

        # get transformation from sql
        h = db.get_trafo(self.src)
    
        if h is not None:
            self.board = Board(h = h)
        else:
            self.board = Board()

        self.dartThrow = None
        self.motionDetected = False
        self.motionRatio = 0

    def calibrate_board(self, closest_field):

        time.sleep(0.5)
        img = self.cap.read()

        #img = cv2.imread('static/jpg/base_img{}.jpg'.format(self.src))

        self.board.calibration(img, closest_field = closest_field)
        h = self.board.h
        db.write_trafo(self.src, h)

    def dart_motion_dect(self):

        self.motionDetected = False  
        self.motionRatio = 0

        cap.start()
        time.sleep(0.5)
        print('Waiting for motion')
        
        #Parameters
        t_rep = 0.16 # Take a picure every t_repeat seconds
        t_max = 0.48 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human
        min_ratio = 0.002 #Thresholds important - make accessible / dynamic - between 0 and 1
        max_ratio = 0.035

        # Get output paths
        config = configparser.ConfigParser()
        config.read('config.ini')
        image_before_link = config['Paths']['image_before_link']   Change to static + src
        image_after_link = config['Paths']['image_after_link']
        del config

        # Initialize loop
        dart_detected = False

        while not dart_detected:

            # Wait for motion
            img_before, img_start_motion, _ = self.wait_for_img_diff_within_thresh(min_ratio, np.inf, t_rep)

            # Wait for motion to stop
            _, img_after, t_motion = self.wait_for_img_diff_within_thresh(0, min_ratio, t_rep, start_image = img_start_motion)

            # Get difference ratio of image befor motion and image after motion
            ratio_final = Camera.get_img_diff_ratio(img_before,img_after)
            
            # Criteria for being a dart:
            # time of motion, maximum object smaller max treshold, size of final object in thresholds
            if t_motion < t_max and ratio_final < max_ratio and ratio_final > min_ratio: # ratio_max < max_ratio and
                dart_detected = True
                cap.stop()
            else:
                print('Motion took too long or object to large')

        print('Dart detected')
        cv2.imwrite(image_before_link, img_before)
        cv2.imwrite(image_after_link, img_after)

        self.dartThrow = dartThrow(image_before_link,image_after_link)

        self.motionDetected = True
        self.motionRatio = ratio_final

    def wait_for_img_diff_within_thresh(self,min_ratio,max_ratio,t_rep, start_image = None):
        img_diff_ratio = -1
        
        # Intialize while loop
        t = 0
        ratio_max = 0
        if start_image is None:
            
            success = False
            while success is False:
                img1, success= self.cap.read()

            time.sleep(t_rep)
        else:
            img1 = start_image

        success = False
        while success is False:
                img2, success = self.cap.read()

        img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

        while img_diff_ratio < min_ratio or img_diff_ratio > max_ratio:
            
            t = t + t_rep
            time.sleep(t_rep)
            img1 = img2.copy()

            success = False
            while success == False:
                img2, success = self.cap.read()

            # Get ratio of difference pixels between first and second image
            img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

        return img1, img2, t

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

