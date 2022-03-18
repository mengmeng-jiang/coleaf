#!/usr/bin/env python

import cv2 as cv
from imutils.perspective import four_point_transform
import numpy as np
import imutils
import sys
import os.path as op

#count the leaf erea
def edge_demo(image,img_name,output_txt):
    hig,len,channel=image.shape 
    if hig < 1000:
        brurred = cv.GaussianBlur(image, (5, 5), 0)
    else:
        brurred = cv.GaussianBlur(image, (7, 7), 0)
    gray = cv.cvtColor(brurred, cv.COLOR_BGR2GRAY)
    edgo_output = cv.Canny(gray, 25, 150)
    kernel = np.ones((3,3), np.uint8)
    closing =cv.morphologyEx(edgo_output, cv.MORPH_CLOSE, kernel)
    #cv.imwrite("canny.jpg", closing)
    # closing[int(0.4668*hig):int(0.4865*hig),0:len] = [0]
    # closing[int(0.9524*hig):int(0.9754*hig),0:len] = [0]
    # closing[0:int(0.02*hig),0:len] = [0]
    # closing[0:hig,int(0.3165*len):int(0.3355*len)] = [0]
    # closing[0:hig,int(0.6605*len):int(0.6775*len)] = [0]
    # cv.imwrite("countour.jpg", closing)
    cloneImage, contours, heriachy = cv.findContours(closing, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contour_img = cv.drawContours(image, contours, -1, (255, 255, 255), 2)
    i = 0
    for contour in contours:   
        area = cv.contourArea(contour)
        if area >= int(0.001*hig*len):
            i+=1
            print(i)
            perimeter = cv.arcLength(contour, True)
            x1, y1, w1, h1 = cv.boundingRect(contour)
            cv.rectangle(image, (x1, y1), (x1+w1, y1+h1), (0, 0, 255), 2)
            M = cv.moments(contour)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            center = (cx,cy)
            cv.circle(image,center, 5, (0, 255, 255), -1)
            rate = round(max(w1,h1)/min(w1,h1), 1)

            (leftx,lefty) = tuple(contour[contour[:,:,0].argmin()][0])
            cv.circle(image,(leftx,lefty), 5, (125, 255, 255), -1)
            (rightx,righty) = tuple(contour[contour[:,:,0].argmax()][0])
            cv.circle(image,(rightx,righty), 5, (125, 255, 255), -1)
            (topx,topy) = tuple(contour[contour[:,:,1].argmin()][0])
            (bottox,bottoy) = tuple(contour[contour[:,:,1].argmax()][0])            
            len1 = int(bottoy) - int(topy) 
            len2 = int(bottoy) - int(lefty)
            leftRate = int(len2)/int(len1)
            #print(leftRate)
            len3 = int(bottoy) - int(cy)
            centerRate = int(len3)/int(len1)
            #print(centerRate)
            
            if rate <= 2.0 :
                shape = 0
            elif rate > 2.0 and rate <= 2.5:
                shape = 3
            elif rate > 2.5 and rate <= 3.0:
                shape = 4
            elif rate > 3.0 and rate <= 10.0:
                shape = 5
            else:
                shape = 6
            rect = cv.minAreaRect(contour)
            box = cv.cv.BoxPoints() if imutils.is_cv2()else cv.boxPoints(rect)
            box = np.int0(box)
            cv.drawContours(image, [box], 0, (242,175,54), 2)
            #print(i,h1,h2,hig)
            x2,y2=(box[0])
            if i <= 9: 
                text_i = "0%s"%i
            elif i > 9:
                text_i = "%s"%i
            text_x = np.int(x2)
            text_y = np.int(y2+30)
            location = (text_x,text_y)
            cv.putText(image, text_i, location, cv.FONT_HERSHEY_COMPLEX, 1.0, (0,0,0),3)
            print("%s\t%s\t%.2f\t%.2f\t%.2f\t%i\t%.2f\t%.2f"%(img_name,text_i,perimeter,area,rate,shape,leftRate,centerRate), file=output_txt)
        else:
            print("the area " + str(area) + " is too little to countect")
    output_img = img_name + "_o.jpg"
    cv.putText(image, img_name, (30,30), cv.FONT_HERSHEY_COMPLEX, 1.0, (0,0,0), 3)
    cv.imwrite(output_img, image)
    return


    
print("--------")
img_name = "xiufu"
output_img = img_name + "_o.jpg"
output_txt = img_name + "_o.txt"
src = cv.imread("D:\JMW\Python\picture_data\/xiufu.jpg")
with open(output_txt, "w")as f1:
    print("#sample\tleaf\tcontourPerimeter\tcontourArea\trectangleRate\tshape\tleftRate\tcenterRate", file=f1)
    edge_demo(src, img_name,f1)
