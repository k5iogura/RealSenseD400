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
args.add_argument('-d','--depth',action='store_true')
args.add_argument('-g','--gray', dest="color", action='store_false')
args.add_argument('-cw', type=int, default=640)
args.add_argument('-ch', type=int, default=480)
args.add_argument('-vw', type=int, default=320)
args.add_argument('-vh', type=int, default=240)
args = args.parse_args()

pipeline = rs.pipeline()
config = rs.config()

if args.depth : config.enable_stream(rs.stream.depth, args.cw, args.ch, rs.format.z16, 30)
if args.color : config.enable_stream(rs.stream.color, args.cw, args.ch, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
start = time()
images= 0
while True:
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()

    if args.depth:
        depth_frame = frames.get_depth_frame()
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_image = cv2.cvtColor(depth_image, cv2.COLOR_GRAY2RGB)
        depth_image = depth_image/(np.max(depth_image)+0.1)
        depth_image = (depth_image*255).astype(np.uint8)
    #    im = cv2.resize(depth_image, (args.vw,args.vh))
    if args.color:
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
