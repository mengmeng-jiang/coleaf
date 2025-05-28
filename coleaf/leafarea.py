#!/usr/bin/env python

from configparser import Interpolation
import sys
import os.path as op
import os

import cv2 as cv
from imutils.perspective import four_point_transform
import numpy as np
import imutils
import math

from plantcv import plantcv as pcv

#Calculate the leaf erea
def calc_photo(image):
    height2, length2, channel=image.shape
    print("original :" + str(height2), str(length2))
    while height2 > 1000:
        image = cv.resize(image, None, fx=0.8, fy=0.8,interpolation=cv.INTER_LINEAR )
        #brurred = cv.bilateralFilter(image, 0, 170, 15)
        height2, length2,chennel=image.shape
        # print(height2)
    
    brurred = cv.GaussianBlur(image, (5, 5), 0)
    gray = cv.cvtColor(brurred, cv.COLOR_BGR2GRAY)
    edgo_output = cv.Canny(gray, 25, 150)
    kernel = np.ones((3, 3), np.uint8)
    closing =cv.morphologyEx(edgo_output, cv.MORPH_CLOSE, kernel)

    return (closing)


def calc_scanned(image):
    height2, length2, channel=image.shape
    lab = pcv.rgb2gray_lab(rgb_img=image, channel="b")
    ret, thesh = cv.threshold(lab, 0, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    img_binary = pcv.threshold.binary(gray_img=lab, threshold=ret, max_value=255, object_type="light")
    kernel = np.ones((9, 9), np.uint8)
    closing = cv.morphologyEx(img_binary, cv.MORPH_CLOSE, kernel)
    return(closing)


#the color space is BGR
def measure_object(original_img, closing_img, background, name, outpath, output_img, f1):  
    height2, length2, channel=original_img.shape
    closing_img = cv.resize(closing_img, (length2,height2), interpolation = cv.INTER_LINEAR ) #缩小后放大
    print("after :" + str(height2), str(length2))
    outImage, contours, heriachy = cv.findContours(closing_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contour_img = cv.drawContours(original_img, contours, -1, (50, 214, 241), 2)

    i = 0
    for contour in contours:
        area = cv.contourArea(contour)
        if area >= round(0.005*height2*length2) and area < round(0.7*height2*length2):
            i+=1
            print(i)
            realrate = (height2*length2)/background
            realarea = area/realrate
            leftmost = tuple(contour[contour[:,:,0].argmin()][0])
            rightmost = tuple(contour[contour[:,:,0].argmax()][0])
            topmost = tuple(contour[contour[:,:,1].argmin()][0])
            bottommost = tuple(contour[contour[:,:,1].argmax()][0])
            cv.circle(contour_img, leftmost, 5, (255, 255, 0), -1)
            cv.circle(contour_img, rightmost, 5, (255, 255, 0), -1)
            cv.circle(contour_img, topmost, 5, (255, 255, 0), -1)
            cv.circle(contour_img, bottommost, 5, (255, 255, 0), -1)
            
            perimeter = cv.arcLength(contour, True)
            x1, y1, w1, h1 = cv.boundingRect(contour)
            cv.rectangle(contour_img, (x1, y1), (x1+w1, y1+h1), (250, 152, 56), 2)
            M = cv.moments(contour)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            center = (cx,cy)
            cv.circle(contour_img,center, 5, (255, 255, 0), -1)
            
            bound_h=max(w1, h1)
            bound_w=min(w1, h1)
            
            #attention, here I named width and height with length, rather than the angle seta.
            rect = cv.minAreaRect(contour)
            min_h=max(rect[1][0], rect[1][1]) #width has the larger length
            min_w=min(rect[1][0], rect[1][1])
            
            #rate2 = round(max(min_w, min_h) / min(min_w, min_h), 2)
            box = cv.cv.BoxPoints() if imutils.is_cv2()else cv.boxPoints(rect)
            box = np.int0(box)
            cv.drawContours(contour_img, [box], 0, (67, 93, 220), 2)
            
            #计算长宽比
            def get_dist(p1,p2):
                distance=math.pow((p1[0]-p2[0]),2) + math.pow((p1[1]-p2[1]),2)
                distance=math.sqrt(distance)
                return distance
            
            top2bot = get_dist(bottommost,topmost)
            lef2rig =  get_dist(rightmost,leftmost)
            if top2bot >= lef2rig:
                dif1=math.fabs(top2bot-bound_h)
                dif2=math.fabs(top2bot-min_h)
            else:
                dif1=math.fabs(lef2rig-bound_h)
                dif2=math.fabs(lef2rig-min_h)
            
            if dif1 < dif2:
                rate = round(bound_h / bound_w,2)
                leaf_length=bound_h
                leaf_width=bound_w
                cv.rectangle(contour_img, (x1, y1), (x1+w1, y1+h1), (0, 255, 0), 2)
            else:
                rate = round(min_h / min_w,2)
                leaf_length=min_h
                leaf_width=min_w
                cv.drawContours(contour_img, [box], 0, (0, 255, 0), 2)
            
            if rate <= 2.00:
                shape = 0
            elif rate > 2.00 and rate <= 2.50:
                shape = 1
            elif rate > 2.50 and rate <= 3.00:
                shape = 2
            elif rate > 3.00 and rate <= 10.00:
                shape = 3
            else:
                shape = 4

            #print(i,h1,h2,hig)
            

            if i <= 9: 
                text_i = "0%s"%i
            elif i > 9:
                text_i = "%s"%i
            text_x = np.int(x1)
            text_y = np.int(y1+h1+30)
            location = (text_x,text_y)
            cv.putText(contour_img, text_i, location, cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0), 3)
            print("%s\t%s\t%.2f\t%.2f\t%.3f\t%.2f\t%i\t%i\t%.2f\t%i"%(
                name,text_i,perimeter,area,realrate,realarea,leaf_length,leaf_width,rate,shape), file=f1)
        else:
            print("the area " + str(area) + " is too little to countect")
    cv.putText(contour_img, name, (30, 30), cv.FONT_HERSHEY_COMPLEX, 1.0, (0,0,0), 3)
    outimg_path = op.join(outpath, output_img)
    cv.imwrite(outimg_path, contour_img)
    print("the area calculation succeeded! ")
    return


def main(image_path, img_type, height1=21, length1=29.7, img_name=None, outdir=None):
    #print(height1,length1)
    background = height1*length1
    print(image_path, background)
    if img_name is None:
        imgname = op.basename(image_path)
        allname = op.splitext(imgname)[0]
        #name = allname.split("_")[0]
    else:
        allname = img_name
    #allname = name + "_"
    output_img = allname + "_o.jpg"
    output_txt = allname + "_o.txt"
    if outdir is None:
        outpath = op.dirname(image_path)
    else:
        outpath = outdir
    outtxt_path = op.join(outpath, output_txt)
     
    image = cv.imread(image_path)
    if img_type == "photo":
        closing = calc_photo(image)
        # closing_path = op.join(outpath, "closing.jpg")
        # cv.imwrite(closing_path,closing)
    elif img_type == "scanned":
        closing = calc_scanned(image)
    with open(outtxt_path, "w")as f1:
        print("#sample\tleaf\tcontourPerimeter\tcontourArea\trealrate\trealarealeaf_length\tleaf_width\trate\tshape", file=f1)
        #closing_img = cv.imread(closing, 0)
        measure_object(image, closing, background, allname, outpath, output_img, f1)


