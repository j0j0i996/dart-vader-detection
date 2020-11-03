import dropbox
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')

# Login to dropbox
dbx = dropbox.Dropbox(config['Dropbox']['AccessToken'])

del config


def file_upload(file_from):

    #add session name

    now = datetime.now()
    file_to = '/image' + now.strftime("%Y_%m_%d_%H_%M_%S") + '.jpg'
    
    with open(file_from, 'rb') as f:
        dbx.files_upload(f.read(), file_to)