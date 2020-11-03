from picamera import PiCamera
from time import sleep
from datetime import datetime
from flask import url_for
import os
import re
import src.dropbox_integration as dbx_int

def take_picture():
    output_path = 'static/jpg/image.jpg'
    try:
        camera = PiCamera()
        camera.rotation=180
        camera.start_preview()
        camera.capture(output_path)
    except: 
        print('Camera failed to take a picture')
    finally:
        camera.close()

    dbx_int.file_upload(output_path)

    return output_path