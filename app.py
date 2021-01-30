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

cam_manager = camMng.camManager()

def exit_handler():
    cam_manager.stop_cams()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wait_throw')
def get_score():
    score, multiplier, nextPlayer, success = cam_manager.detection()
    return json.dumps({'score': score, 'multiplier': multiplier, 'nextPlayer': nextPlayer})

if __name__ == '__main__':
    atexit.register(exit_handler)
    
    cam_manager.start_cams()

    #cam_manager.take_pic()

    #cam_manager.manual_calibration()
    #cam_manager.cam_list[0].calibrate_board(18)
    #cam_manager.cam_list[1].calibrate_board(11)
    #cam_manager.cam_list[2].calibrate_board(2) 

    while True:
        cam_manager.detection()

    #app.run(host='0.0.0.0', port='8090') #, debug=True



    cam_manager.stop_cams()
