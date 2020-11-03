from picamera import PiCamera
from time import sleep
from datetime import datetime
from flask import url_for
import os
import re
import src.dropbox_integration as dbx_int

def take_picture():
    output_path = 'jpg/image.jpg'
    try:
        camera = PiCamera()
        camera.rotation=180
        camera.start_preview()
        camera.capture('static/' + output_path)
    except: 
        print('Camera failed to take a picture')
    finally:
        camera.close()

    dbx_int.picture_upload(output_path)

    return output_path