import cv2
import numpy as np

class dartThrow:

    def __init__(self, img_before_link, img_after_link, board) :
        self.img_before_link = img_before_link
        self.img_after_link = img_after_link
        self.board = board
        self.is_dart = self.is_dart()

        if self.is_dart:
            self.rel_carth_pos = self.get_rel_pos()
            self.score = self.board.get_score(self.rel_carth_pos)

    def __repr__(self):
        return 'RelCarth Pos: {} \n\nStd Carth Pos: {} \n'\
            .format(self.rel_carth_pos, self.std_carth_pos)

    def is_dart(self):
        # Fake implementation to test other functions
        return True

    def get_rel_pos(self):

        img_bf = cv2.imread(self.img_before_link)
        img_af = cv2.imread(self.img_after_link)

        diff = cv2.absdiff(img_bf, img_af)
        height, width = diff.shape[:2]

        # transform to gray scale
        diffGray = cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)

        # add blur
        kernel = np.ones((5,5),np.float32)/25
        diffBlur = cv2.filter2D(diffGray,-1,kernel)

        # First step: Find dart -> Use contours to find bounding box around dart
        # Find contours
        diffCnts = diffBlur.copy()
        ret, thresh = cv2.threshold(diffCnts, 30, 255, 0) #Important threshold
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        diffCnts = cv2.cvtColor(diffBlur, cv2.COLOR_GRAY2BGR)
        img = cv2.drawContours(diffCnts, contours, -1, (255,255,255), 2)

        bnds = {'top':height, 'left':width, 'right':0, 'bottom':0}

        # computes the bounding box for all contours
        for contour in contours:
            (x,y,w,h) = cv2.boundingRect(contour)
            bnds['left'], bnds['right'] = min(x, bnds['left']), max(x+w, bnds['right'])
            bnds['top'], bnds['bottom'] = min(y, bnds['top']), max(y+h, bnds['bottom'])
        
        #2. Step: Sensible feature detection inside the detecting bounding box

        #Increase box boundaries
        change_sides = {'top':-50, 'left':-20, 'right':20, 'bottom':0}
        for k in bnds.keys():
            bnds[k]=bnds[k]+change_sides[k]

        #For testing
        if bnds['right'] - bnds['left'] > 0 and bnds['bottom'] - bnds['top'] > 0:
            cv2.rectangle(diffCnts, (bnds['left'], bnds['top']), (bnds['right'], bnds['bottom']), (255, 0, 0), 2)

        diffFeat = diffBlur.copy()[bnds['top']:bnds['bottom'], bnds['left']:bnds['right']]

        #For testing
        diffFeatFiltered = diffBlur.copy()[bnds['top']:bnds['bottom'], bnds['left']:bnds['right']]

        features = cv2.goodFeaturesToTrack(diffFeat, 640, 0.0008, 1, mask=None, blockSize=3, useHarrisDetector=1, k=0.06)

        #For testing
        for feature in features:
            x,y = feature.ravel()
            cv2.circle(diffFeat,(x,y),3,255,-1)

        # 3. Step Filter features by drawing line through them
        iteration_count = 1
        while True:
            [vx, vy, x, y] = cv2.fitLine(features, cv2.DIST_HUBER, 0, 0.1, 0.1) #dist_L1 cost function is p(r)=r, dist_L2 cost function is p(r)=r^2
            lefty = int((-x * vy / vx) + y)
            righty = int(((width - x) * vy / vx) + y)

            features_to_delete = []
            i = 0
            p1 = np.array([0,lefty])
            p2 = np.array([width-1, righty])
            for feature in features:
                x, y = feature.ravel()

                # check distance to fitted line, only draw corners within certain range
                p3 = np.array([x,y])
                distance = abs(np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))
                if distance > 10:  # threshold important -> make accessible
                    features_to_delete.append(i)

                i += 1
            if features_to_delete ==[]:
                break

            features = np.delete(features, [features_to_delete], axis=0)  # delete corners to form new array

        #For testing
        for feature in features:
            x,y = feature.ravel()
            cv2.circle(diffFeatFiltered,(x,y),3,255,-1)


        # 4th Step: Find most top feature which is close to line -> is dart tip
        min_y = height
        corr_x = None  # Corresponding coordinate
        p1 = np.array([0,lefty])
        p2 = np.array([width-1, righty])
        # Find most top feature
        for feature in features:
            x,y = feature.ravel()
            p3 = np.array([x,y])
            distance = abs(np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))
            if y < min_y and distance < 5: # threshold important -> make accessible
                min_y = y
                corr_x = x
        
        x_out, y_out = bnds['left'] + corr_x, bnds['top'] + min_y

        #For testing
        cv2.circle(diffFeat,(corr_x,min_y),5,100,-1)

        cv2.line(diffFeatFiltered,(0,lefty),(width-1,righty),(255,255,0),3)

        path_out = 'static/jpg/'
        cv2.drawMarker(img_af, (int(x_out), int(y_out)), color=(0, 76, 252), markerSize = 40, thickness = 2)
        cv2.imwrite(path_out + 'rec_dart.jpg',img_af)
        cv2.imwrite(path_out + 'features_line_filtered.jpg',diffFeatFiltered)
        cv2.imwrite(path_out + 'contours.jpg',diffCnts)
        cv2.imwrite(path_out + 'features.jpg',diffFeat)
        print(x_out, y_out)

        return [x_out, y_out]
