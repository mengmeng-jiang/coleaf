#!/usr/bin/env python

import sys
import os.path as op
import math
import cv2 as cv
import numpy as np

from imutils.perspective import four_point_transform

#remove the reflections
def remove_reflections(image): 

    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV) #change to HSV
    h, s, v = cv.split(hsv)
    _, mask = cv.threshold(v, 220, 255, cv.THRESH_BINARY) #use v to find reflection
    dst2 = cv.inpaint(image, mask, 5, cv.INPAINT_TELEA)
    print("remove reflection down well")    
    return dst2


#crop the background
#reference1:https://pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
#reference2:https://pyimagesearch.com/2014/09/01/build-kick-ass-mobile-document-scanner-just-5-minutes/
def edge_crop(image,real_height, real_length,outpath,imgname):

    real_rate = round(real_height/real_length, 2)
    print("real_rate:" + str(real_rate))
    brurred = cv.GaussianBlur(image, (5, 5), 0)
    gray = cv.cvtColor(brurred, cv.COLOR_BGR2GRAY)
    #mimg = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,15,10)
    thr, mimg = cv.threshold(gray, 160, 255, cv.THRESH_BINARY)
    kernel = np.ones((5,5),np.uint8)
    opening = cv.morphologyEx(mimg, cv.MORPH_OPEN, kernel) 
    edgo_output = cv.Canny(opening, 75, 150) 
    # cv.imwrite("threshold.jpg", gray)
    # cv.imwrite("edgo.jpg", edgo_output)
    # cv.imwrite("dilation.jpg", canny_out)
    height1, length1 = edgo_output.shape
    print(height1*length1)
    cloneImage, contours, heriachy = cv.findContours(edgo_output, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    def cnt_area(cnt):
        area = cv.contourArea(cnt)
        return area
    contours.sort(key = cnt_area, reverse=True)
    contour_img = cv.drawContours(edgo_output, contours[0], -1, (255, 255, 255), 2)
    #cv.imwrite("contour.jpg", contour_img)
    print(cv.contourArea(contours[0]))
    #res = []
    for contour in contours[:5]:
        area = cv.contourArea(contour)
        #res.append(area)
        if area >= int(height1*length1/5):
            print("i have found the papare")
            epsilon = 0.1 * cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, epsilon, True)
            #print(approx)
            hull = cv.convexHull(approx)
            #print(hull)
            # hull_img = cv.polylines(image, [hull], True, (0, 255, 0), 2) #绘制绿框
            # outhull = op.join(outpath, imgname+"_hull.jpg")
            # cv.imwrite(outhull, hull_img)
            def get_dist(p1,p2):
                distance=math.pow((p1[0]-p2[0]),2) + math.pow((p1[1]-p2[1]),2)
                distance=math.sqrt(distance)
                return distance
            right = (hull[0])[0]
            down = (hull[1])[0]
            left = (hull[2])[0]
            up = (hull[3])[0]
            counter_height = max(get_dist(up, right), get_dist(left,down))
            counter_height = round(counter_height)

            counter_length = max(get_dist(right,down), get_dist(left, up))            
            counter_length = round(counter_length) 

            if len(hull) == 4:
                if counter_length >= counter_height:
                    length2 = counter_length
                    height2 = round(length2*real_rate)
                    pts1 = np.float32([left,up,right,down])
                    pts2 = np.float32([[0,0],[length2,0],[length2,height2],[0,height2]])
                    m = cv.getPerspectiveTransform(pts1,pts2)
                    dst=cv.warpPerspective(image,m,(length2,height2))
                    crop_rate = round(height2/length2,2)
                if counter_length < counter_height:
                    height2 = counter_height
                    length2 = round(height2*real_rate)
                    pts1 = np.float32([up,right,down,left])
                    pts2 = np.float32([[0,0],[height2,0],[height2,length2],[0,length2]])
                    m = cv.getPerspectiveTransform(pts1,pts2)
                    dst=cv.warpPerspective(image,m,(height2,length2))
                    crop_rate = round(length2/height2,2)
                print("crop_rate: " + str(crop_rate))
                #dst = four_point_transform(image, approx.reshape(height2,length2))
                print("you did a great job")
                return dst
            else:
                print(" The four points of the  contour cannot be obtained.")
                #print(" try to change a flat sheet of paper, and make sure here is only one papare ")
                return image
            #break
        else:
            print(" Eligible contour cannot be obtained, get closer to get the photo and try again ")

            return image



def main(image_path, crop=False, height=21, length=29.7, reflections=False, outdir=None):
    print("----------")
    image = cv.imread(image_path)
    
    #if imgname is None:
    imgname = op.basename(image_path)
    name = op.splitext(imgname)[0]
    if outdir is None:
        outpath = op.dirname(image_path)
    else:
        outpath = outdir
    
    tip = "_i"
    if crop is True:
        image = edge_crop(image,height,length,outpath,imgname)
        tip = "_c"
    if reflections is True:
        image = remove_reflections(image)
        tip = "_r"

    if crop is True and reflections is True:
        tip = "_p"

    outname = op.join(outpath, name + tip + ".jpg")
    cv.imwrite(outname, image)

# if __name__ == "__main__":
#     main(sys.argv[1], True, True)
