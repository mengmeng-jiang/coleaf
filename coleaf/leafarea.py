#!/usr/bin/env python

import sys
import os.path as op

import cv2 as cv
from imutils.perspective import four_point_transform
import numpy as np
import imutils

from plantcv import plantcv as pcv

#Calculate the leaf erea
def calc_photo(image):
    height2, length2, channel=image.shape 
    if height2 < 1000:
        brurred = cv.GaussianBlur(image, (5, 5), 0)
    else:
        brurred = cv.GaussianBlur(image, (7, 7), 0)
    gray = cv.cvtColor(brurred, cv.COLOR_BGR2GRAY)
    edgo_output = cv.Canny(gray, 25, 150)
    kernel = np.ones((3, 3), np.uint8)
    closing =cv.morphologyEx(edgo_output, cv.MORPH_CLOSE, kernel)
    closing[0:int(0.01*height2),0:length2] = [0]
    closing[int(0.99*height2):height2,0:length2] = [0]
    closing[0:height2,0:int(0.01*length2)] = [0]
    closing[0:height2,int(0.99*height2):height2] = [0]
    return(closing)
    # closing_path = op.join(outpath, "closing.jpg")
    # cv.imwrite(closing_path, closing)
    # closing[int(0.4668*hig):int(0.4865*hig),0:len] = [0]
    # closing[int(0.9524*hig):int(0.9754*hig),0:len] = [0]
    # closing[0:hig,int(0.3165*len):int(0.3355*len)] = [0]
    # closing[0:hig,int(0.6605*len):int(0.6775*len)] = [0]
    # cv.imwrite("countour.jpg", closing)

def calc_scanned(image):
    lab = pcv.rgb2gray_lab(rgb_img=image, channel="b")
    ret, thesh = cv.threshold(lab, 0, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    img_binary = pcv.threshold.binary(gray_img=lab, threshold=ret, 
                                    max_value=255, object_type="light")
    kernel = np.ones((9, 9), np.uint8)
    closing = cv.morphologyEx(img_binary, cv.MORPH_CLOSE, kernel)
    return(closing)


#the color space is BGR
def measure_object(original_img, closing_img, background, name, outpath, output_img, f1):  
    height2, length2, channel=original_img.shape
    outImage, contours, heriachy = cv.findContours(closing_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contour_img = cv.drawContours(original_img, contours, -1, (50, 214, 241), 2)

    i = 0
    for contour in contours:   
        area = cv.contourArea(contour)
        if area >= int(0.001*height2*length2) and area < int(0.7*height2*length2):
            i+=1
            print(i)
            realrate = area/(height2*length2)
            realarea = realrate*background
            perimeter = cv.arcLength(contour, True)
            x1, y1, w1, h1 = cv.boundingRect(contour)
            cv.rectangle(contour_img, (x1, y1), (x1+w1, y1+h1), (250, 152, 56), 2)
            M = cv.moments(contour)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            center = (cx,cy)
            cv.circle(contour_img,center, 5, (255, 255, 0), -1)
            rate = round(max(w1, h1) / min(w1, h1), 1)
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
            cv.drawContours(contour_img, [box], 0, (67, 93, 220), 2)
            #print(i,h1,h2,hig)
            
            (leftx, lefty) = tuple(contour[contour[:,:,0].argmin()][0])
            cv.circle(contour_img,(leftx, lefty), 5, (255, 255, 0), -1)
            (rightx,righty) = tuple(contour[contour[:,:,0].argmax()][0])
            cv.circle(contour_img,(rightx, righty), 5, (255, 255, 0), -1)
            (topx, topy) = tuple(contour[contour[:,:,1].argmin()][0])
            (bottox, bottoy) = tuple(contour[contour[:,:,1].argmax()][0])            
            len1 = int(bottoy) - int(topy) 
            len2 = int(bottoy) - int(lefty)
            leftRate = int(len2)/int(len1)
            #print(leftRate)
            len3 = int(bottoy) - int(cy)
            centerRate = int(len3)/int(len1)
            #print(centerRate)
            if i <= 9: 
                text_i = "0%s"%i
            elif i > 9:
                text_i = "%s"%i
            text_x = np.int(x1)
            text_y = np.int(y1+h1+30)
            location = (text_x,text_y)
            cv.putText(contour_img, text_i, location, cv.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 0), 3)
            print("%s\t%s\t%.2f\t%.2f\t%.5f\t%.3f\t%.2f\t%i\t%.2f\t%.2f"%(
                name,text_i,perimeter,area,realrate, realarea,rate,shape,leftRate,centerRate), file=f1)
        else:
            print("the area " + str(area) + " is too little to countect")
    cv.putText(contour_img, name, (30, 30), cv.FONT_HERSHEY_COMPLEX, 1.0, (0,0,0), 3)
    outimg_path = op.join(outpath, output_img)
    cv.imwrite(outimg_path, contour_img)
    print("the area calculation succeeded! ")
    return


def main(image_path, img_type, height1=21, length1=29.7, img_name=None, outdir=None):
    background = height1*length1
    if img_name is None:
        imgname = op.basename(image_path)
        allname = op.splitext(imgname)[0]
        name = allname.split("_")[0]
    else:
        name = img_name
    allname = name + "_"
    output_img = allname + "o.jpg"
    output_txt = allname + "o.txt"
    if outdir is None:
        outpath = op.dirname(image_path)
    else:
        outpath = outdir
    outtxt_path = op.join(outpath, output_txt)
     
    image = cv.imread(image_path)
    if img_type == "photo":
        closing = calc_photo(image)
    elif img_type == "scanned":
        closing = calc_scanned(image) 
    with open(outtxt_path, "w")as f1:
        print("#sample\tleaf\tcontourPerimeter\tcontourArea\trealrate\trealarea\trectangleRate\tshape\tleftRate\tcenterRate", file=f1)
        #closing_img = cv.imread(closing, 0)
        measure_object(image, closing, background, name, outpath, output_img, f1)

# if __name__ == "__main__":
#     main(sys.argv[1:])