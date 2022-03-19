#!/usr/bin/env python


import sys

import cv2 as cv
import numpy as np
import os.path as op


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
def edge_crop(image): 
    brurred = cv.GaussianBlur(image, (5, 5), 0) #高斯模糊先去噪，因为Canny对噪声敏感，但是不能模糊的太厉害，不然会导致一些边缘被模糊掉
    gray = cv.cvtColor(brurred, cv.COLOR_BGR2GRAY)
    #mimg = cv.adaptiveThreshold(gray, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,11,2)
    thr, mimg = cv.threshold(gray, 160, 255, cv.THRESH_BINARY)
    kernel = np.ones((5,5),np.uint8)
    opening = cv.morphologyEx(mimg, cv.MORPH_OPEN, kernel)               # 防止A4的轮廓被下一步的中值滤波去除，变大一点
    edgo_output = cv.Canny(opening, 100, 125)
    # cv.imwrite("threshold.jpg", gray)
    # cv.imwrite("edgo.jpg", edgo_output)
    # cv.imwrite("dilation.jpg", opening)
    hig, length = edgo_output.shape
    print(hig*length)
    cloneImage, contours, heriachy = cv.findContours(edgo_output, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    contour_img = cv.drawContours(edgo_output, contours, -1, (255, 255, 255), 2)
    #cv.imwrite("test_b.jpg", contour_img)
    res = []
    i = 0
    for contour in contours:   
        area = cv.contourArea(contour)
        res.append(area)
        if area >= int(hig*length/3):
            i = 1
            epsilon = 0.1 * cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, epsilon, True)        # 获取近似轮廓
            #print(approx)
            hull = cv.convexHull(approx)                              # 默认返回坐标点
            #print(hull)
            #hull_img = cv.polylines(image, [hull], True, (0, 255, 0), 2)
            #cv.imwrite('hull_img.jpg', hull_img)
            if len(hull) == 4:
                dst = four_point_transform(image, hull.reshape(4,2))    # 矫正变换
                print("crop down well")
                return dst
            
            else:
                print(" The four points of the contour cannot be obtained")
            break
    if i == 0:
        print(" Eligible contour cannot be obtained ")


def main(image_path, crop = False, reflections = False, outdir=None):
    image = cv.imread(image_path)
    print("----------")
    tip = "_i"
    if crop is True:
        image = edge_crop(image)
        tip = "_c"
    if reflections is True:
        image = remove_reflections(image)
        tip = "_r"

    if crop is True and reflections is True:
        tip = "_p"
    #if imgname is None:
    imgname = op.basename(image_path)
    name = op.splitext(imgname)[0]
    if outdir is None:
        outpath = op.dirname(image_path)
    else:
        outpath = outdir
    outname = op.join(outpath, name + tip + ".jpg")

    cv.imwrite(outname, image)

# if __name__ == "__main__":
#     main(sys.argv[1], True, True)