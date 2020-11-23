from datetime import datetime
import configparser
import src.dropbox_integration as dbx_int
import sys
import numpy as np
import cv2
from src.boardClass import *
from src.dartThrowClass import *

# Check if we are working on raspberry pi. If not, PiCamera cannot be used.
# This can be set in config.ini
config = configparser.ConfigParser()
config.read('config.ini')
if int(config['Development']['OnRaspberry']):
    from picamera import PiCamera 

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
        # Fake implementation to test other functions
        image_before_link = 'static/jpg/before.jpg'
        image_after_link = 'static/jpg/after.jpg'
        self.dartThrow = dartThrow(image_before_link,image_after_link,self.board)

    # takes one picture and stores it locally and potentially on dropbox
    def take_picture(self,img_name):
        
        # Check if filename is jpg
        if not img_name.endswith('.jpg'):
            img_name = img_name + '.jpg'

        #local output name
        local_output = 'static/jpg/' + img_name

        try:
            PiCam = PiCamera()
            PiCam.rotation = self.rotation
            PiCam.start_preview()
            PiCam.capture(local_output)

        except: 
            print('Camera failed to take a picture')
            print("Unexpected error:", sys.exc_info()[0])
            raise

        finally:
            PiCam.close()

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


# Testing
cam1 = Camera('Test', 180)
print(cam1.__dict__)