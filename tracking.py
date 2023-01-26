# -*- coding: utf-8 -*-
"""Tracking.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ULty-Cra3VJ3TbgZ_98CWI9B2BSUlI1u

# first try
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
from scipy.interpolate import RectBivariateSpline
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
import cv2
from google.colab.patches import cv2_imshow

def LucasKanade(It, It1, rect, p0 = np.zeros(2)):
	   
    threshold = 0.1
    x1, y1, x2, y2 = rect[0], rect[1], rect[2], rect[3]
    rows_img, cols_img = It.shape
    rows_rect, cols_rect = x2 - x1, y2 - y1
    dp = [[cols_img], [rows_img]] #just an intial value to enforce the loop

    # template-related can be precomputed
    Iy, Ix = np.gradient(It1)
    y = np.arange(0, rows_img, 1)
    x = np.arange(0, cols_img, 1)     
    c = np.linspace(x1, x2, int(cols_rect))
    r = np.linspace(y1, y2, int(rows_rect))
    cc, rr = np.meshgrid(c, r)
    spline = RectBivariateSpline(y, x, It)
    T = spline.ev(rr, cc)
    spline_gx = RectBivariateSpline(y, x, Ix)
    spline_gy = RectBivariateSpline(y, x, Iy)
    spline1 = RectBivariateSpline(y, x, It1)

    # in translation model jacobian is not related to coordinates
    jac = np.array([[1,0],[0,1]])

    while np.square(dp).sum() > threshold:
            
        # warp image using translation motion model
        x1_w, y1_w, x2_w, y2_w = x1+p0[0], y1+p0[1], x2+p0[0], y2+p0[1]
        
        cw = np.linspace(x1_w, x2_w, int(cols_rect))
        rw = np.linspace(y1_w, y2_w, int(rows_rect))
        ccw, rrw = np.meshgrid(cw, rw)
        
        warpImg = spline1.ev(rrw, ccw)
        
        #compute error image
        err = T - warpImg
        errImg = err.reshape(-1,1) 
        
        #compute gradient
        Ix_w = spline_gx.ev(rrw, ccw)
        Iy_w = spline_gy.ev(rrw, ccw)
        #I is (n,2)
        I = np.vstack((Ix_w.ravel(),Iy_w.ravel())).T
        
        #computer Hessian
        delta = I @ jac 
        #H is (2,2)
        H = delta.T @ delta
        
        #compute dp
        #dp is (2,2)@(2,n)@(n,1) = (2,1)
        dp = np.linalg.inv(H) @ (delta.T) @ errImg
        
        #update parameters
        p0[0] += dp[0,0]
        p0[1] += dp[1,0]
    
    return p0

"""### CAR 1"""

# write your script here, we recommend the above libraries for making your animation
frames = np.load('/content/car1.npy')
rect = [390, 110, 520, 230]
width = rect[3] - rect[1]
length = rect[2] - rect[0]
rectList = []
video = []
time_total = 0
seq_len = frames.shape[2]
video_format = cv2.VideoWriter_fourcc('X','V','I','D')
video_output = cv2.VideoWriter('car1.avi',video_format,30.0,(frames.shape[1],frames.shape[0]))

for i in range(seq_len,0,-1):
    if (i == seq_len):
        continue
    print("Processing frame %d" % i)
    a = rect.copy()
    rectList.append(a)

    start = time.time()
    It = frames[:,:,i-1]
    It1 = frames[:,:,i]
    p = LucasKanade(It, It1, rect)
    # p = LucasKanade(It, It1, rect)
    rect[0] -= 1.5*p[0]
    rect[1] -= p[1]
    rect[2] -= p[0]
    rect[3] -= p[1]
    end = time.time()
    time_total += end - start

    f = np.copy(frames[:,:,i])
    f = cv2.cvtColor(f,cv2.COLOR_GRAY2RGB)
    f = cv2.rectangle(f, (int(rect[0]),int(rect[1])), (int(rect[2]),int(rect[3])), (0,255,0), 3)
    # cv2_imshow(f)
    video.append(f)
  
video.reverse()
for i in video: video_output.write(i)
print('Finished, the tracking frequency is %.4f' % (seq_len / time_total))
video_output.release()
cv2.destroyAllWindows()

"""### CAR 2"""

# write your script here, we recommend the above libraries for making your animation
frames = np.load('/content/car2.npy')
rect = [59, 116, 145, 151]
width = rect[3] - rect[1]
length = rect[2] - rect[0]
rectList = []
time_total = 0
seq_len = frames.shape[2]
video_format = cv2.VideoWriter_fourcc('X','V','I','D')
video_output = cv2.VideoWriter('car2.avi',video_format,30.0,(frames.shape[1],frames.shape[0]))

for i in range(seq_len):
    if (i == 0):
        continue
    print("Processing frame %d" % i)
    a = rect.copy()
    rectList.append(a)

    start = time.time()
    It = frames[:,:,i-1]
    It1 = frames[:,:,i]
    p = LucasKanade(It, It1, rect)
    rect[0] += p[0]
    rect[1] += p[1]
    rect[2] += p[0]
    rect[3] += p[1]
    end = time.time()
    time_total += end - start

    f = np.copy(frames[:,:,i])
    f = cv2.cvtColor(f,cv2.COLOR_GRAY2RGB)
    f = cv2.rectangle(f, (int(rect[0]),int(rect[1])), (int(rect[2]),int(rect[3])), (0,255,0), 3)
    video_output.write(f)

print('Finished, the tracking frequency is %.4f' % (seq_len / time_total))
video_output.release()
cv2.destroyAllWindows()

"""### Helicopter"""

# write your script here, we recommend the above libraries for making your animation
frames = np.load('/content/landing.npy')
rect = [440, 85, 560, 140]
width = rect[3] - rect[1]
length = rect[2] - rect[0]
rectList = []
time_total = 0
seq_len = frames.shape[2]
video_format = cv2.VideoWriter_fourcc('X','V','I','D')
video_output = cv2.VideoWriter('helicopter.avi',video_format,30.0,(frames.shape[1],frames.shape[0]))

for i in range(seq_len):
    if (i == 0):
        continue
    print("Processing frame %d" % i)
    a = rect.copy()
    rectList.append(a)

    start = time.time()
    It = frames[:,:,i-1]
    It1 = frames[:,:,i]
    p = LucasKanade(It, It1, rect)
    rect[0] += p[0]
    rect[1] += p[1]
    rect[2] += p[0]
    rect[3] += p[1]
    end = time.time()
    time_total += end - start

    f = np.copy(frames[:,:,i])
    f = cv2.cvtColor(f,cv2.COLOR_GRAY2RGB)
    f = cv2.rectangle(f, (int(rect[0]),int(rect[1])), (int(rect[2]),int(rect[3])), (0,255,0), 3)
    video_output.write(f)

print('Finished, the tracking frequency is %.4f' % (seq_len / time_total))
video_output.release()
cv2.destroyAllWindows()

