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
from flask import Flask, request, send_from_directory, send_file, safe_join
from flask_socketio import SocketIO, send, emit

SOCKET_SERVER_URL = '192.168.0.10'
PORT = 3000

cam_manager = camMng.camManager()

app = Flask(__name__)
app.config["IMAGES"] = "static/jpg"
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
    cam_manager.dect_loop_active = False
    print('disconnected')

@app.route('/echo/<msg>', methods=['GET'])
def echo(msg):
    print(msg)
    return json.dumps( msg )

@app.route('/calibration', methods=['PATCH'])
def calibraton():
    closest_field = int(request.args.get('closest_field'))
    cam_idx = int(request.args.get('cam_idx'))
    success = cam_manager.cam_list[cam_idx].auto_calibration(closest_field)
    return str(success)

@app.route('/get-cal-img/<int:cam_idx>', methods=['GET'])
def get_last_img(cam_idx):
    src = cam_manager.cam_list[cam_idx].src
    filename = 'calibration_{}.jpg'.format(src)
    safe_path = safe_join(app.config["IMAGES"], filename)

    try: 
        return send_file(safe_path, as_attachment=False)
    except FileNotFoundError:
        abort(404)

@app.route('/get-last-img/<int:cam_idx>', methods=['GET'])
def get_cal_img(cam_idx):
    src = cam_manager.cam_list[cam_idx].src
    filename = 'last_{}.jpg'.format(src)
    safe_path = safe_join(app.config["IMAGES"], filename)

    try: 
        return send_file(safe_path, as_attachment=False)
    except FileNotFoundError:
        abort(404)

atexit.register(exit_handler)
cam_manager.start_cams()
sio.run(app, async)

if __name__ == '__main__':
    pass
    #atexit.register(exit_handler)
    #print('hi')
    #cam_manager.start_cams()
    #sio.run(app, host=SOCKET_SERVER_URL, port=PORT)

    """
    for i in range(20):
        cam_manager.cam_list[0].take_pic('static/jpg/chess/img_0_2_{}.jpg'.format(i))
        cam_manager.cam_list[1].take_pic('static/jpg/chess/img_2_2_{}.jpg'.format(i))
        cam_manager.cam_list[2].take_pic('static/jpg/chess/img_4_2_{}.jpg'.format(i))
        time.sleep(1)
    """

    #cam_manager.cam_list[0].auto_calibration(18)
    #cam_manager.cam_list[1].auto_calibration(11)
    #cam_manager.cam_list[2].auto_calibration(2)
    #cam_manager.manual_calibration()

    #cam_manager.stop_cams()
