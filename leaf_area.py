#!/usr/bin/env python
from plantcv import plantcv as pcv
import cv2 as cv
import numpy as np
import sys



def image_thresholding(image):
    #pcv.plot_image(image)
    lab = pcv.rgb2gray_lab(rgb_img=image,channel="b")
    ret, thesh = cv.threshold(lab, 0,255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    img_binary = pcv.threshold.binary(gray_img=lab, threshold=ret, max_value=255, object_type="light")
    kernel = np.ones((3,3), np.uint8)
    closing = cv.morphologyEx(img_binary, cv.MORPH_CLOSE, kernel)
    #cv.imwrite("test_kai.png", closing)
    return(closing)

def measure_object(image, img_name, output_handle):    
    ret, binary = cv.threshold(image, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    outImage, contours, heriachy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    contour_img = cv.drawContours(color, contours, -1, (255, 255, 255), -1)

    text_i = 0
    for contour in contours:
        area = cv.contourArea(contour)
        if area <= 1000:
            pass
        else:
            perimeter = cv.arcLength(contour, True)
            x, y, w, h = cv.boundingRect(contour)
            cv.rectangle(contour_img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            rect = cv.minAreaRect(contour)
            box = cv.boxPoints(rect)
            box = np.int0(box)
            cv.drawContours(contour_img, [box], 0, (242,175,54), 2)
            rate = min(w,h)/max(w,h)
            mm = cv.moments(contour)
            if mm['m00'] == 0:
                continue
            else:
                cx = mm['m10']/mm['m00']
                cy = mm['m01']/mm['m00']
                cv.circle(contour_img, (np.int(cx), np.int(cy)), 3, (125, 125, 125), -1)
            text_i = text_i+1
            text_i_str = "0%s"%text_i
            text_x = np.int(x+w+10)
            text_y = np.int(y+h+10)
            cv.putText(contour_img, text_i_str, (text_x, text_y), cv.FONT_HERSHEY_COMPLEX, 1.0, (125,125,125),2)
            print("%s\t%.1f\t%.3f\t%.3f\t%d:%d"%(text_i_str,area,perimeter,rate,np.int(cx),np.int(cy)), file=output_handle)

        text_all = img_name
        output = img_name + "_output.jpg"
        cv.putText(contour_img, text_all, (30,30), cv.FONT_HERSHEY_COMPLEX, 1.0, (125,125,125), 2)
        cv.imwrite(output, contour_img)
    return


def main(args):
    image, image_name = args
    img_name = image_name
    txt = image_name + ".txt"
    
    print("--------")
    src = cv.imread(image)
    closing = image_thresholding(src)
    with open(txt, "w")as f1:
        print("#leaf\tcontourArea\tcontourPerimeter\trectangleRate\tcenter", file=f1)
        measure_object(closing, img_name, f1)

if __name__=="__main__":
    if len(sys.argv) < 3:
        print('usage: python leaf_area.py <image> <image_name>')
        sys.exit()
    
    main(sys.argv[1:])