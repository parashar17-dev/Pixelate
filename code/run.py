import color_segment
import dijkstra

import gym
import pix_main_arena
import time
import pybullet as p
import pybullet_data
import cv2
import os
import numpy as np
import aruco
import math


#function to check whether the pateint is circle or square by checking the change in no circles and squares detected
def check_status(img,circle,square):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    l_b = np.array([100, 150, 0])
    u_b = np.array([140, 255, 255])
    maskB = cv2.inRange(hsv, l_b, u_b, )
    contoursB, hierarchy = cv2.findContours(maskB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contoursB, -1, (0, 0, 255), thickness=2)
    cv2.imshow("Image", img)
    Lb = list()
    squaret=0
    circlet=0
    triangle=0
    for cB in contoursB:
        approx = cv2.approxPolyDP(cB, 0.02 * cv2.arcLength(cB, True), True)
        if cv2.contourArea(cB)>250:
            if len(approx) == 3:
                triangle+=1
            elif len(approx) == 4:
                squaret+=1
            else:
                circlet+=1
    if(circlet>circle):
        return 0,circlet,squaret
    else:
        circle=circlet
        square=squaret
        return 1,circlet,squaret

#function to check the bot's position by aruco detection
def get_aruco(dest):
    get = env.camera_feed()
    get = get.astype(np.uint8).copy()
    dis,ang,cen = aruco.GetAruco(get,dest).detectAruco()
    while(dis==0 and ang==0 and cen==0):
            right(0)
            get = env.camera_feed()
            get = get.astype(np.uint8).copy()
            dis,ang,cen = aruco.GetAruco(get,dest).detectAruco()
    return dis,ang,cen

#function to move right
def right(ang):
    if ang==0:
        k=20
    else:
        k=max(math.ceil(ang*3),50)
    c=2
    for i in range(0,k):
        p.stepSimulation()
        env.move_husky(c, -1*c, c, -1*c)

#function to move left
def left(ang):
    k=max(math.ceil(ang*3),50)
    c=2
    for i in range(0,k):
        p.stepSimulation()
        env.move_husky(-1*c, c, -1*c, c)

#function to move forward by dis
def move(dis):
    k=max(math.ceil(3*dis),40)
    c=7
    for i in range(0,k):
        p.stepSimulation()
        env.move_husky(c, c, c, c)

def stop():
    p.stepSimulation()
    env.move_husky(0, 0, 0, 0)

#function to align the bot in the direction of dest
def align(dest):
    p=0
    dis,ang,cnrs = get_aruco(dest)
    while abs(ang)>5:
        dis,ang,cnrs = get_aruco(dest)
        if(ang>2.0):
            right(abs(ang))
        if(ang<-2.0):
            left(abs(ang))
        stop()

#function to make the bot travel to the current destination
def travel(dest):
    dis,ang,cnrs = get_aruco(dest)
    disprev=dis
    
    while dis>5:
        dis,ang,cnrs = get_aruco(dest)
        if(dis>disprev):
            break
        move(dis)
        disprev=dis
        stop()

#main logic
if __name__=="__main__":
    env = gym.make("pix_main_arena-v0")
    time.sleep(3)

    img = env.camera_feed()
    circle=1
    square=1
    img= img.astype(np.uint8).copy()

    #applying color segmentation for analysing the arena
    A = color_segment.img_process(img) 
    graphlist = A.graphlist
    mid = A.mid
    print("see")
    print(A.patients[0])
    print("triangles")
    print(A.triangles)
    print("circles")
    print(A.circles)
    print("squares")
    print(A.squares)

    #getting the graph for the arena
    graph = dijkstra.Graph(graphlist)

    path, cost1 = graph.dijkstra(143, A.patients[1][0])
    path, cost2 = graph.dijkstra(143, A.patients[0][0])

    patients = list()

    if(cost1<cost2):
        patients.append(A.patients[1][0])
        patients.append(A.patients[0][0])
    else:
        patients.append(A.patients[0][0])
        patients.append(A.patients[1][0])

    print(patients)
    print(patients[0])


    path, cost = graph.dijkstra(143, patients[0])
    print(path)
    last = path[-1]
    cur=143

    time.sleep(5)


    for i in path:
        print("coordinates of")
        print(i)
        print(mid[i//12,i%12])
        
        if(i == last):
            env.remove_cover_plate(i//12,i%12)
            see = env.camera_feed()
            see = see.astype(np.uint8).copy()
            x,circle,square = check_status(see,circle,square)
            if(x==0):
                print("first patient is a circle")
                next=0
            else:
                print("first patient is a square")
                next=1
            time.sleep(1)
        print("********")
        print("cur:",cur)
        print("dest:",i)
        
        align(tuple(mid[i//12,i%12]))
        travel(tuple(mid[i//12,i%12]))
        cur = i

    #######reached first patient#######
    #######reached first patient#######
    #######reached first patient#######

    if(next==0):
        path, cost = graph.dijkstra(cur, A.circles[0])
    else:
        path, cost = graph.dijkstra(cur, A.squares[0])
    
    print(path)
    last = path[-1]
    
    for i in path:
        if(cur==i):
            continue
        if(i == last):
            print("delivered first pateint to hostpital")
            time.sleep(1)
        print("********")
        print("cur:",cur)
        print("dest:",i)
        align(tuple(mid[i//12,i%12]))
        travel(tuple(mid[i//12,i%12]))
        #B.show()
        cur = i

    #######reached first hospital#######
    #######reached first hospital#######
    #######reached first hospital#######

    path, cost = graph.dijkstra(cur, patients[1])
    print(path)
    last = path[-1]

    for i in path:
        if(cur==i):
            continue
        if(i == last):
            env.remove_cover_plate(i//12,i%12)
            see = env.camera_feed()
            see = see.astype(np.uint8).copy()
            x,circle,square = check_status(see,circle,square)
            if(x==0):
                print("second patient is a circle")
                next=0
            else:
                print("second patient is a square")
                next=1
            time.sleep(1)
        print("********")
        print("cur:",cur)
        print("dest:",i)
        align(tuple(mid[i//12,i%12]))
        travel(tuple(mid[i//12,i%12]))
        #B.show()
        cur = i

    #######reached second patient#######
    #######reached second patient#######
    #######reached second patient#######

    if(next==0):
        path, cost = graph.dijkstra(cur, A.circles[0])
    else:
        path, cost = graph.dijkstra(cur, A.squares[0])

    print(path)
    last = path[-1]
    
    for i in path:
        if(cur==i):
            continue
        if(i == last):
            print("delivered second pateint to hostpital")
            time.sleep(1)
        print("********")
        print("cur:",cur)
        print("dest:",i)
        align(tuple(mid[i//12,i%12]))
        travel(tuple(mid[i//12,i%12]))
        #B.show()
        cur = i

    #######reached second hospital#######
    #######reached second hospital#######
    #######reached second hospital#######

    
    print("task completed")
    cv2.waitKey(0)
    time.sleep(1)
    time.sleep(100)