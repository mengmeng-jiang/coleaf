#!/usr/bin/env python
import sys
import cv2 as cv
import numpy as np

def clahe_demo(image, img_name):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    clahe = cv.createCLAHE(clipLimit=5.0, tileGridSize=(5, 5))
    dst = clahe.apply(gray)
    binary2 = cv.adaptiveThreshold(dst,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 25, 10) 
    kernel = np.ones((3,3),np.uint8)
    opening = cv.morphologyEx(binary2, cv.MORPH_OPEN, kernel)
    #cv.imwrite("opening.png", opening)
    outImage, contours, heriachy = cv.findContours(opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # need python:3.7，opencv:3.4.3
    contour_img = cv.drawContours(opening, contours, -1, (255, 255, 255), -1)
    i = 0
    for contour in contours:
        hull = cv.convexHull(contour)
        ((cx, cy), (width, height), theta) = cv.minAreaRect(hull)
        if height <0.0001:
            continue
        rate = min(width,height)/max(width,height)
        rate = round(rate, 2)
        eara = round(width*height, 2)
        if rate <= 0.5 and max(width, height) >= 70:
            i = i+1
            rect = ((cx, cy), (width, height), theta)
            box = np.int0(cv.boxPoints(rect))
            cv.drawContours(image, [box], 0, (255, 0, 255), 2)
    print(i)
    output = img_name + "_out.jpg"
    cv.imwrite(output, image)
    return

def main(args):
    image, image_name = args
    img_name = image_name
    print("--------")
    src = cv.imread(image)
    clahe_demo(src, img_name)
   
if __name__=="__main__":
    if len(sys.argv) < 3:
        print('usage: python trichome_counter.py <image> <image_name>')
        sys.exit()
    
    main(sys.argv[1:])