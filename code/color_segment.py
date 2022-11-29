import gym
import pix_main_arena
import time
import pybullet as p
import pybullet_data
import cv2
import os
import numpy as np



class img_process:
    
    mid = np.zeros([12, 12, 2], dtype="uint16")
    graphlist = list()
    patients = list()
    triangles = list()
    squares = list()
    circles = list()


    def segment(self,lower,upper,value):
        mask = cv2.inRange(self.hsv, lower, upper, )
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        L = list()
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

            else:
                cX, cY = 0, 0

            R = int(cY / self.w)
            C = int(cX / self.h)
            B = R * 12 +C

            L.append([B, value])

        return L
    
    def __init__(self,img):
        r = cv2.selectROI("Crop arena", img)
        crop = img[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

        n = 12
        xf= (r[3])/n
        yf= (r[2])/n
        
        img= img.astype(np.uint8).copy()
        for i in range(0,12):
            for j in range(0,12):
                self.mid[i,j,1]=i*xf+(xf/2)+r[1]
                self.mid[i,j,0]=j*yf+(yf/2)+r[0]


        print(r)
        cv2.imshow("Image", crop)
        self.hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        gray_image = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        height = crop.shape[0]
        width = crop.shape[1]
        self.h = int(height / n)
        self.w = int(width / n)

        l_w = np.array([0, 0, 220])
        u_w = np.array([0, 0, 255])
        Lw = self.segment(l_w,u_w,1)

        l_g = np.array([35, 52, 72])
        u_g = np.array([70, 255, 255])
        Lg = self.segment(l_g,u_g,2)

        l_y = np.array([22, 93, 0])
        u_y = np.array([45, 255, 255])
        Ly = self.segment(l_y,u_y,3)

        l_r = np.array([0, 20, 10])
        u_r = np.array([10, 255, 255])
        Lr = self.segment(l_r,u_r,4)

        l_p = np.array([150, 100, 150])
        u_p = np.array([250, 153, 250])
        Lp = self.segment(l_p,u_p,9)
        for i in Lp:
            self.patients.append(i)

        l_b = np.array([100, 150, 0])
        u_b = np.array([140, 255, 255])
        maskB = cv2.inRange(self.hsv, l_b, u_b, )
        contoursB, hierarchy = cv2.findContours(maskB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(crop, contoursB, -1, (0, 0, 255), thickness=2)
        cv2.imshow("Image", crop)
        Lb = list()
        oneway = list()

        for cB in contoursB:
            MB = cv2.moments(cB)
            if MB["m00"] != 0:
                cXb = int(MB["m10"] / MB["m00"])
                cYb = int(MB["m01"] / MB["m00"])

            else:
                cXb, cYb = 0, 0

            Rb = int(cYb / self.w)
            Cb = int(cXb / self.h)
            Bb = Rb * 12 +Cb
            cv2.imshow("Image", crop)

            approx = cv2.approxPolyDP(cB, 0.02 * cv2.arcLength(cB, True), True)
            if cv2.contourArea(cB)>250:
                if len(approx) == 3:
                    self.triangles.append(Bb)
                    print("triangle at ",Bb)
                    print(approx)
                    print(cXb,cYb)
                    for k in approx:
                        if(k[0][0]<(cXb+4) and k[0][0]>(cXb-4)):
                            if(k[0][1]<cYb):
                                oneway.append([Bb,'U'])
                            else:
                                oneway.append([Bb,'D'])
                            break
                        elif(k[0][1]<cYb+4 and k[0][1]>cYb-4):
                            if(k[0][0]<cXb):
                                oneway.append([Bb,'L'])
                            else:
                                oneway.append([Bb,'R'])
                            break
                elif len(approx) == 4:
                    self.squares.append(Bb)
                    Lb.append([Bb, 500])
                else:
                    self.circles.append(Bb)
                    Lb.append([Bb, 500])

        print(oneway)

        Listall = Lg + Lr + Lw + Ly + Lb + Lp

        for i in Listall:
            if(i[0] == 143):
                Listall.remove(i)
        for i in Listall:
            if(i[0] == 143):
                Listall.remove(i)

        Listall.append([143,0])

        one_c = list()

        for i in oneway:
            for k in Listall:
                if(k[0]==i[0]):
                    one_c.append(k)

        sortedLw = sorted(Listall, key=lambda item: item[0])
        print("printing list")
        print(sortedLw)
        print("list printed")
        graph = sortedLw

        graph1 = sorted(graph, key=lambda item: item[1])
        destination = graph1[-1][0]

        R = n

        for i in oneway:
            cur = 0
            c = i[0]
            for k in one_c:
                if(k[0]==c):
                    cost=k[1]


            if(i[1]=='R'):
                for i, j in graph:
                    if (i == c + 1 and (c+1) % R != 0):
                        self.graphlist.append((c, c + 1, graph[cur][1]))
                    if (i == c - 1 and (c) % R != 0):
                        self.graphlist.append((c - 1, c, cost))
                    cur = cur + 1
            elif(i[1]=='L'):
                for i, j in graph:
                    if (i == c + 1 and (c+1) % R != 0):
                        self.graphlist.append((c + 1, c, cost))
                    if (i == c - 1 and (c) % R != 0):
                        self.graphlist.append((c, c - 1, graph[cur][1]))
                    cur = cur + 1
            elif(i[1]=='U'):
                for i, j in graph:
                    if (i == c + R):
                        self.graphlist.append((c + R, c, cost))
                    if (i == c - R):
                        self.graphlist.append((c, c - R, graph[cur][1]))
                    cur = cur + 1
            elif(i[1]=='D'):
                for i, j in graph:
                    if (i == c + R):
                        self.graphlist.append((c, c + R, graph[cur][1]))
                    if (i == c - R):
                        self.graphlist.append((c - R, c, cost))
                    cur = cur + 1
        
        print("oneway edges")
        print(self.graphlist)

        for i in oneway:
            for j in graph:
                if(j[0]==i[0]):
                    graph.remove(j)

        print(graph)

        r = len(graph)
        for i in range(0, r):
            cur = 0
            c = graph[i][0]
            for i, j in graph:

                if (i == c + 1 and (c+1) % R != 0):
                    self.graphlist.append((c, c + 1, graph[cur][1]))
                if (i == c - 1 and (c) % R != 0):
                    self.graphlist.append((c, c - 1, graph[cur][1]))
                if (i == c + R):
                    self.graphlist.append((c, c + R, graph[cur][1]))
                if (i == c - R):
                    self.graphlist.append((c, c - R, graph[cur][1]))
                cur = cur + 1

        print(self.graphlist)

    


