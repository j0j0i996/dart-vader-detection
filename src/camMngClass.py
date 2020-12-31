import src.cameraClass as camCls
from threading import Thread
import cv2
import time
import numpy as np
import time

class camManager:
        
    def __init__(self, width = 512, height = 384):

        self.width = width
        self.height = height
        self.src_list = self.get_srcs()
        #self.src_list = [0]
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

    def stop_cams(self):
        for cam in self.cam_list:
            cam.stop()

    def detection(self):
        
        # start motion detection
        t_list = []
        for cam in self.cam_list:
            t = Thread(target=cam.dart_motion_dect, args=())
            t.start()
            t_list.append(t)
        
        motion = False
        while motion == False:
            for cam in self.cam_list:
                if cam.motionDetected:
                    motion = True
        
        time.sleep(1)

        ratio_list = []
        end_of_turn = False
        for cam in self.cam_list:
                if cam.motionDetected:
                    ratio_list.append({'cam':cam, 'src':cam.src, 'ratio': cam.motionRatio})
                    if cam.motionRatio == False:
                        end_of_turn = True
                else:
                    cam.motionDetected = True # stops motion detection of camera

        print(ratio_list)

        if end_of_turn:
            score = False
            event = 'End of turn'
            std_pos = None
            print('End of turn')
        elif len(ratio_list) == 1:
            cam = ratio_list[0]['cam']
            rel_pos = cam.dartThrow.get_pos(format = 'point')
            std_pos = cam.board.rel2std(rel_pos)

            #testing
            img = cam.board.draw_board()
            cv2.circle(img, (int(std_pos[0]), int(std_pos[1])), 3, (255,0,0), 2)
            cv2.imwrite('static/jpg/line_detection.jpg', img)

            score = cam.board.get_score(std_pos)
            event = 'Dart'
        else:
            filter_list = sorted(ratio_list, key=lambda k: k['ratio'], reverse = True)[0:2]
            print(filter_list)
            cams = [x['cam'] for x in filter_list]

            line_list = []
            for cam in cams:
                p1, p2 = cam.dartThrow.get_pos(format = 'line')
                print(p1)
                print(p2)
                p1 = cam.board.rel2std(p1)
                p2 = cam.board.rel2std(p2)
                line_list.append([p1,p2])

                
            print(line_list)
            std_pos = self.line_intersection(line_list[0],line_list[1])

            #testing
            img = cams[0].board.draw_board()
            img = cv2.line(img,(int(line_list[0][0][0]),int(line_list[0][0][1])), (int(line_list[0][1][0]),int(line_list[0][1][1])), 255, 2)
            cv2.line(img,(int(line_list[1][0][0]),int(line_list[1][0][1])), (int(line_list[1][1][0]),int(line_list[1][1][1])), 255, 2)
            cv2.circle(img, (int(std_pos[0]), int(std_pos[1])), 3, (255,0,0), 2)
            cv2.imwrite('static/jpg/line_detection.jpg', img)

            score = cams[0].board.get_score(std_pos)
            event = 'Dart'

        for t in t_list:
            t.join()

        #testing
        #camCls.Camera.img_count = camCls.Camera.img_count + 1
        
        return score, event, std_pos

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
        