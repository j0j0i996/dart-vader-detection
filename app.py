from flask import Flask, render_template
import os
import json
import cv2
import sys
import src.cameraClass as camCls
import src.camMngClass as camMng
import atexit
import time

app = Flask(__name__)

camManager = camMng.camManager()

def exit_handler():
    camManager.stop_cams()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wait_throw')
def get_score():
    score, multiplier, nextPlayer = camManager.detection()
    return json.dumps({'score': score, 'multiplier': multiplier, 'nextPlayer': nextPlayer})

if __name__ == '__main__':
    atexit.register(exit_handler)
    
    camManager.start_cams()

    #camManager.take_pic()

    camManager.manual_calibration()
    #camManager.cam_list[0].calibrate_board(1)
    #camManager.cam_list[2].calibrate_board(11)
    #camManager.cam_list[4].calibrate_board(2) 

    while True:
        camManager.detection()

    #app.run(host='0.0.0.0', port='8090') #, debug=True

    camManager.stop_cams()
