#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import os.path
import numpy as np
# from functools import reduce

folder='/tmp/alarm/2021-03-02'
first = True
count = 0

imagesize = (0, 0)

# see http://stackoverflow.com/questions/3374828/how-do-i-track-motion-using-opencv-in-python
files = os.listdir(folder)
files.sort()

for filename in files:
	count=count+1
	if filename.endswith(".jpg"):
		color_image = cv2.imread(os.path.join(folder,filename), cv2.IMREAD_COLOR)
		print("Reading file %s - (%d/%d - depth %d)" % (filename,color_image.shape[1],color_image.shape[0],color_image.shape[2]))
		# Smooth to get rid of false positives
		color_image = cv2.GaussianBlur(color_image, (3,3), 0)

		if imagesize != color_image.shape[:2]:
			imagesize = color_image.shape[:2]
			# image.copy().astype(float)
			moving_average = np.zeros(color_image.shape, np.float32) # cv2.CreateImage( imagesize, cv2.IPL_DEPTH_32F, 3)
			grey_image = np.zeros((color_image.shape[0],color_image.shape[1],1), np.uint8) # cv2.CreateImage( imagesize, cv2.IPL_DEPTH_8U, 1)
			first = True

		if first:
			moving_average = np.float32(color_image) # cv2.convertScaleAbs(color_image, 1.0, 0.0)
			# cv2.ConvertScale(color_image, moving_average, 1.0, 0.0)
			temp = color_image.copy()
			difference = color_image.copy()
			first = False
		else:
			cv2.accumulateWeighted(color_image, moving_average, 0.020)

		# cv2.imshow('img',color_image)
		# Convert the scale of the moving average.
		# temp = cv2.convertScaleAbs(moving_average, 1.0, 0.0)

		# Minus the current frame from the moving average.
		difference = cv2.absdiff(color_image, np.uint8(moving_average))

		# Convert the image to grayscale.
		grey_image = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

		# Convert the image to black and white.
		grey_image = cv2.threshold(grey_image, 70, 255, cv2.THRESH_BINARY)[1]

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
				points = []

				for contour in contours:
					bound_rect = cv2.boundingRect(contour)

					pt1 = (bound_rect[0], bound_rect[1])
					pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
					points.append(pt1)
					points.append(pt2)
					cv2.rectangle(color_image, pt1, pt2, (0, 0, 255), 1)

				# too many diverse changes, a circle does not work here
				#if len(points):
				#	center_point = reduce(lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), points)
				#	center_point = (int(center_point[0]), int(center_point[1]))
				#	cv2.circle(color_image, center_point, 40, (255, 255, 255), 1)
				#	cv2.circle(color_image, center_point, 30, (0, 100, 255), 1)
				#	cv2.circle(color_image, center_point, 20, (255, 255, 255), 1)
				#	cv2.circle(color_image, center_point, 10, (0, 100, 255), 1)
				cv2.imwrite(os.path.join(folder,"check", filename), color_image)

		#if count>10:
		#	break