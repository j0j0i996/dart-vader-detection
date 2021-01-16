import src.cameraClass as camCls
from threading import Thread
import cv2
import time
import numpy as np
import time

class camManager:
        
    def __init__(self, width = 640, height = 480):

        self.width = width
        self.height = height
        self.src_list = self.get_srcs()
        #self.src_list = [0, 2, 4]
        self.cam_list = self.activate_cams()

        print(self.src_list)


    @staticmethod
    def get_srcs():
        
        max_tries = 3
        src_list = []

        for src in range(9):
            cap=cv2.VideoCapture(src)
            for _ in range(max_tries):
                if cap.read()[0] is True:
                    src_list.append(src)
                    break
            cap.release()
        
        return src_list

    def activate_cams(self):
        cams = []
        for src in self.src_list:
            cams.append(camCls.Camera(src=src, rot=180, width = self.width , height = self.height))
        return cams

    def start_cams(self):
        for cam in self.cam_list:
            cam.start()
        time.sleep(5)

    def stop_cams(self):
        for cam in self.cam_list:
            cam.stop()

    def take_pic(self):
        for cam in self.cam_list:
            cam.take_pic()

    def manual_calibration(self):
        for cam in self.cam_list:
            cam.manual_calibration()

    def detection(self):
        
        # start motion detection
        t_list = []
        for cam in self.cam_list:
            t = Thread(target=cam.dart_motion_dect, args=())
            t.start()
            t_list.append(t)

        print('Waiting for motion')
        
        motion = False
        while motion == False:
            for cam in self.cam_list:
                if cam.stopMotionThread:
                    motion = True
        
        time.sleep(0.3)

        dect_cams = []
        nextPlayer = False
        for cam in self.cam_list:
                if cam.stopMotionThread: # get information of cameras which detected motion
                    dect_cams.append({'cam':cam, 'src':cam.src, 'ratio': cam.motionRatio, 'p1': None, 'p2': None})
                    if cam.motionRatio == False:
                        nextPlayer = True
                else:
                    cam.stopMotionThread = True # stops motion detection of other cameras

        if nextPlayer:
            score = False
            multiplier = False
            std_pos = None
            print('End of turn')
        else:
            nextPlayer = False
            if len(dect_cams) == 1:
                print('point')
                cam = dect_cams[0]['cam']
                rel_pos = cam.dartThrow.get_pos(format = 'point')
                std_pos = cam.board.rel2std(rel_pos)

                #testing
                img = cam.board.draw_board()
                cv2.circle(img, (int(std_pos[0]), int(std_pos[1])), 3, (255,0,0), 2)
                cv2.imwrite('static/jpg/line_detection.jpg', img)

                score, multiplier = cam.board.get_score(std_pos)
            else:
                print('line')
                #filter_list = sorted(ratio_list, key=lambda k: k['ratio'], reverse = True)[0:2]
                cams = [x['cam'] for x in dect_cams]

                line_list = []
                for item in dect_cams:
                    item['p1'], item['p2'] = item['cam'].dartThrow.get_pos(format = 'line')

                # prioritize cams:
                # current priorization method: take most vertical line
                dect_cams = sorted(dect_cams,key = lambda k: abs(k['p1'][0] - self.width / 2))
                print('cam:' + str(dect_cams[0]['src']) + '\n cam:' + str(dect_cams[1]['src']))

                for item in dect_cams[0:2]:
                    p1 = item['cam'].board.rel2std(item['p1'])
                    p2 = item['cam'].board.rel2std(item['p2'])
                    line_list.append([p1,p2])

                std_pos = self.line_intersection(line_list[0],line_list[1])

                #testing
                img = cams[0].board.draw_board()
                img = cv2.line(img,(int(line_list[0][0][0]),int(line_list[0][0][1])), (int(line_list[0][1][0]),int(line_list[0][1][1])), 255, 2)
                cv2.line(img,(int(line_list[1][0][0]),int(line_list[1][0][1])), (int(line_list[1][1][0]),int(line_list[1][1][1])), 255, 2)
                cv2.circle(img, (int(std_pos[0]), int(std_pos[1])), 3, (255,0,0), 2)
                cv2.imwrite('static/jpg/line_detection.jpg', img)

                score, multiplier = cams[0].board.get_score(std_pos)

        # Make sure all threads are closed
        for cam in self.cam_list:
            cam.stopMotionThread = True
        
        return score, multiplier, nextPlayer

    @staticmethod
    def line_intersection(line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y


if __name__ == '__main__':
    cam_mng = camManager()
    print(cam_mng.src_list)
        