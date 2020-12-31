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


if __name__ == '__main__':
    img_upload('static/jpg/after_0.jpg','/Images/Session_2020_30_12/before_{}_{}.jpg'.format(0,1))