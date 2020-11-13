from picamera import PiCamera
from datetime import datetime
import configparser
import src.dropbox_integration as dbx_intbefore
import sys
import numpy as np
from src.classes import *

class Camera:
    boardPosition = None
    stdBoardPosition = EllipsisDef()

    def __init__(self, name, rotation):
        self.name = name
        self.rotation = rotation
        self.boardPosition = self.calibration()

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

    @staticmethod
    def calibration():
        pts = np.float32([[0,0],[0,0],[0,0],[0,0],[0,0]])
        return EllipsisDef(pts)


# Testing
# cam1 = Camera('Test', 180)
# print(cam1.__dict__)