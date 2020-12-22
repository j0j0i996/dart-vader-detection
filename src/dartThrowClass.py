import cv2
import numpy as np

class dartThrow:

    def __init__(self, img_before_link, img_after_link):
        self.img_before_link = img_before_link
        self.img_after_link = img_after_link

    def __repr__(self):
        return 'RelCarth Pos: {} \n\nStd Carth Pos: {} \n'\
            .format(self.rel_carth_pos, self.std_carth_pos)

    def get_pos(self, format = 'line'): #alternative: format = 'point'

        imgBf = cv2.imread(self.img_before_link)
        imgAf = cv2.imread(self.img_after_link)

        diff = cv2.absdiff(imgBf, imgAf)
        height, width = diff.shape[:2]

        # transform to gray scale
        diff_gray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        #add blur
        kernel = np.ones((3,3),np.float32)/9
        diffBlur = cv2.filter2D(diff_gray,-1,kernel)

        # First step: Find dart -> Use contours to find bounding box around dart
        cnt, box_dart = self.get_dart_cnt_and_box(diffBlur)

        # Second: Get features insed dart box and fit line through them
        line = self.get_line(diffBlur, box_dart)

        if format == 'line':
            [vx, vy, x0, y0] = line
            lefty = float((-x0 * vy / vx) + y0)
            righty = float((width - x0) * vy / vx + y0)
            p1 = np.array([0,lefty])
            p2 = np.array([width-1, righty])

            #Testing
            cv2.line(imgAf,(0,int(lefty)),(width-1,int(righty)),(255,255,0),)
            cv2.imwrite('static/jpg/dart_line.jpg',imgAf)
            return p1, p2
            
        elif format == 'point':
            pos = self.get_tip_pos(cnt, line, width)

            #Testing
            cv2.drawMarker(imgAf, (int(pos[0]), int(pos[1])), color=(0, 76, 252), markerSize = 40, thickness = 2)
            cv2.imwrite('static/jpg/rec_dart.jpg',imgAf)
            return pos
        else:
            print('wrong format of position entered')

    @staticmethod
    def get_tip_pos(cnt, line, width):
        #sort contour points from top to bottom
        cnt = np.array(cnt).reshape(len(cnt),2)
        ind = np.lexsort((cnt[:,0],cnt[:,1])) 
        cnt = cnt[ind]

        # get distance of each point to line with signs
        [vx, vy, x0, y0] = line
        lefty = int((-x0 * vy / vx) + y0)
        righty = int(((width - x0) * vy / vx) + y0)

        p1 = np.array([0,lefty])
        p2 = np.array([width-1, righty])

        orth = np.array([vx * np.cos(np.pi/2) - vy * np.sin(np.pi/2), vx * np.sin(np.pi/2) + vy * np.cos(np.pi/2)])

        tip_pos = None
        for pt in cnt:
                dist = np.cross(p2-p1,pt-p1)/np.linalg.norm(p2-p1)
                if tip_pos is None and abs(dist) < 4:
                    tip_pos = pt

        return tip_pos

    @staticmethod
    def get_dart_cnt_and_box(diff):
        
        inc_box = 1.2 # Importan threshold

        # Get binary image
        ret, binary_img = cv2.threshold(diff, 70, 255, 0) #Important threshold

        # Get contours
        kernel = np.ones((50,20),np.float32)
        binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)
        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # If more than 1 contour found, merge neigboring contours
        rects = []
        if len(contours) > 1:
            for cnt in contours:
                rects.append(cv2.boundingRect(cnt))
            
            # check if rectangles overlap (intersection with w>0 and h>0) or are close to each other
            for a in rects:
                for b in rects: 
                    if a == b:
                        continue
                    
                    # get intersection rectangle
                    x = max(a[0], b[0])
                    y = max(a[1], b[1])
                    w = min(a[0]+a[2], b[0]+b[2]) - x
                    h = min(a[1]+a[3], b[1]+b[3]) - y

                    max_dist = 20 # important threshold - max distance between rectangles which shall be connected
                    if w>-max_dist and h>-max_dist:
                        binary_img = cv2.rectangle(binary_img,(x,y),(x+w,y+h), 255, thickness=cv2.FILLED)

        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cnt = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(cnt)

        #increas box
        center,(rect_width,rect_height),theta = rect
        rect_width = rect_width * inc_box
        rect_height = rect_height * inc_box
        rect = center,(rect_width,rect_height),theta

        box = cv2.boxPoints(rect)
        box = np.int0(box)

        return cnt, box

    @staticmethod
    def get_line(diff, box_dart):

        height, width = diff.shape[:2]

        mask = np.zeros_like(diff)
        cv2.fillPoly(mask,pts=[box_dart],color=255)

        features = cv2.goodFeaturesToTrack(diff, 640, 0.0008, 1, mask=mask, blockSize=3, useHarrisDetector=1, k=0.06) #sensible: 0.0004, medium: 0.0008, conservative: 0.001

        # Filter features by drawing line through them
        [vx, vy, x0, y0] = cv2.fitLine(features, cv2.DIST_HUBER, 0, 0.1, 0.1) #dist_L1 cost function is p(r)=r, dist_L2 cost function is p(r)=r^2
        line = [vx, vy, x0, y0]
        lefty = int((-x0 * vy / vx) + y0)
        righty = int(((width - x0) * vy / vx) + y0)

        features_to_delete = []
        i = 0
        p1 = np.array([0,lefty])
        p2 = np.array([width-1, righty])

        return line

if __name__ == '__main__':
    dart = dartThrow('static/jpg/before.jpg', 'static/jpg/after.jpg')
    p1, p2 = dart.get_position(format = 'line')
    print(p1)
    print(p2)