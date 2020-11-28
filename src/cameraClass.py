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
        
    def __init__(self, name, rotation):
        self.name = name
        self.rotation = rotation
        self.board = self.calibration()
        self.dartThrow = None

    def calibration(self):
        rel_pts = {
            "center": [372,318],
            "left": [221,333],
            "right": [525,301],
            "top": [360,217],
            "bottom": [380,372]
        }

        return Board(rel_pts = rel_pts)
        #self.img_width = 480
        #self.img_height = 720

    def motion_detection(self):

        image_before_link = 'static/jpg/before.jpg'
        image_after_link = 'static/jpg/after.jpg'
        
        t_repeat = 0.05 # Take a picure every t_repeat seconds
        t_max = 0.2 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human

        images = [0,0,0] # indexes: 0: before motion, 1: motion detected?, 2: after motion

        try:
            # define a video capture object 
            vid = cv2.VideoCapture(0) 
            
            while True:
                #1. Step Check for motion
                time.sleep(t_repeat)
                ret, img = vid.read() 
                img = cv2.rotate(img, cv2.ROTATE_180)
                images[0] = images[1]
                images[1] = img
                
                if isinstance(images[0],int):
                    continue

                if Camera.are_images_different(images[0], images[1]):
                    t = t_repeat

                    # Check if motion stops within time
                    while t < t_max:
                        time.sleep(t_repeat)
                        ret, img = vid.read() 
                        img = cv2.rotate(img, cv2.ROTATE_180)
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
                        time.sleep(0.5)
                        images = [0,0,0]
                        continue
            
        except: 
            print('Camera failed to take a picture')
            print("Unexpected error:", sys.exc_info()[0])
            raise

        finally:
            vid.release()
        print('Detected')
        self.dartThrow = dartThrow(image_before_link,image_after_link,self.board)

    # takes one picture and stores it locally and potentially on dropbox
    def take_picture(self,img_name):
        
        # Check if filename is jpg
        if not img_name.endswith('.jpg'):
            img_name = img_name + '.jpg'

        #local output name
        local_output = 'static/jpg/' + img_name

        try:
            # define a video capture object 
            vid = cv2.VideoCapture(0) 
            ret, img = vid.read() 
            img = cv2.rotate(img, cv2.ROTATE_180)
            cv2.imwrite(local_output,img)

        except: 
            print('Camera failed to take a picture')
            print("Unexpected error:", sys.exc_info()[0])
            raise

        finally:
            vid.release()

        #Check if image shall be uploaded to dbx
        config = configparser.ConfigParser()
        config.read('config.ini')

        if int(config['Dropbox']['Enabled']):
            print('Test')
            now = datetime.now()
            dbx_name = '/Images/Session_2020_11_22/' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.jpg'
            dbx_int.img_upload(local_output,dbx_name)

        del config
        return local_output

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

