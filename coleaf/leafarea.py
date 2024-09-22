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

# import matplotlib.image as img
import pandas as pd
from scipy.cluster.vq import whiten, kmeans,vq
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

#Calculate the leaf erea


def calc_photo(image,outpath):
    height2, length2, channel=image.shape
    print("original :" + str(height2), str(length2))
    while height2 > 1000:
        image = cv.resize(image, None, fx=0.8, fy=0.8,interpolation=cv.INTER_LINEAR )

        height2, length2,chennel=image.shape

    
    brurred = cv.bilateralFilter(image, 0, 170, 15)
    gray = cv.cvtColor(brurred, cv.COLOR_BGR2GRAY)

    edgo_output = cv.Canny(gray, 50, 100)
    kernel = np.ones((3, 3), np.uint8)
    closing =cv.morphologyEx(edgo_output, cv.MORPH_CLOSE, kernel)
    return brurred, closing


def calc_scanned(image,outpath):
    height2, length2, channel=image.shape
    while height2 > 1000:
        image = cv.resize(image, None, fx=0.8, fy=0.8,interpolation=cv.INTER_LINEAR )
        height2, length2,chennel=image.shape
    lab=cv.cvtColor(image, cv.COLOR_BGR2LAB)
    l,a,b = cv.split(lab)
    ret, thesh = cv.threshold(b, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    kernel = np.ones((9, 9), np.uint8)
    closing = cv.morphologyEx(thesh, cv.MORPH_CLOSE, kernel)
    return closing


#the color space is BGR
def measure_object(original_img, closing_img, background, name, outpath, output_img, f1):  
    height2, length2, channel=original_img.shape
    closing_img = cv.resize(closing_img, (length2,height2), interpolation = cv.INTER_LINEAR )
    closing_img[0:int(0.01*height2),0:length2] = [0]
    closing_img[int(0.99*height2):height2,0:length2] = [0]
    closing_img[0:height2,0:int(0.01*length2)] = [0]
    closing_img[0:height2,int(0.99*length2):length2] = [0]

    print("after :" + str(height2), str(length2))
    outImage, contours, heriachy = cv.findContours(closing_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    mask = np.zeros(closing_img.shape, np.uint8)
    cv.drawContours(mask,contours,-1,255,-1)
    masked = cv.bitwise_and(original_img, original_img, mask=mask)
    Z = masked.reshape((-1,3))  
    Z = Z[(Z!=0).any(axis=1)]
    Z = np.float32(Z)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    K = 3
    ret,cluster,Kcenter=cv.kmeans(Z,K,None,criteria,10,cv.KMEANS_RANDOM_CENTERS)
    Kcenter = np.uint8(Kcenter)

    Kcenter_list=list(map(tuple, Kcenter))
    cluster1= cluster.flatten()
    color_number=np.bincount(cluster1)
    color_proportion=color_number/sum(color_number)
    color_proportion2=np.around(color_proportion,decimals=3)

    color_dict = dict(zip(Kcenter_list, color_proportion2))
    color_dict = dict(sorted(color_dict.items(), key=lambda x: x[1], reverse=True))
    #print(color_dict)
    color_max=max(color_dict,key=color_dict.get)
    (max_B,max_G,max_R)=color_max
    print(color_max)

    mask = np.zeros(closing_img.shape, np.uint8)
    cv.drawContours(mask,contours,-1,255,-1)
    contour_img = cv.drawContours(original_img, contours, -1, (50, 214, 241), 2)
  
    i = 0
    for contour in contours:      
        area = cv.contourArea(contour)
        if area >= round(0.001*height2*length2) and area < round(0.7*height2*length2):
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
            
            rect = cv.minAreaRect(contour)
            min_h=max(rect[1][0], rect[1][1]) 
            min_w=min(rect[1][0], rect[1][1])
        
            box = cv.cv.BoxPoints() if imutils.is_cv2()else cv.boxPoints(rect)
            box = np.int0(box)
            cv.drawContours(contour_img, [box], 0, (67, 93, 220), 2)
            
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
                shape = 3
            elif rate > 2.50 and rate <= 3.00:
                shape = 4
            elif rate > 3.00 and rate <= 10.00:
                shape = 5
            else:
                shape = 6

            if i <= 9: 
                text_i = "0%s"%i
            elif i > 9:
                text_i = "%s"%i
            text_x = np.int(x1)
            text_y = np.int(y1+h1+30)
            location = (text_x,text_y)
            cv.putText(contour_img, text_i, location, cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0), 3)
            print("%s\t%s\t%.2f\t%.2f\t%.3f\t%.2f\t%i\t%i\t%.2f\t%i\t%s"%(
                name,text_i,perimeter,area,realrate,realarea,leaf_length,leaf_width,rate,shape,color_max), file=f1)
        else:
            print("the area " + str(area) + " is too little to countect")

    x2 = int(0.01*length2)
    y2 = int(0.05*height2)
    x3 = int(0.03*length2)
    for key, value in color_dict.items():
        print(key)
        print(value)
        leftup = (x2,y2)
        color_size=int(0.2*height2)
        y3 = y2 + int(value*color_size)
        rightdown = (x3,y3)
        key_color=tuple((int(x) for x in key))
        cv.rectangle(contour_img,leftup,rightdown,key_color,-1)
        y2 = y3
    cv.putText(contour_img, name, (int(0.01*length2), int(0.04*height2)), cv.FONT_HERSHEY_COMPLEX, 1.0, (0,0,0), 3)
    outimg_path = op.join(outpath, output_img)
    cv.imwrite(outimg_path, contour_img)
    print("the area calculation succeeded! ")
    return



#def main(image_path, img_type, height1=21, length1=29.7, img_name=None, outdir=None):
def main(args, height1=21, length1=29.7, img_name=None, outdir=None):
    image_path, img_type = args
    
    background = height1*length1
    print(image_path, background)
    if img_name is None:
        imgname = op.basename(image_path)
        allname = op.splitext(imgname)[0]
    else:
        allname = img_name
    output_img = allname + "_o.jpg"
    output_txt = allname + "_o.txt"
    if outdir is None:
        outpath = op.dirname(image_path)
    else:
        outpath = outdir
    outtxt_path = op.join(outpath, output_txt)
     
    image = cv.imread(image_path)
    if img_type == "photo":
        brurred, closing = calc_photo(image,outpath)
    elif img_type == "scanned":
        closing = calc_scanned(image,outpath)
    with open(outtxt_path, "w")as f1:
        print("#sample\tleaf\tcontourPerimeter\tcontourArea\trealrate\trealarea\tleaf_length\tleaf_width\trate\tshape\tcolor", file=f1)
        measure_object(image, closing, background, allname, outpath, output_img, f1)

#if __name__=="__main__":
#    if len(sys.argv) < 3:
#        print('usage: python leaf_area.py <image_path_name> <img_type>')
#        sys.exit()

#    main(sys.argv[1:])

