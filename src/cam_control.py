from picamera import PiCamera
from time import sleep
from datetime import datetime
from flask import url_for
import os
import re

def take_picture():
    camera = PiCamera()
    camera.rotation=180
    # Camera warm-up time
    try:
        camera.start_preview()
        # output filename to be one counter higher than the latest image so far (if latest image: 'image4.jpg' -> next image 'image5.jpg')
        now = datetime.now()
        output_path = 'images/image' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.jpg'
        camera.capture('static/' + output_path)

    finally:
        camera.close()

    return output_path