import pyrealsense2 as rs
import numpy as np
import cv2
import sys, os
import argparse
from time import time
from os.path import isfile, join
import re
from pdb import *

args = argparse.ArgumentParser()
args.add_argument('-d','--depth', dest="color",action='store_false')
args.add_argument('-cw', type=int, default=640)
args.add_argument('-ch', type=int, default=480)
args.add_argument('-vw', type=int, default=640)
args.add_argument('-vh', type=int, default=480)
args = args.parse_args()

pipeline = rs.pipeline()
config = rs.config()

if not args.color : config.enable_stream(rs.stream.depth, args.cw, args.ch, rs.format.z16, 30)
if     args.color : config.enable_stream(rs.stream.color, args.cw, args.ch, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
start = time()
images= 0
while True:
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()

    if not args.color:
        depth_frame = frames.get_depth_frame()
        depth_frame = rs.colorizer().colorize(depth_frame)
        im = np.asanyarray(depth_frame.get_data())
        #im = cv2.applyColorMap(depth_image, cv2.COLORMAP_HSV)
        im = cv2.resize(im, (args.vw,args.vh))
    else:
        color_image = np.asanyarray(color_frame.get_data())
        im = cv2.resize(color_image, (args.vw, args.vh))

    cv2.imshow('RS',im)
    if cv2.waitKey(1) != -1:break
    sys.stdout.write('\b'*20)
    images+=1
    sys.stdout.write("%.3fFPS"%(images/(time()-start)))
    sys.stdout.flush()

pipeline.stop()
print("\nfin")
