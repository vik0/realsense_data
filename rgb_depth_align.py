## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2017 Intel Corporation. All Rights Reserved.

#####################################################
##              Align Depth to Color               ##
#####################################################

# First import the library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2

# Create a pipeline
pipeline = rs.pipeline()

#Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print "Depth Scale is: " , depth_scale

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 2 #1 meter
clipping_distance = clipping_distance_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

count = 1
# Streaming loop
try:
    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image
        
        # Align the depth frame to color frame
        aligned_frames = align.proccess(frames)
        
        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()
        
        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue
        
        # print np.asanyarray(aligned_depth_frame.get_data())
        depth_image = np.asanyarray(aligned_depth_frame.get_data())*1.0
        color_image = np.asanyarray(color_frame.get_data())

        # Remove background - Set pixels further than clipping_distance to grey
        # grey_color = 153
        # depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
        # bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        # print depth_image_3d
        # Render images
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        # images = np.hstack((bg_removed, depth_colormap))
        depth_image = depth_image*depth_scale
        depth_image = depth_image*5000.0
        depth_image = depth_image.astype(np.uint16)
        color_image = color_image.astype(np.uint8)

        cv2.namedWindow('Depth', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Depth_Visual', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Color', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Depth', depth_image)
        cv2.imshow('Depth_Visual', depth_colormap)
        cv2.imshow('Color', color_image)

        # color_image_mod = color_image + 10*depth_colormap
        # cv2.namedWindow('Combined', cv2.WINDOW_AUTOSIZE)
        # cv2.imshow('Combined', color_image_mod)

        # print(np.mean(depth_image))

        key =cv2.waitKey(10)
        if key == 27:
            break
        if key == 32: # Space is pressed
            flag = cv2.imwrite('rgbd/Depth_'+str(count)+'.png',depth_image)
            flag = flag * cv2.imwrite('rgbd/Color_'+str(count)+'.png',color_image)
            if flag:
                print ('saved image pair '+str(count))
            else:
                print('could not save files')
            count +=1
finally:
    pipeline.stop()

