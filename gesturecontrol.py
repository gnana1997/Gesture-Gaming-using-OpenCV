#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 20:42:01 2020
@author: Gnana Murthiy
@description: Game controlling with Fists in Navy blue gloves using openCV. Left Fist- Break Righ Fist- acceleration
This code is inspired by a project, by Patel Digant: https://github.com/pateldigant/gesture-gaming-python 
Custom Logic was written to handle both the keys simultaneously for gaming requirements.
"""

from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
from directkeys import right_pressed,left_pressed
from directkeys import PressKey, ReleaseKey 


break_key_pressed=left_pressed
accelerato_key_pressed=right_pressed

# define the lower and upper boundaries of the "navy blue" object in the HSV color space
#https://stackoverflow.com/questions/36817133/identifying-the-range-of-a-color-in-hsv-using-opencv
blueLower = np.array([110, 40, 40])
blueUpper = np.array([130,255,255])

vs = VideoStream(src=0).start()
 
# allow the camera or video file to warm up
time.sleep(2.0)
initial = True
flag = False
current_key_pressed = set()
circle_radius = 30
windowSize = 160
lr_counter = 0

# keep looping
break_pressed=False
accelerator_pressed=False
while True:
    keyPressed = False
    break_pressed=False
    accelerator_pressed=False
    # grab the current frame
    frame = vs.read()
    height,width = frame.shape[:2]
 
    #Flipped the frame so that left hand appears on the left side and right hand appears on the right side
    frame = cv2.flip(frame,1);
    
    # resize the frame, blur it, and convert it to the HSV color space
    frame = imutils.resize(frame, height=300)
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # crteate a mask for the orange color and perform dilation and erosion to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, blueLower, blueUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
 
    # find contours in the mask and initialize the current
    # (x, y) center of the orange object

    # divide the frame into two halves so that we can have one half control the acceleration/brake 
    # and other half control the left/right steering.
    left_mask = mask[:,0:width//2,]
    right_mask = mask[:,width//2:,]

    #find the contours in the left and right frame to find the center of the object
    cnts_left = cv2.findContours(left_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_left = imutils.grab_contours(cnts_left)
    center_left = None

    cnts_right = cv2.findContours(right_mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts_right = imutils.grab_contours(cnts_right)
    center_right = None
    # only proceed if at least one contour was found
    key_count=0
    key_pressed=0
    if len(cnts_left) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and centroid
        c = max(cnts_left, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        # find the center from the moments 0.000001 is added to the denominator so that divide by 
        # zero exception doesn't occur
        center_left = (int(M["m10"] / (M["m00"]+0.000001)), int(M["m01"] / (M["m00"]+0.000001)))
        #print("center_left",center_left)
        # only proceed if the radius meets a minimum size
        if radius > circle_radius:
            # draw the circle and centroid on the frame,
            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 0, 255), 2)
            cv2.circle(frame, center_left, 5, (0, 0, 255), -1)
            #Bottom Left region
            if center_left[1] > 250:
                cv2.putText(frame,'Break Applied',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
                PressKey(break_key_pressed)
                break_pressed=True
                current_key_pressed.add(break_key_pressed)
                #Break key- 75 #Acc key-77
                key_pressed=break_key_pressed
                keyPressed = True
                key_count=key_count+1
    # only proceed if at least one contour was found
    if len(cnts_right) > 0:
        c2 = max(cnts_right, key=cv2.contourArea)
        ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
        M2 = cv2.moments(c2)
        center_right = (int(M2["m10"] / (M2["m00"]+0.000001)), int(M2["m01"] / (M2["m00"]+0.000001)))
        center_right = (center_right[0]+width//2,center_right[1])
        # only proceed if the radius meets a minimum size
        if radius2 > circle_radius:
            cv2.circle(frame, (int(x2)+width//2, int(y2)), int(radius2),
                (0, 255, 0), 2)
            cv2.circle(frame, center_right, 5, (0, 255, 0), -1)
            #Bottom Right region
            if center_right[1] >250 :
                cv2.putText(frame,'Acc. Applied',(350,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)
                PressKey(accelerato_key_pressed)
                key_pressed=accelerato_key_pressed
                accelerator_pressed=True
                keyPressed = True
                current_key_pressed.add(accelerato_key_pressed)
                key_count=key_count+1
    
    frame_copy=frame.copy()
    #Bottom left region rectangle
    frame_copy = cv2.rectangle(frame_copy,(0,height//2 ),(width//2,width),(255,255,255),1)
    cv2.putText(frame_copy,'Break',(10,280),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)
    #Bottom right region rectangle
    frame_copy = cv2.rectangle(frame_copy,(width//2,height//2),(width,height),(255,255,255),1)
    cv2.putText(frame_copy,'Acceleration',(330,280),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)

    # show the frame to our screen
    cv2.imshow("Frame", frame_copy)

    #If part: We need to release the pressed key if none of the key is pressed else the program will keep on sending
    #Else part:If different keys(Only one key in each frame) are pressed in previous and current frames, then we must
    #release previous frame key, Also release the key in current frame key for smoother control
    if not keyPressed and len(current_key_pressed) != 0:
        for key in current_key_pressed:
            ReleaseKey(key)
        current_key_pressed = set()
    elif key_count==1 and len(current_key_pressed)==2:    
            for key in current_key_pressed:             
                if key_pressed!=key:
                    ReleaseKey(key)
            current_key_pressed = set()
            for key in current_key_pressed:
                ReleaseKey(key)
            current_key_pressed = set()
        
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
 

vs.stop() 
# close all windows
cv2.destroyAllWindows()