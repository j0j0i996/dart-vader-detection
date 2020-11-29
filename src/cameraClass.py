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
            "center": [335,323],
            "left": [202,334],
            "right": [469,308],
            "top": [322,231],
            "bottom": [340,372]
        }
        return rel_pts

    def motion_detection(self):
        
        t_repeat = 0.025 # Take a picure every t_repeat seconds
        t_max = 0.1 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human

        images = [0,0,0] # indexes: 0: before motion, 1: motion detected?, 2: after motion

        minRatio = 0.00005 #Thresholds important - make accessible / dynamic - between 0 and 1
        maxRatio = 0.009

        wait_for_two_equal_imgs = True

        while True:

            #1. Step Check for motion
            t = 0
            time.sleep(t_repeat)
            img = self.take_picture()
            images[0] = images[1]
            images[1] = img
            
            if isinstance(images[0],int):
                continue

            # Get ratio of differenct pixels between first and second image
            img_diff_ratio = Camera.get_img_diff_ratio(images[0], images[1])
            
            if wait_for_two_equal_imgs and img_diff_ratio < minRatio:
                wait_for_two_equal_imgs = False
                continue

            if img_diff_ratio < minRatio:
                # No object / too small
                continue
            elif img_diff_ratio > maxRatio:
                # Object too large
                print('Object too large')

                # Reset images
                images = [0,0,0] 
                wait_for_two_equal_imgs = True
                continue
            else:
                # Motion detected and no large object
                # 2. Step: Check if motion stops within time
                while t < t_max:
                    t = t + t_repeat
                    time.sleep(t_repeat)

                    img = self.take_picture()
                    images[2] = img
                    
                    #Check if there is still movement
                    img_diff_ratio = Camera.get_img_diff_ratio(images[1], images[2])
                    if img_diff_ratio > minRatio: # Check if motion is still ongoing
                        t = t + t_repeat
                        images[1] = images[2]
                        continue
                    else: # Motion stopped
                        break
                else:
                    print('Motion took too long')
                    
                    # Reset images
                    images = [0,0,0]
                    wait_for_two_equal_imgs = True
                    continue

                # Final check if object size is plausible for a Dart
                img_diff_ratio = Camera.get_img_diff_ratio(images[0], images[2])
                if img_diff_ratio > minRatio and img_diff_ratio < maxRatio:
                    print('Detected')
                    # Get image output path
                    config = configparser.ConfigParser()
                    config.read('config.ini')
                    image_before_link = config['Paths']['image_before_link']
                    image_after_link = config['Paths']['image_after_link']
                    del config

                    cv2.imwrite(image_before_link, images[0])
                    cv2.imwrite(image_after_link, images[2])
                    break

                else:
                    continue

        self.dartThrow = dartThrow(image_before_link,image_after_link,self.board)

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

