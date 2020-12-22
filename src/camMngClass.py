import cameraClass as camCls
from threading import Thread
import cv2

class camManager:
        
    def __init__(self):
        self.src_list = self.get_srcs()
        self.cam_list = self.activate_cams()

    @staticmethod
    def get_srcs():
        
        max_tries = 3
        src_list = []

        for src in range(9):
            cap=cv2.VideoCapture(src)
            for _ in range(max_tries):
                if cap.read()[0] is not False:
                    src_list.append(src)
                    break
            cap.release()
        
        return src_list

    def activate_cams(self):

        cams = []
        for src in self.src_list:
            cams.append(camCls.Camera(src=src, rot=180))
        return cams


    def motion_detection(self):
        
        # start motion detection
        t_list = []
        for cam in self.cam_list:
            t = Thread(target=cam.dart_motion_dect, args=())
            t.start()
            t.append(t_list)
        
        no_motion = True

        while no_motion:
            for cam in self.cam_list:
                if cam.motionDetected:
                    return
        
        time.sleep(0.05)

        ratio_list = []
        for cam in self.cam_list:
                if cam.motionDetected:
                    ratio_list.append{'src':cam.src, 'ratio': cam.motionRatio}

        if len(ratio_list) == 1:
            pos = camera.dartThrow.get_pos(format = 'point')
            score = camera.board.get_score(pos)
        else:
            get maximimum 2 arguments

            
        



if __name__ == '__main__':
    cam_mng = camManager()
    print(cam_mng.cam_list)
        