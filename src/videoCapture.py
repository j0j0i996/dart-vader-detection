# import the necessary packages
from threading import Thread
import cv2
import time

rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]

class VideoStream:
    def __init__(self, src, width, height, rot = 0):
        # initialize the video camera stream and read the first frame
        # from the stream
        try:
            self.stream = cv2.VideoCapture(src)
        except:
            print("Cam is invalid.")

        self.stream.set(3, width)
        self.stream.set(4, height)
        self.stream.set(cv2.CAP_PROP_EXPOSURE,-5)
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
        #with concurrent.futures.ThreadPoolExecutor() as executor:
            #executor.submit(self.update)
        self.t = Thread(target=self.update, args=()).start()

    def update(self):
        # keep looping infinitely until the thread is stopped
        time.sleep(3)
        while self.running:
            (self.success, self.frame) = self.stream.read()
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
        
        self.count_last_read = self.image_count
        return frame, success

    def stop(self):
        # indicate that the thread should be stopped
        self.running = False
        

if __name__ == '__main__':
    cap = VideoStream(src = 0, rot = 180)
    cap.start()
    time.sleep(3)
    for i in range(5):
        img, success = cap.read()
        time.sleep(0.1)
        print(success)
        cv2.imwrite('test{}.jpg'.format(i), img)
        
    time.sleep(0.5)
    for i in range(6,10):
        img, success = cap.read()
        time.sleep(0.1)
        print(success)
        cv2.imwrite('test{}.jpg'.format(i), img)
    cap.stop()
    