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

#camera = camCls.Camera(src=4, rot=180)
#camera.calibrate_board(3)
camManager = camMng.camManager()

def exit_handler():
    camManager.stop_cams()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wait_throw')
def get_score():
    camera.dart_motion_dect()
    pos = camera.dartThrow.get_pos(format = 'point')
    score = camera.board.get_score(pos)
    return json.dumps({'score': score})

if __name__ == '__main__':
    atexit.register(exit_handler)

    camManager.cam_list[2].calibrate_board(20)

    #camManager.start_cams()
    #while True:
        #camManager.motion_detection()

    
    time.sleep(1)
    camManager.stop_cams()
    print('end')
    #app.run(host='0.0.0.0', port='8090') #, debug=True

    #img = cv2.imread('static/jpg/base_img4.jpg')
    #print(camera.board.h)
    #imgWarp = cv2.warpPerspective(img,camera.board.h,(800,800))
    #img = camera.cap.read() 
    #cv2.imwrite('static/jpg/warp.jpg', imgWarp)
