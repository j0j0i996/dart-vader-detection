# import the necessary packages
from threading import Thread
import cv2

rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]

class VideoStream:
    def __init__(self, src=0, width = 640, height = 480, rot = 0):
        # initialize the video camera stream and read the first frame
        # from the stream
        try:
            self.stream = cv2.VideoCapture(src)
        except:
            print("Cam is invalid.")

        self.stream.set(3, width)
        self.stream.set(4, height)
        self.stream.set(cv2.CAP_PROP_EXPOSURE,-2)

        (self.grabbed, self.frame) = self.stream.read()
        self.rotCode = rotations[int(rot/90)]

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
        while self.running:
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        frame, grabbed = self.frame, self.grabbed
        if self.rotCode is not None:
            frame = cv2.rotate(frame, self.rotCode)
        return frame, grabbed

    def stop(self):
        # indicate that the thread should be stopped
        self.running = False
        

if __name__ == '__main__':
    cap = VideoStream(src = 2, rot = 180)
    cap.start()
    for i in range(5):
        img, success = cap.read()
        print(success)
        cv2.imwrite('test{}.jpg'.format(i), img)
    cap.stop()
    cap.start()
    for i in range(6,10):
        img, success = cap.read()
        print(success)
        cv2.imwrite('test{}.jpg'.format(i), img)
    cap.stop()
    