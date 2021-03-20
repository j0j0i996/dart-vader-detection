import src.cameraClass as camCls
import src.boardClass as boardCls
from threading import Thread
import cv2
import time
import numpy as np
import time
import datetime
import sys
import json

class camManager:
        
    def __init__(self, width = 800, height = 600, local_video = False):

        self.width = width
        self.height = height
        self.src_list = self.get_srcs()
        #self.src_list = [0,2,4]
        self.cam_list = self.activate_cams(local_video)
        self.dect_loop_active = False

        print(self.src_list)


    @staticmethod
    def get_srcs():
        
        MAX_TRIES = 3
        src_list = []

        for src in range(9):
            cap=cv2.VideoCapture(src)
            for _ in range(MAX_TRIES):
                if cap.read()[0] is True:
                    src_list.append(src)
                    break
            cap.release()
        
        return src_list

    def activate_cams(self, local_video):
        cams = []
        for src in self.src_list:
            cams.append(camCls.Camera(src=src, rot=180, width = self.width , height = self.height, local_video=local_video))
        return cams

    def start_cams(self):
        for cam in self.cam_list:
            cam.start()
        time.sleep(7)

    def stop_cams(self):
        for cam in self.cam_list:
            cam.stop()

    def take_pic(self):
        for cam in self.cam_list:
            cam.take_pic()
    
    def record_video(self, duration):
        t_list = []
        for cam in self.cam_list:
            t = Thread(target=cam.record_video, args=(duration,))
            t.start()
            t_list.append(t)


    def manual_calibration(self):
        for cam in self.cam_list:
            cam.manual_calibration()

    def dect_loop(self,sio):
        self.dect_loop_active = True
        while self.dect_loop_active == True:
            try:
                field, multiplier, nextPlayer = self.detection()
                sio.emit('dart', json.dumps({"field": field, "multiplier": multiplier, "nextPlayer": nextPlayer}))
                print('message sent')
            except Exception as ex:
                    print(ex) 

    def detection(self):

        # start motion detection
        t_list = []
        for cam in self.cam_list:
            t = Thread(target=cam.dart_motion_dect, args=())
            t.start()
            t_list.append(t)

        print('Waiting for motion')

        motion = False
        undetected_indx = list(range(len(self.cam_list)))
        dect_cams = []
        next_player  = False
        while motion is False:
            for i in undetected_indx:
                cam = self.cam_list[i]
                if cam.stop_dect_thread:
                    motion = True
                    undetected_indx.remove(i)
                    dect_cams.append({'cam':cam, 'src':cam.src, 'single_pt': None, 'line_pts': None})

                    if cam.is_hand_motion:
                        next_player = True

        t0 = datetime.datetime.now()
        t_now = datetime.datetime.now()

        T_MAX = 0.4 #treshold
        while (t_now-t0).total_seconds() < T_MAX and len(dect_cams) < len(self.cam_list):
            for i in undetected_indx:
                cam = self.cam_list[i]
                if cam.stop_dect_thread:
                    undetected_indx.remove(i)
                    dect_cams.append({'cam':cam, 'src':cam.src, 'single_pt': None, 'line_pts': None})

                    if cam.is_hand_motion:
                        next_player = True

            t_now = datetime.datetime.now()

        # Make sure all threads are closed
        for cam in self.cam_list:
            cam.stop_dect_thread = True

        if next_player:
            time.sleep(1)
            score = False
            multiplier = False
            pos = None
            print('End of turn')
        else:
            single_pt_list = []
            line_list = []
            for item in dect_cams:
                try:
                    single_pt_rel, line_rel = item['cam'].dartThrow.get_pos()
                except Exception as ex:
                    print(ex)
                    continue
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    continue

                single_pt_std = item['cam'].board.rel2std(single_pt_rel)
                single_pt_list.append(single_pt_std)

                line_std = [item['cam'].board.rel2std(line_rel[0]),item['cam'].board.rel2std(line_rel[1])]
                line_list.append(line_std)

            print('{} cams detected a motion'.format(len(dect_cams)))

            if len(single_pt_list) == 0: 
                raise Exception('Not able to find dart')

            if len(single_pt_list) == 1:
                
                pos = single_pt_list[0]
                score, multiplier = boardCls.Board.get_score(pos)

                #testing
                #img = cam.board.draw_board()
                #cv2.circle(img, (int(pos[0]), int(pos[1])), 3, (255,0,0), 2)
                #cv2.imwrite('static/jpg/recognition.jpg', img)

            else:
                
                
                #get two single pts which are closest together
                def dist(pt1, pt2):
                    comparison = pt1 == pt2
                    equal_arrays = comparison.all()
                    if equal_arrays:
                        return np.inf
                    else:
                        return np.linalg.norm(pt2-pt1)

                dist_matrix = np.array([np.array([dist(pt1, pt2) for pt1 in single_pt_list]) for pt2 in single_pt_list])
                ind = np.unravel_index(dist_matrix.argmin(), dist_matrix.shape)
                single_pt_list = [single_pt_list[i] for i in list(ind)]

                
                #get avg of single points
                avg_single_pt = np.mean(single_pt_list, axis = 0)

                # get interesection points of lines
                intersect_list = []
                for i in range(len(line_list)):
                    for j in range(len(line_list)):
                        if i < j: 
                            try:
                                intersect = self.line_intersection(line_list[i],line_list[j])
                            except Exception as ex:
                                print(ex)
                                continue

                            intersect_list.append(intersect)

                # take intesect which is closest to avg_single_pt as dart tip pos
                dist_list = [np.linalg.norm(pt-avg_single_pt) for pt in intersect_list]
                pos = intersect_list[np.argmin(dist_list)]
                """
                #testing
                img = cam.board.draw_board()
                for line in line_list:
                    cv2.line(img,(int(line[0][0]),int(line[0][1])), (int(line[1][0]),int(line[1][1])), 255, 2)
                cv2.circle(img, (int(pos[0]), int(pos[1])), 3, (255,0,0), 2)
                cv2.imwrite('static/jpg/recognition.jpg', img)
                """

                score, multiplier = boardCls.Board.get_score(pos)

        t1 = datetime.datetime.now()

        print('Total recognition time: {}'.format(t1-t0))
        return score, multiplier, next_player

    @staticmethod
    def line_intersection(line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('Lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y


if __name__ == '__main__':
    cam_mng = camManager()
    print(cam_mng.src_list)
        