#!/usr/bin/env python

import sys
import os.path as op

import cv2 as cv
import numpy as np


def count_trich(image, outimg_path):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    clahe = cv.createCLAHE(clipLimit=5.0, tileGridSize=(5, 5))
    dst = clahe.apply(gray)
    binary2 = cv.adaptiveThreshold(dst,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 25, 10) 
    kernel = np.ones((3,3),np.uint8)
    opening = cv.morphologyEx(binary2, cv.MORPH_OPEN, kernel)
    #cv.imwrite("opening.png", opening)
    outimgage, contours, heriachy = cv.findContours(opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # here need python:3.7，opencv:3.4.3(source activate base) to avoid the bug "ValueError: not enough values to unpack (expected 3, got 2)"
    contour_img = cv.drawContours(opening, contours, -1, (255, 255, 255), -1)
    i = 0
    for contour in contours:
        hull = cv.convexHull(contour)
        ((cx, cy), (width, height), theta) = cv.minAreaRect(hull)
        if height <0.0001:
            continue
        rate = min(width,height)/max(width,height)
        rate = round(rate, 2)
        area = round(width*height, 2)
        if rate <= 0.5 and max(width, height) >= 70:
            i = i+1
            rect = ((cx, cy), (width, height), theta)
            box = np.int0(cv.boxPoints(rect))
            cv.drawContours(image, [box], 0, (255, 0, 255), 2)
    print(i)
    cv.imwrite(outimg_path, image)
    return

def main(image_path, img_name=None, outdir=None):
    if img_name is None:
        imgname = op.basename(image_path)
        allname = op.splitext(imgname)[0]
    else:
        allname = img_name
    output_img = allname+"_t.jpg"
    if outdir is None:
        outpath = op.dirname(image_path)
    else:
        outpath = outdir
    outimg_path =op.join(outpath,output_img)

    image = cv.imread(image_path)
    count_trich(image, outimg_path)
   
# if __name__=="__main__":
#     if len(sys.argv) < 3:
#         print('usage: python trichome_counter.py <image> <image_name>')
#         sys.exit()
    