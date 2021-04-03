import os
import json
import sys
import src.cameraClass as camCls
import src.camMngClass as camMng
import atexit
import asyncio
import websockets
import cv2
import time
import logging
from flask import Flask
from flask import request
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

cam_manager = camMng.camManager()

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
    emit('echoresponse', {'data': message['data']})

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

@app.route('/echo/<msg>', methods=['GET'])
def echo(msg):
    return (msg)

@app.route('/calibration', methods=['PATCH'])
def calibraton():
    closest_field = request.args.get('closest_field')
    cam_idx = request.args.get('cam_idx')
    success = cam_manager.cam_list[int(cam_idx)].auto_calibration(int(closest_field))
    return str(success)

if __name__ == '__main__':

    logger.info('Program start')
    atexit.register(exit_handler)

    cam_manager.start_cams()

    #sio.run(app, host=SOCKET_SERVER_URL, port=PORT)

    #cam_manager.take_pic()

    cam_manager.cam_list[0].auto_calibration(18)
    #cam_manager.cam_list[1].auto_calibration(11)
    #cam_manager.cam_list[2].auto_calibration(2)
    #cam_manager.manual_calibration()

    cam_manager.stop_cams()
