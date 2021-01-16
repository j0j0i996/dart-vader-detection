import cv2
import numpy as np

class dartThrow:

    def __init__(self, img_before, img_after, src):
        self.img_before = img_before
        self.img_after = img_after
        self.src = src

    def __repr__(self):
        return 'RelCarth Pos: {} \n\nStd Carth Pos: {} \n'\
            .format(self.rel_carth_pos, self.std_carth_pos)

    def get_pos(self, format = 'line'): #alternative: format = 'point'

        #imgBf = cv2.imread(self.img_before_link)
        #imgAf = cv2.imread(self.img_after_link)
        imgBf = self.img_before
        imgAf = self.img_after

        diff = cv2.absdiff(imgBf, imgAf)
        height, width = diff.shape[:2]

        # transform to gray scale
        diff_gray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        #add blur
        kernel = np.ones((3,3),np.float32)/9
        diffBlur = cv2.filter2D(diff_gray,-1,kernel)

        # First step: find contours of dart
        box = self.get_dart_box(diffBlur)

        # Second: fit line through contour
        line = self.get_line(diffBlur, box)

        if format == 'line':
            [vx, vy, x0, y0] = line
            top = float((-y0 * vx / vy) + x0)
            bottom = float((height - y0) * vx / vy + x0)
            p1 = np.array([top,0])
            p2 = np.array([bottom, height - 1])

            #Testing
            cv2.line(imgAf,(int(top),0),(int(bottom),height - 1),(255,255,0),)
            cv2.imwrite('static/jpg/dart_line_{}.jpg'.format(self.src),imgAf)
            return p1, p2
            
        elif format == 'point':
            ctn_pts = self.get_dart_cnt(diffBlur)
            pos = self.get_tip_pos(cnt_pts, line, width)

            #Testing
            cv2.drawMarker(imgAf, (int(pos[0]), int(pos[1])), color=(0, 76, 252), markerSize = 40, thickness = 2)
            cv2.imwrite('static/jpg/dart_pt_{}.jpg'.format(self.src),imgAf)
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
    def get_dart_box(diff):

        height, width = diff.shape[:2]
        
        # Get binary image
        ret, binary_img = cv2.threshold(diff,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Important threshold
        height, width = diff.shape[:2]

        #Remove small objects
        min_size = height * 0.06

        # Get contours
        #kernel = np.ones((int(height * 0.05),int(width * 0.05)),np.float32)
        #binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)
        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #Concatenate all cnt points
        cnt_pts = None
        for cnt in contours:
            if cv2.contourArea(cnt) > min_size:
                if cnt_pts is None:
                    cnt_pts = cnt
                else:
                    cnt_pts = np.concatenate((cnt_pts,cnt), axis=0)

        # Create bounding box
        center,(width,height),theta = cv2.minAreaRect(cnt_pts)

        # Increase size
        inc = 2 #Important threshold
        height = height * inc
        width = width * inc
        rect = center,(width,height),theta

        box = cv2.boxPoints(rect)
        box = np.int0(box)

        return box

    #@staticmethod
    def get_dart_cnt(self, diff):
        #currently unused
        
        #Testing
        #cv2.imwrite('static/jpg/diff_{}.jpg'.format(self.src), diff)

        height, width = diff.shape[:2]

        # Get binary image
        ret, binary_img = cv2.threshold(diff, 60, 255, 0) #Important threshold
        #Testing
        #cv2.imwrite('static/jpg/binary_{}.jpg'.format(self.src), binary_img)

        # Get contours
        kernel = np.ones((int(height * 0.15),int(width * 0.075)),np.float32) #Important thresholds
        binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)
        #Testing
        #cv2.imwrite('static/jpg/morph_{}.jpg'.format(self.src), binary_img)
        contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        #Testing
        #contour_img = cv2.drawContours(diff, contours, -1, (255,255,255), 3)
        #cv2.imwrite('static/jpg/contour_{}.jpg'.format(self.src), contour_img)

        cnt_pts = None
        for cnt in contours:
            if cv2.contourArea(cnt) > 50:
                if cnt_pts is None:
                    cnt_pts = cnt
                else:
                    cnt_pts = np.concatenate((cnt_pts,cnt), axis=0)

        return cnt_pts

    @staticmethod
    def get_line_old(diff, cnt_pts):
        #currently unused

        height, width = diff.shape[:2]

        # Filter features by drawing line through them
        max_iter = 3 #limited to avoid infinite loops
        for _ in range(max_iter):
            [vx, vy, x0, y0] = cv2.fitLine(cnt_pts, cv2.DIST_L2, 0, 0.1, 0.1) #dist_L1 cost function is p(r)=r, dist_L2 cost function is p(r)=r^2
            line = [vx, vy, x0, y0]
            lefty = int((-x0 * vy / vx) + y0)
            righty = int(((width - x0) * vy / vx) + y0)

            pts_to_delete = []
            i = 0
            p1 = np.array([0,lefty])
            p2 = np.array([width-1, righty])
            for pt in cnt_pts:
                x, y = pt.ravel()

                # check distance to fitted line, only draw corners within certain range
                p3 = np.array([x,y])
                distance = abs(np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))
                if distance > width * 0.05:  # threshold important
                    pts_to_delete.append(i)

                i += 1
            if pts_to_delete ==[]:
                break

            cnt_pts = np.delete(cnt_pts, [pts_to_delete], axis=0)  # delete corners to form new array

        return line

    @staticmethod
    def get_line(diff, box_dart):

        height, width = diff.shape[:2]

        mask = np.zeros_like(diff)
        cv2.fillPoly(mask,pts=[box_dart],color=255)

        features = cv2.goodFeaturesToTrack(diff, 640, 0.001, 1, mask=mask, blockSize=3, useHarrisDetector=1, k=0.06) #sensible: 0.0004, medium: 0.0008, conservative: 0.001

        # Filter features by drawing line through them
        max_iter = 1
        for _ in range(max_iter):
            [vx, vy, x0, y0] = cv2.fitLine(features, cv2.DIST_HUBER, 0, 0.1, 0.1) #dist_L1 cost function is p(r)=r, dist_L2 cost function is p(r)=r^2
            line = [vx, vy, x0, y0]
            lefty = int((-x0 * vy / vx) + y0)
            righty = int(((width - x0) * vy / vx) + y0)

            features_to_delete = []
            i = 0
            p1 = np.array([0,lefty])
            p2 = np.array([width-1, righty])
            for feature in features:
                x, y = feature.ravel()

                # check distance to fitted line, only draw corners within certain range
                p3 = np.array([x,y])
                distance = abs(np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))
                if distance > width * 0.05:  # threshold importantwhile True:
                    features_to_delete.append(i)

                i += 1
            if features_to_delete ==[]:
                break

            features = np.delete(features, [features_to_delete], axis=0)  # delete corners to form new array

        return line

if __name__ == '__main__':
    dart = dartThrow('static/jpg/before.jpg', 'static/jpg/after.jpg')
    p1, p2 = dart.get_position(format = 'line')
    print(p1)
    print(p2)