from datetime import datetime
import configparser
import src.dropbox_integration as dbx_intbefore
import sys
import numpy as np
from src.boardClass import *
from src.dartThrowClass import *

# Check if we are working on raspberry pi. If not, PiCamera cannot be used.
# This can be set in config.ini
config = configparser.ConfigParser()
config.read('config.ini')
if int(config['Development']['OnRaspberry']):
    from picamera import PiCamera 

class Camera:
    stdBoardPos = None

    def __init__(self, name, rotation):
        self.name = name
        self.rotation = rotation
        self.boardPosition = self.calibration()
        self.dartThrow = None
        self.relBoardPos = None

    @staticmethod
    def calibration():
        pts = np.float32([[0,0],[0,0],[0,0],[0,0],[0,0]])
        return Board(pts)
    
    def motion_detection(self)
        # Fake implementation to test other functions
        image_before_link = 'static/jpg/before.jpg'
        image_after_link = 'static/jpg/before.jpg'
        self.dartThrow = dartThrow(image_before_link,image_after_link)

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
            dbx_name = '/Images/' + now.strftime("%Y_%m_%d_%H_%M_%S") + img_name
            dbx_int.img_upload(local_output,dbx_name)

        del config
        return local_output


# Testing
cam1 = Camera('Test', 180)
print(cam1.__dict__)