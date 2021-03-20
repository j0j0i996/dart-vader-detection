import os
import json
import sys
import src.cameraClass as camCls
import src.camMngClass as camMng
#import src.dectHandler as dectHandler
import atexit
import asyncio
import websockets
import cv2
import time
import logging
from flask import Flask
from flask_socketio import SocketIO, send, emit

SOCKET_SERVER_URL = '192.168.0.10'
PORT = 3000

logger = logging.getLogger('Logging')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logger.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

cam_manager = camMng.camManager(local_video=False)

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app)

def exit_handler():
    cam_manager.stop_cams()

@sio.on('connect')
def connect():
    print('connected')

@sio.on('echo')
def echo(message):
    print(message)
    #emit('echoresponse', {'data': message['data']})

@sio.on('start_dect')
def start_dect(msg):
    if cam_manager.dect_loop_active == False:
        sio.start_background_task(target = cam_manager.dect_loop(sio))

@sio.on('end_dect')
def end_dect(msg):
    cam_manager.dect_loop_active = False

@sio.on('disconnect')
def disconnect():
    print('disconnected')

if __name__ == '__main__':

    logger.info('Program start')
    atexit.register(exit_handler)

    cam_manager.start_cams()

    sio.run(app, host=SOCKET_SERVER_URL, port=PORT)

    #cam_manager.take_pic()
    #cam_manager.manual_calibration()

    cam_manager.stop_cams()
