#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import os.path
import numpy as np
import os
import yaml

# from functools import reduce

# read config file
cfg = []
if os.path.isfile("config.yml"):
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)

folder = '/data'
os.mkdir("/data/check")
first = True
count = 0
minsquare = 10
if "minsquare" in cfg:
    minsquare = int(cfg["minsquare"])

imagesize = (0, 0)

# see http://stackoverflow.com/questions/3374828/how-do-i-track-motion-using-opencv-in-python
files = os.listdir(folder)
files.sort()

for filename in files:
    count = count + 1
    if filename.endswith(".jpg"):
        color_image = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_COLOR)
        print("Reading file %s - (%d/%d - depth %d)" % (filename,
                                                        color_image.shape[1],
                                                        color_image.shape[0],
                                                        color_image.shape[2]))

        # Smooth to get rid of false positives
        color_image = cv2.GaussianBlur(color_image, (3, 3), 0)

        if imagesize != color_image.shape[:2]:
            imagesize = color_image.shape[:2]
            moving_average = np.zeros(color_image.shape, np.float32)
            grey_image = np.zeros((color_image.shape[0], color_image.shape[1], 1), np.uint8)
            first = True

        if first:
            moving_average = np.float32(color_image)
            temp = color_image.copy()
            difference = color_image.copy()
            first = False
        else:
            cv2.accumulateWeighted(color_image, moving_average, 0.020)

        # cv2.imshow('img',color_image)

        # Minus the current frame from the moving average.
        difference = cv2.absdiff(color_image, np.uint8(moving_average))

        # Convert the image to grayscale.
        grey_image = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

        # Convert the image to black and white.
        grey_image = cv2.threshold(grey_image, 70, 255, cv2.THRESH_BINARY)[1]

        if "ignore" in cfg:
            for i in cfg["ignore"]:
                pts = i.split("-")
                pt1s = pts[0].split("x")
                pt1 = (int(pt1s[0]), int(pt1s[1]))
                pt2s = pts[1].split("x")
                pt2 = (int(pt2s[0]), int(pt2s[1]))
                cv2.rectangle(grey_image, pt1, pt2, (0, 0, 0), -1)

        # eliminate small changes
        temp = cv2.dilate(grey_image, None, 18)
        temp = cv2.erode(temp, None, 10)
        contours, hirarchy = cv2.findContours(temp, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            bound_rect = cv2.boundingRect(contour)
            if bound_rect[2] < minsquare and bound_rect[3] < minsquare:
                pt1 = (bound_rect[0], bound_rect[1])
                pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
                cv2.rectangle(grey_image, pt1, pt2, (0, 0, 0), -1)

        # cv2.imshow('img',grey_image)

        dif = cv2.countNonZero(grey_image)
        if dif > 1000:
            if dif > 100000:
                first = True
                print("  %d - restarting" % dif)
            else:
                print("  %d - HIT" % dif)
                # Dilate and erode to get people blobs
                grey_image = cv2.dilate(grey_image, None, 18)
                grey_image = cv2.erode(grey_image, None, 10)

                contours, hirarchy = cv2.findContours(grey_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    bound_rect = cv2.boundingRect(contour)

                    pt1 = (bound_rect[0], bound_rect[1])
                    pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
                    cv2.rectangle(color_image, pt1, pt2, (0, 0, 255), 1)

                cv2.imwrite(os.path.join(folder, "check", filename), color_image)
