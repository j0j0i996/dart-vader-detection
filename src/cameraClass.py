from datetime import datetime
import configparser
import src.dropbox_integration as dbx_int
import sys
import numpy as np
import cv2
import time
from src.boardClass import *
from src.dartThrowClass import *


config = configparser.ConfigParser()
config.read('config.ini')

class Camera:
        
    def __init__(self, name, rotation, width = 720, height = 480):
        self.name = name
        self.rotation = rotation
        self.board = self.calibration()
        self.width = width
        self.height = height
        self.dartThrow = None
        self.bnds = self.get_camera_bnds() # set image boundaries around dart board dependent on calibration

    def calibration(self):
        rel_pts = {
            "center": [372,318],
            "left": [221,333],
            "right": [525,301],
            "top": [360,217],
            "bottom": [380,372]
        }

        return Board(rel_pts = rel_pts)

    def motion_detection(self):

        image_before_link = 'static/jpg/before.jpg'
        image_after_link = 'static/jpg/after.jpg'
        
        t_repeat = 0.05 # Take a picure every t_repeat seconds
        t_max = 0.2 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human

        images = [0,0,0] # indexes: 0: before motion, 1: motion detected?, 2: after motion

                             
        while True:

            #1. Step Check for motion
            img = self.take_picture()

            images[0] = images[1]
            images[1] = img
            
            if isinstance(images[0],int):
                continue

            if Camera.are_images_different(images[0], images[1]):
                t = t_repeat

                # 2. Step: Check if motion stops within time
                while t < t_max:
                    time.sleep(t_repeat)
                    img = self.take_picture()
                    images[2] = img

                    if Camera.are_images_different(images[1], images[2]):
                        t = t + t_repeat
                        continue
                    else: # Motion stopped
                        break

                if t < t_max: # Motion detected and stopped in time
                    cv2.imwrite(image_before_link,images[0])
                    cv2.imwrite(image_after_link,images[2])
                    break
                else: #Motion detected but was too long
                    time.sleep(1)
                    images = [0,0,0]
                    continue
            
        print('Detected')
        self.dartThrow = dartThrow(image_before_link,image_after_link,self.board)

    # takes one picture and returns it
    def take_picture(self):

        try:
            # define a video capture object 
            cap = cv2.VideoCapture(0)
            
            #set the width and height, and UNSUCCESSFULLY set the exposure time
            #cap.set(3,self.width)
            #cap.set(4,self.height) 

            ret, img = cap.read() 
            img = cv2.rotate(img, cv2.ROTATE_180)  #Rotation important, make dynamic / accessible

            # Crop to dart board
            img = img[self.bnds['top']:self.bnds['bottom'], self.bnds['left']:self.bnds['right']]

        except: 
            print('Camera failed to take a picture')
            print("Unexpected error:", sys.exc_info()[0])
            raise

        finally:
            cap.release()

        return img

    def get_camera_bnds(self):

        extend = 100
        bnds = {'top': max(self.board.rel_pts['top'][1] - extend, 0),
                'left': max(self.board.rel_pts['left'][0] - extend, 0),
                'right': min(self.board.rel_pts['right'][0] + extend, self.width),
                'bottom':min(self.board.rel_pts['bottom'][0] + extend, self.height)
                }

        return bnds

    @staticmethod
    def are_images_different(img1, img2):

        minThres =  80 #Thresholds important - make accessible / dynamic
        maxThres = 1000

        diff = cv2.absdiff(img2,img1)
        diffGray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(diffGray, (5, 5), 0)
        #blur = cv2.bilateralFilter(blur, 9, 75, 75)
        _, thresh = cv2.threshold(blur, 60, 255, 0)

        print(cv2.countNonZero(thresh))

        if (cv2.countNonZero(thresh) > minThres and cv2.countNonZero(thresh) < maxThres):
            return True
        else:
            return False

