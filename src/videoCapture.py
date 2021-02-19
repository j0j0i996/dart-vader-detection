# import the necessary packages
from threading import Thread
import cv2
import time
import numpy as np

rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]

class VideoStream:
    def __init__(self, src, width, height, rot = 0, local_video = False):

        self.width = width
        self.height = height
        self.local_video = local_video
          
        try:
            if self.local_video is False:
                self.stream = cv2.VideoCapture(src)

                codec = cv2.VideoWriter_fourcc( 'M', 'J', 'P', 'G'    )
                self.stream.set(cv2.CAP_PROP_FOURCC, codec)
                self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
                self.stream.set(cv2.CAP_PROP_EXPOSURE, 15)
                self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
                self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
                self.stream.set(cv2.CAP_PROP_FPS, 8)
            else:
                self.stream = cv2.VideoCapture('../dart_test_vids/test_vids/vid{}.avi'.format(src))
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
            if self.local_video:
                time.sleep(1/15)

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