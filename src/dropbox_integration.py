import dropbox
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Login to dropbox
dbx = dropbox.Dropbox(config['Dropbox']['AccessToken'])

del config