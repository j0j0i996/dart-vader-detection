import datetime
import cv2
import time
import numpy as np
import src.boardClass as boardClass
import src.dartThrowClass as dartThrowClass
import src.videoCapture as videoCapture
import src.db_handler as db
class Camera:
        
    def __init__(self, src, width, height, rot = 0):

        self.src = src
        self.cap = videoCapture.VideoStream(src = src, width = width, height = height, rot = rot)
        
        # get transformation from sql
        h = db.get_trafo(self.src)
    
        if h is not None:
            self.board = boardClass.Board(h = h, src = self.src)
        else:
            self.board = boardClass.Board(src = self.src)

        self.dartThrow = None
        self.stop_dect_tread = False
        self.is_hand_motion = False

        #testing
        self.img_count = 7

    def start(self):
        self.cap.start()

    def stop(self):
        self.cap.stop()

    def take_pic(self):
        if self.cap.running == False:
            self.start()

        success = False
        img = None
        max_tries = 10
        for _ in range(max_tries):
            img, success = self.cap.read()
            if success:
                break

        if success == False:
            raise Exception('Problem reading camera')

        print(img.shape)

        cv2.imwrite('static/jpg/last_{}.jpg'.format(self.src), img)

        return img

    def calibrate_board(self, closest_field):

        img = self.take_pic()

        self.board.calibration(img, closest_field = closest_field)
        h = self.board.h
        db.write_trafo(self.src, h)

        self.stop()

    def manual_calibration(self):
        self.board.manual_calibration()
        h = self.board.h
        print(h)
        db.write_trafo(self.src, h)

    def dart_motion_dect(self):

        self.stop_dect_thread = False
        self.dartThrow = None
        
        #Parameter
        T_MAX = 0.6 # Maximum time the motion should take time
        T_VIB = 0.05 # potential vibration time
        MIN_RATIO = 0.001 #Thresholds important - make accessible / dynamic - between 0 and 1
        MAX_RATIO = 0.035
        DECT_RATIO = MIN_RATIO / 5
        
        while self.stop_dect_thread == False:

            # Wait for motion
            img_before, img_start_motion = self.wait_diff_in_bnd(DECT_RATIO, np.inf)

            t1 = datetime.datetime.now()
            # Wait for motion to stop
            _, img_after = self.wait_diff_in_bnd(0, DECT_RATIO, start_image = img_start_motion)

            t2 = datetime.datetime.now()
            t_motion = (t2-t1).total_seconds()

            time.sleep(T_VIB)

            # take img after motion stopped:
            img_after, _ = self.cap.read()

            # Get difference ratio of image befor motion and image after motion
            ratio_final = Camera.get_img_diff_ratio(img_before,img_after)
            #print("Ratio cam {} = {}".format(self.src,ratio_final))
            
            # Criteria for being a dart:
            if t_motion < T_MAX and ratio_final < MAX_RATIO and ratio_final > MIN_RATIO:
                #dart detected
                
                #Testing
                #cv2.imwrite('static/jpg/before_{}.jpg'.format(self.src), img_before)
                #cv2.imwrite('static/jpg/after_{}.jpg'.format(self.src), img_after)
                #cv2.imwrite('static/session_imgs/before_{}_{}.jpg'.format(self.src, self.img_count),img_before)
                #cv2.imwrite('static/session_imgs/after_{}_{}.jpg'.format(self.src, self.img_count),img_after)
                #self.img_count = self.img_count + 1

                self.dartThrow = dartThrowClass.dartThrow(img_before,img_after, self.src)
                self.is_hand_motion = False
                self.stop_dect_thread = True
                return

            elif t_motion > T_MAX or ratio_final > MAX_RATIO:
                #hand detected
                self.stop_dect_thread = True
                self.is_hand_motion = True
                return

    def wait_diff_in_bnd(self,MIN_RATIO,MAX_RATIO, start_image = None):
        img_diff_ratio = -1
        
        if start_image is None:
            img1, _ = self.cap.read()
        else:
            img1 = start_image

        img2, _ = self.cap.read()
        img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

        while img_diff_ratio < MIN_RATIO or img_diff_ratio > MAX_RATIO:
            
            img1 = img2.copy()

            img2, _ = self.cap.read()

            img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

        return img1, img2

    @staticmethod
    def get_img_diff_ratio(img1, img2):

        DIM = (240, 180)
        img1 = cv2.resize(img1, DIM)
        img2 = cv2.resize(img2, DIM)

        diff = cv2.absdiff(img2,img1)
        diff = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        #diff = cv2.GaussianBlur(diff, (5, 5), 0)
        _, thresh = cv2.threshold(diff, 60, 255, 0)

        white_pixels = cv2.countNonZero(thresh)
        total_pixels = diff.size
        ratio = white_pixels/total_pixels

        return ratio


if __name__ == '__main__':
    img1 = cv2.imread('../static/jpg/last_0.jpg')
    img2 = cv2.imread('../static/jpg/last_2.jpg')

    dim = (240, 180)
    img1 = cv2.resize(img1, dim)
    cv2.imwrite('../static/jpg/small_0.jpg', img1)

    t1 = datetime.datetime.now()

    img2 = cv2.resize(img2, dim)

    ratio = Camera.get_img_diff_ratio(img1, img2)

    t2 = datetime.datetime.now()

    print(ratio)
    print('img diff time: {}'.format(t2-t1))

