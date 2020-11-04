from flask import Flask, render_template
import src.cam_control as cam_ctrl
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/take_picture')
def take_picture():
    image_path = cam_ctrl.take_picture()
    return json.dumps({'path': image_path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8090') #, debug=True