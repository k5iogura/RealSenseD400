#!/usr/bin/env python3
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
args.add_argument('-d','--depth', action='store_true')
args.add_argument('-c','--color', action='store_true')
args.add_argument('-b','--both' , action='store_true')
args.add_argument('-cw', type=int, default=640)
args.add_argument('-ch', type=int, default=480)
args.add_argument('-vw', type=int, default=640)
args.add_argument('-vh', type=int, default=480)
args = args.parse_args()
if args.both or (not args.color and not args.depth): args.depth = args.color = True
print("Depth/Color/Both",args.depth, args.color, args.both)

pipeline = rs.pipeline()
config   = rs.config()

align_to = rs.stream.color
align    = rs.align(align_to)

if args.depth: config.enable_stream(rs.stream.depth, args.cw, args.ch, rs.format.z16, 30)
if args.color: config.enable_stream(rs.stream.color, args.cw, args.ch, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
start = time()
images= 0
while True:
    frame = pipeline.wait_for_frames()
    align_frame = align.process(frame)
    if args.color: color_frame = align_frame.get_color_frame()
    if args.depth: depth_frame = align_frame.get_depth_frame()

    if not args.color and args.depth:
        depth_frame = rs.colorizer().colorize(depth_frame)
        im = np.asanyarray(depth_frame.get_data())
        im = cv2.resize(im, (args.vw,args.vh))
    if args.color and args.depth:
        depth_frame = rs.colorizer().colorize(depth_frame)
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
