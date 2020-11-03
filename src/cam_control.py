from picamera import PiCamera
from time import sleep
from datetime import datetime
from flask import url_for
import os
import re
import dropbox_integration as dbx_int

def take_picture():
    output_path = 'jpg/image.jpg'
    try:
        output_path = 'jpg/image.jpg'
        camera = PiCamera()
        camera.rotation=180
        camera.start_preview()
        camera.capture('static/' + output_path)
    except: 
        print('I could not take a picture')
    finally:
        camera.close()

    dbx_int.picture_upload(output_path)

    return output_path