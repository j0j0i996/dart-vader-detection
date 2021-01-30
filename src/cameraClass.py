import datetime
import cv2
import time
import numpy as np
import src.boardClass as boardClass
import src.dartThrowClass as dartThrowClass
import src.videoCapture as videoCapture
import src.db_handler as db
import src.dropbox_integration as dbx

img_count = 0

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
        self.stopDectThread = False
        self.is_hand_motion = False

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

        #try:
            self.stopDectThread = False
            self.dartThrow = None
            
            #Parameters
            t_sleep = 0 # Take a picure every t_sleep at seconds
            t_max = 0.7 # Maximum time the motion should take time - hereby we can distinguish between dart throw and human
            min_ratio = 0.002 #Thresholds important - make accessible / dynamic - between 0 and 1
            max_ratio = 0.05
            dect_ratio = min_ratio

            #Testing
            #image_before_link = 'static/jpg/before_{}.jpg'.format(self.src)
            #image_after_link = 'static/jpg/after_{}.jpg'.format(self.src)
            
            while self.stopDectThread == False:

                # Wait for motion
                img_before, img_start_motion = self.wait_diff_in_bnd(dect_ratio, np.inf, t_sleep)

                t1 = datetime.datetime.now()
                # Wait for motion to stop
                _, img_after = self.wait_diff_in_bnd(0, dect_ratio, t_sleep, start_image = img_start_motion)

                t2 = datetime.datetime.now()
                t_motion = (t2-t1).total_seconds()

                # take img after motion stopped:
                time.sleep(t_sleep)
                img_after, _ = self.cap.read()

                # Get difference ratio of image befor motion and image after motion
                ratio_final = Camera.get_img_diff_ratio(img_before,img_after)
                
                # Criteria for being a dart:
                if t_motion < t_max and ratio_final < max_ratio and ratio_final > min_ratio:
                    #dart detected
                    
                    #Testing
                    #cv2.imwrite(image_before_link, img_before)
                    #cv2.imwrite(image_after_link, img_after)
                    #lobal img_count
                    #cv2.imwrite('static/session_imgs/before_{}_{}.jpg'.format(self.src, img_count),img_before)
                    #cv2.imwrite('static/session_imgs/after_{}_{}.jpg'.format(self.src, img_count),img_after)
                    #img_count = img_count + 1

                    self.dartThrow = dartThrowClass.dartThrow(img_before,img_after, self.src)
                    self.is_hand_motion = False
                    self.stopDectThread = True
                    return

                elif t_motion > t_max or ratio_final > max_ratio:
                    #hand detected
                    self.stopDectThread = True
                    self.is_hand_motion = True
                    return

        #except:
        #    self.stopDectThread = True
        #    self.is_hand_motion = False
        #    self.dartThrow = None
        #    return

    def wait_diff_in_bnd(self,min_ratio,max_ratio,t_sleep, start_image = None):
        img_diff_ratio = -1
        
        if start_image is None:
            img1, _ = self.cap.read()
            time.sleep(t_sleep)
        else:
            img1 = start_image

        img2, _ = self.cap.read()
        img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)

        while img_diff_ratio < min_ratio or img_diff_ratio > max_ratio:
            
            time.sleep(t_sleep)
            img1 = img2.copy()

            img2, _ = self.cap.read()

            img_diff_ratio = Camera.get_img_diff_ratio(img1, img2)
    
        print("Diff ratio = {} ".format(round(img_diff_ratio, 5)))

        return img1, img2

    @staticmethod
    def get_img_diff_ratio(img1, img2):

        dim = (320, 240)
        img1 = cv2.resize(img1, dim)
        img2 = cv2.resize(img2, dim)

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

    dim = (320, 240)
    img1 = cv2.resize(img1, dim)
    cv2.imwrite('../static/jpg/small_0.jpg', img1)

    t1 = datetime.datetime.now()

    img2 = cv2.resize(img2, dim)

    ratio = Camera.get_img_diff_ratio(img1, img2)

    t2 = datetime.datetime.now()

    print(ratio)
    print('img diff time: {}'.format(t2-t1))

