import datetime
import cv2
import time
import numpy as np
import glob
import src.boardClass as boardClass
import src.dartThrowClass as dartThrowClass
import src.videoCapture as videoCapture
import src.db_handler as db
import params

class Camera:
        
    def __init__(self, src, width, height, rot = 0):

        self.src = src
        self.width = width
        self.height = height
        h = db.get_trafo(self.src)
        exp = db.get_exposure(self.src)

        if exp is not None and h is not None:
            self.cap = videoCapture.VideoStream(src = self.src, width = width, height = height, rot = rot, exp = exp)
            self.board = boardClass.Board(h = h, src = self.src)
        else:
            self.cap = videoCapture.VideoStream(src = self.src, width = width, height = height, rot = rot)
            self.board = boardClass.Board(src = self.src)

        self.dartThrow = None
        self.stop_dect_tread = False
        self.is_hand_motion = False
        self.mapx, self.mapy = self.get_distortion_map()

    def start(self):
        self.cap.start()

    def stop(self):
        self.cap.stop()

    def take_pic(self, path = None):

        success = False
        img = None
        max_tries = 10
        for _ in range(max_tries):
            img, success = self.cap.read()
            if success:
                break

        if success == False:
            raise Exception('Problem reading camera')

        img = cv2.remap(img, self.mapx, self.mapy, cv2.INTER_LINEAR)

        print(img.shape)

        if path is None:
            cv2.imwrite('static/jpg/last_{}.jpg'.format(self.src), img)
        else:
            cv2.imwrite(path, img)
        
        return img

    def record_video(self, duration):

        frame_width = int(self.cap.stream.get(3))
        frame_height = int(self.cap.stream.get(4))
        path = '../dart_test_vids/test_vids/vid{}.avi'.format(self.src)
        out = cv2.VideoWriter(path ,cv2.VideoWriter_fourcc('M','J','P','G'), 8, (frame_width,frame_height))

        t1 = datetime.datetime.now()
        while((datetime.datetime.now()-t1).total_seconds() < duration):
            img, success = self.cap.read()

            if success == True: 
                out.write(img)
            else:
                break

        out.release()


    def auto_calibration(self, closest_field):
      
        exp_times = (10, 8, 12, 15, 18, 20, 9, 25, 6, 30, 35, 45, 60, 80) # move to constants
        exp_it = iter(exp_times)
        
        success = False
        while not success: 
            try:
                exp_time = next(exp_it)
                print(exp_time)
                self.cap.stream.set(cv2.CAP_PROP_EXPOSURE, exp_time)
                img = self.take_pic()
                success = self.board.auto_calibration(img, closest_field = closest_field)

            except StopIteration:
                return False

        h = self.board.h
        db.write_row(self.src, h, exp_time)
        
        return True


    def get_distortion_map(self):
        mtx = np.array([[params.fx, 0, params.cx],[0, params.fy, params.cy],[0, 0, 1]])
        dist = np.array([[params.k1, params.k2, params.p1, params.p2, params.k3]])
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (self.width,self.height), 1, (self.width,self.height))
        mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (self.width,self.height), 5)
        return mapx, mapy

    def calibrate_distortion_matrix(self):
        # Not in use

        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        size = (7,9) # Constant
        objp = np.zeros((size[0]*size[1],3), np.float32)
        objp[:,:2] = np.mgrid[0:size[0],0:size[1]].T.reshape(-1,2)
        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        path = 'static/jpg/chess_board/'
        images = glob.glob(path + 'img_4*.jpg')

        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (size[0],size[1]), None)
            # If found, add object points, image points (after refining them)
            if ret == True:

                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners)

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        h,  w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

        print('camera matrix: {}'.format(mtx))
        print('distortion: {}'.format(dist))
        print('new camera matrix: {}'.format(newcameramtx))

        return newcameramtx, mtx, dist


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
            
            # Criteria for being a dart:
            if t_motion < T_MAX and ratio_final < MAX_RATIO and ratio_final > MIN_RATIO:
                # undistort images
                img_before = cv2.remap(img_before, self.mapx, self.mapy, cv2.INTER_LINEAR)
                img_after = cv2.remap(img_after, self.mapx, self.mapy, cv2.INTER_LINEAR)

                self.dartThrow = dartThrowClass.dartThrow(img_before,img_after, self.src)
                self.is_hand_motion = False
                self.stop_dect_thread = True
                return

            elif t_motion > T_MAX or ratio_final > MAX_RATIO:
                #hand detected
                print("Hand detected. Cam: {} T: {} Ratio: {}".format(self.src, t_motion, ratio_final))
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

