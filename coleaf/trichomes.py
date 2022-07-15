#!/usr/bin/env python

import sys
import os.path as op

import cv2 as cv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



def clahe_demo(image,outimg_hist):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    #cv.imwrite("D:\JMW\Python\picture_data\/trichomes\/0_gray.tif", gray)
    clahe = cv.createCLAHE(clipLimit=7.0, tileGridSize=(5,5))
    dst = clahe.apply(gray)
    #cv.imwrite("D:\JMW\Python\picture_data\/trichomes\/1_clahe.tif", dst)    
    binary2 = cv.adaptiveThreshold(dst,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 25, 0)
    #cv.imwrite("D:\JMW\Python\picture_data\/trichomes\/2_binary.tif",binary2) 
    kernel = np.ones((3,3),np.uint8) 
    opening = cv.morphologyEx(binary2, cv.MORPH_OPEN, kernel)
    #cv.imwrite("D:\JMW\Python\picture_data\/trichomes\/3_opening.tif",opening)
    outImage, contours, heriachy = cv.findContours(opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # here need python:3.7，opencv:3.4.3(source activate base) to avoid the bug "ValueError: not enough values to unpack (expected 3, got 2)"
    mask = np.zeros(opening.shape, np.uint8)
    contour_img = cv.drawContours(mask, contours, -1, (255, 255, 255), -1)
    #cv.imwrite("D:\JMW\Python\picture_data\/trichomes\/4_contour.tif",contour_img)
    i = 0
    rate_list=[]
    area_list=[]
    size_list=[]
    for contour in contours:
        ((cx, cy), (width, height), theta) = cv.minAreaRect(contour)
        if height <1:
            continue
        rate = min(width,height)/max(width,height)
        rate = round(rate, 2)
        area = round(cv.contourArea(contour),2)
        size = round(max(width,height),2)

        rate_list.append(rate)
        area_list.append(area)
        size_list.append(size)    
        i+=1
    all_list=[rate_list,area_list,size_list]


    trait = pd.DataFrame(all_list)
    trait = trait.T
    trait.rename(columns={0:'rate',1:'area',2:'size'},inplace=True)
    trait_stat = trait.agg(['min','max','mean','std']).round(decimals=2)
    print("contour stat: ")
    print(trait_stat)
    

    f,(ax1,ax2) = plt.subplots(1,2,figsize=(10,5),dpi=300)
    ax1.hist(trait['size'][trait['size']>10],5,color="tab:blue")
    ax1.set_title("contours_length plot",fontsize=15)
    ax1.set_ylabel("number",fontsize=13)
    ax1.set_xlabel("pixel",fontsize=13)
    ax1.set_ylim(0,50)
    count,division = pd.np.histogram(trait['size'][trait['size']>10],bins=5) 
    #print(count,division)
    max2=np.argsort(count)[-2]
    valuemin = division[max2]

    filter = trait[trait['size']>valuemin]
    filter_stat = filter.agg(['min','max','mean','std']).round(decimals=2)
    ax2.hist(filter['area'],3,color="orangered")
    ax2.set_title("trichomes_area plot",fontsize=15)
    ax2.set_ylim(0,50)
    ax2.set_ylabel("number",fontsize=13)
    ax2.set_xlabel("pixel",fontsize=13)
    plt.savefig(outimg_hist)
    count2, division2 = pd.np.histogram(filter['area'],bins=3)  

    #print(count2,division2)
    max3=np.argsort(count2)[-2]
    valuemin2 = division2[max3]
    area_all = filter['area'][filter['area']>valuemin2].sum()
    area_mean = filter['area'][filter['area']<valuemin2].mean()
    print("trichomes stat: ")
    print(filter_stat)
    #print(area_all)
    area_true = round(area_all/area_mean)
    return(valuemin,valuemin2,area_true,contours)

def sifter(valuemin,valuemin2,area_true,contours,image,outimg_path):    
    area_big=0
    nu = 0
    for contour in contours:
        ((cx, cy), (width, height), theta) = cv.minAreaRect(contour)
        size = round(max(width,height),2)

        if size > valuemin:
            area = round(cv.contourArea(contour),2) 
            nu+=1
            rect = ((cx, cy), (width, height), theta)
            box = np.int0(cv.boxPoints(rect))
            cv.drawContours(image, [box], 0, (180, 119, 31), 2)
            if area > valuemin2: 
                area_big+=1
                cv.drawContours(image, [box], 0, (0, 69, 255), 2)
            
    print("Number of individual trichomes:"+"\t"+ str(nu))
    print("The number of abnormal contours in area:" +"\t"+ str(area_big))
    print("number of intersecting trichomes:" +"\t"+ str(area_true))
    true_nu = nu-area_big+area_true
    #print(true_nu)
    height2, length2, channel=image.shape
    text_x = np.int(length2-200)
    text_y = np.int(height2-100)
    location = (text_x,text_y)
    cv.putText(image, str(true_nu), location, cv.FONT_HERSHEY_COMPLEX, 2, (0, 0, 0), 3)
    print(outimg_path+":"+"\t"+ str(true_nu), file=sys.stdout)
    cv.imwrite(outimg_path, image)
    return

def main(image_path, img_name=None, outdir=None):
    if img_name is None:
        imgname = op.basename(image_path)
        allname = op.splitext(imgname)[0]
        #allname = imgname
    else:
        allname = img_name
    output_hist = allname+"_hist.jpg"
    output_img = allname+"_t.tif"
    if outdir is None:
        outpath = op.dirname(image_path)
    else:
        outpath = outdir
    outimg_hist =op.join(outpath, output_hist)
    outimg_path =op.join(outpath, output_img)

    image = cv.imread(image_path)
    valuemin, valuemin2, area_true, contours = clahe_demo(image, outimg_hist)
    sifter(valuemin, valuemin2, area_true, contours, image, outimg_path)
   
# if __name__=="__main__":
#     if len(sys.argv) < 3:
#         print('usage: python trichome_counter.py <image> <image_name>')
#         sys.exit()
    