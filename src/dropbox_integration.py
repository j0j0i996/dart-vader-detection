import dropbox
import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini')

# Login to dropbox
dbx = dropbox.Dropbox(config['Dropbox']['AccessToken'])

del config

def img_upload(file_from, file_to):
            
    with open(file_from, 'rb') as f:
        dbx.files_upload(f.read(), file_to)