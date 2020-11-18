from flask import Flask, render_template
import os
import json
import src.cameraClass as camCls

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/take_picture/<img_name>')
def take_picture(img_name):
    image_path = cam.take_picture(img_name)
    return json.dumps({'path': image_path})

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port='8090') #, debug=True
    #app.run(debug=True, port='8090')
    camera = camCls.Camera('Test',180)
    camera.motion_detection()

    #print('_______')
    #print('Dart Throw representation')
    #print(camera.dartThrow)

    #print('\nDart Board representation\n')
    #print(camera.board)
