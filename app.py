from flask import Flask, render_template
import os
import json
import src.cameraClass as camCls

app = Flask(__name__)

camera = camCls.Camera('Test',180)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/take_picture/<img_name>')
def take_picture(img_name):
    image_path = camera.take_picture(img_name)
    return json.dumps({'path': image_path})

@app.route('/wait_throw')
def get_score():
    camera.motion_detection()
    return json.dumps({'score': camera.dartThrow.score})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8090', debug=True) #, debug=True
    #app.run(debug=True, port='8090')
    #camera = camCls.Camera('Test',180)
    #camera.motion_detection()
