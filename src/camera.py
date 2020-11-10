from picamera import PiCamera
from datetime import datetime
import configparser
import src.dropbox_integration as dbx_intbefore
import sys

def take_picture(img_name):

    # Check if filename is jpg
    if not img_name.endswith('.jpg'):
        img_name = img_name + '.jpg'

    #local output name
    local_output = 'static/jpg/' + img_name

    try:
        camera = PiCamera()
        camera.rotation=180
        camera.start_preview()
        camera.capture(local_output)

    except: 
        print('Camera failed to take a picture')
        print("Unexpected error:", sys.exc_info()[0])
        raise

    finally:
        camera.close()

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