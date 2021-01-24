# import the necessary packages
from threading import Thread
import cv2
import time
import numpy as np

rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]

class VideoStream:
    def __init__(self, src, width, height, rot = 0):
        # initialize the video camera stream and read the first frame
        # from the stream
        try:
            self.stream = cv2.VideoCapture(src)
        except:
            print("Cam is invalid.")

        codec = 0x47504A4D
        self.stream.set(cv2.CAP_PROP_FOURCC, codec)
        self.width = width
        self.height = height
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
        self.stream.set(cv2.CAP_PROP_EXPOSURE, 50)
        
        self.stream.set(cv2.CAP_PROP_FPS,15)
        self.rotCode = rotations[int(rot/90)]
        self.update_count = 0
        self.last_read_count = 0

        self.frame = None
        self.success = None

        # initialize the variable used to indicate if the thread should
        self.running = False

    def start(self):
        # start the thread to read frames from the video stream
        self.running = True
        self.t = Thread(target=self.update, args=()).start()

    def update(self):
        # keep looping infinitely until the thread is stopped
        while self.running:
            success, frame = self.stream.read()
            dim = (self.width, self.height)
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            #cv2.normalize(frame, frame, 0, 220, cv2.NORM_MINMAX)
            self.success, self.frame = success, frame
            self.update_count = self.update_count + 1

    def read(self):
        # return the frame most recently read
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
        # indicate that the thread should be stopped
        self.running = False