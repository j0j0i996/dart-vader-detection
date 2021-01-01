from datetime import datetime
import numpy as np
import cv2
import time
from datetime import datetime
import src.boardClass as boardClass
import src.dartThrowClass as dartThrowClass
import src.videoCapture as videoCapture
import src.db_handler as db
import src.dropbox_integration as dbx
import sqlite3 
import json

#testing
img_count = 55

class Camera:
        
    def __init__(self, src = 0, width = 640, height = 480, rot = 0):

        self.src = src
        self.cap = videoCapture.VideoStream(src = src, width = width, height = height, rot = rot)
        self.img_count = 0
        
        # get transformation from sql
        h = db.get_trafo(self.src)
    
        if h is not None:
            self.board = boardClass.Board(h = h, src = self.src)
        else:
            self.board = boardClass.Board(src = self.src)

        self.dartThrow = None
        self.stopMotionThread = False
        self.motionRatio = 0
        self.img_before = None
        self.img_after = None

    def start(self):
        self.cap.start()

    def stop(self):
        self.cap.stop()

    def take_pic(self):
        if self.cap.running == False:
            self.start()

        max_tries = 10
        for _ in range(max_tries):
            img, success = self.cap.read()
            if success:
                break

        if success == False:
            raise Exception('Problem reading camera')
            return

        cv2.imwrite('static/jpg/last_{}.jpg'.format(self.src), img)

        return img

    def calibrate_board(self, closest_field):

        img = self.take_pic()

        self.board.calibration(img, closest_field = closest_field)
        h = self.board.h
        db.write_trafo(self.src, h)

        self.stop()

    def manual_calibration(self):
        self.board.manual_calibration()
        h = self.board.h
        print(h)
        db.write_trafo(self.src, h)

    def dart_motion_dect(self):
        
        self.stopMotionThread = False
        self.motionRatio = 0

        print('Waiting for motion')
        
        #Parameters
        t_rep = 0.16 # Take a picure every t_repeat seconds
        t_max = 0.48 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human
        min_ratio = 0.002 #Thresholds important - make accessible / dynamic - between 0 and 1
        max_ratio = 0.03

        #Testing
        image_before_link = 'static/jpg/before_{}.jpg'.format(self.src)
        image_after_link = 'static/jpg/after_{}.jpg'.format(self.src)

        
        while self.stopMotionThread == False:

            # Wait for motion
            img_before, img_start_motion, _ = self.wait_for_img_diff_within_thresh(min_ratio, np.inf, t_rep)

            # Wait for motion to stop
            _, img_after, t_motion = self.wait_for_img_diff_within_thresh(0, min_ratio, t_rep, start_image = img_start_motion)

            # Get difference ratio of image befor motion and image after motion
            ratio_final = Camera.get_img_diff_ratio(img_before,img_after)
            
            # Criteria for being a dart:
            # time of motion, maximum object smaller max treshold, size of final object in thresholds
            if t_motion < t_max and ratio_final < max_ratio and ratio_final > min_ratio: # ratio_max < max_ratio and
                
                #Testing
                #cv2.imwrite(image_before_link, img_before)
                #cv2.imwrite(image_after_link, img_after)
                #global img_count
                #dbx.img_upload(image_before_link,'/Images/Session_2020_30_12/before_{}_{}.jpg'.format(self.src, img_count))
                #dbx.img_upload(image_after_link,'/Images/Session_2020_30_12/after_{}_{}.jpg'.format(self.src, img_count))
                #img_count = img_count + 1

                self.dartThrow = dartThrowClass.dartThrow(img_before,img_after, self.src)
                self.motionRatio = ratio_final
                self.stopMotionThread = True
                return
            else:
                self.stopMotionThread = True
                self.motionRatio = False
                self.dartThrow = None
                return

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

        return ratio

