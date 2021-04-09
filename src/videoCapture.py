# import the necessary packages
from threading import Thread
import cv2
import time
import numpy as np

rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]

class VideoStream:
    def __init__(self, src, width, height, rot = 0, exp = 15):

        self.width = width
        self.height = height
          
        try:
            self.stream = cv2.VideoCapture(src)
            codec = cv2.VideoWriter_fourcc( 'M', 'J', 'P', 'G'    )
            self.stream.set(cv2.CAP_PROP_FOURCC, codec)
            self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
            self.stream.set(cv2.CAP_PROP_EXPOSURE, exp)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.stream.set(cv2.CAP_PROP_FPS, 8)
        except:
            print("Not able to open camera {}".format(src))

        self.rotCode = rotations[int(rot/90)]
        self.update_count = 0
        self.last_read_count = 0
        self.frame = None
        self.success = None
        self.running = False

    def start(self):
        self.running = True
        self.t = Thread(target=self.update, args=()).start()

    def update(self):
        while self.running:
            success, frame = self.stream.read()
            self.success, self.frame = success, frame
            self.update_count = self.update_count + 1

    def read(self):
        frame, success = self.frame, self.success
        while True:
            frame, success = self.frame, self.success
            if self.update_count > self.last_read_count and success == True:
                break
        
        if self.rotCode is not None:
            frame = cv2.rotate(frame, self.rotCode)
        
        self.last_read_count = self.update_count

        return frame, success

    def stop(self):
        self.running = False