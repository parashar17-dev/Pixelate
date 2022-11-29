import cv2.aruco as aruco
import cv2
import math

class GetAruco:
    
    def __init__(self, img, dest):
        self.img= img
        self.dest= dest

    def angle(self, vector1, vector2):
        x1, y1 = vector1
        x2, y2 = vector2
        inner_product = x1*x2 + y1*y2
        len1 = math.hypot(x1, y1)
        len2 = math.hypot(x2, y2)
        return math.acos(inner_product/(len1*len2))
        
    def detectAruco(self):

        # Constant parameters used in Aruco methods
        ARUCO_PARAMETERS = aruco.DetectorParameters_create()
        ARUCO_DICT = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)


        # Create grid board object we're using in our stream
        board = aruco.GridBoard_create(
                markersX=2,
                markersY=2,
                markerLength=0.09,
                markerSeparation=0.01,
                dictionary=ARUCO_DICT)


        # Create vectors we'll be using for rotations and translations for postures
        rvecs, tvecs = None, None

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        #Detect Aruco markers
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMETERS)

        if ids is None:
            return 0,0,0

        xs=0
        ys=0
        cnrs= corners[0][0]
        for i in range(0,4):
            xs=xs+cnrs[i][0]

        for i in range(0,4):
            ys=ys+cnrs[i][1]


        x1= (cnrs[0][0]+cnrs[1][0])/2
        y1= (cnrs[0][1]+cnrs[1][1])/2

        x2= (cnrs[2][0]+cnrs[3][0])/2
        y2= (cnrs[2][1]+cnrs[3][1])/2

        pt1 = (0.0, ys/4)
        pt2 = (x1-xs/4, ys/4-y1)
        ang1 = math.degrees(self.angle(vector1=pt1, vector2=pt2))
        if(x1<xs/4):
            ang1=ang1*-1

        pt3 = (self.dest[0]-xs/4, ys/4-self.dest[1])
        ang2 = math.degrees(self.angle(vector1=pt3, vector2=pt1))
        if(self.dest[0]<xs/4):
            ang2=ang2*-1

        ang = ang2-ang1
        if(ang>180):
            ang = (360-ang)*-1

        if(ang<-180):
            ang = (360+ang)

        dis = math.sqrt( (xs/4-self.dest[0])**2 + (ys/4-self.dest[1])**2 )
        self.img = aruco.drawDetectedMarkers(self.img, corners, borderColor=(0, 0, 255))
        
        cv2.imwrite("media/aruco_detected.png", self.img)
        return dis,ang,[xs/4,ys/4]
