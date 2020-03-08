import cv2
import numpy as np
from rivgraph.rivers import river_utils as ru
from scipy import misc
import numpy as np
import gdal
from matplotlib import pyplot as plt
from rivgraph import mask_to_graph
import cv2

def nothing(x):
    pass

#mask_midline_rivGraph
def midline(img):
    I = cv2.imread(img)
    Imask = np.zeros((I.shape[0], I.shape[1]), dtype=np.bool)
    Imask[I[:,:,0] != 255] = True
    coords, widths = ru.mask_to_centerline(Imask, 'ew')

    plt.imshow(Imask)
    plt.plot(coords[:,0], coords[:,1])
    plt.show()

#Trackbars
cv2.namedWindow('colors')
cv2.createTrackbar('LH', 'colors', 0, 255, nothing)
cv2.createTrackbar('UH', 'colors', 255, 255, nothing)
cv2.createTrackbar('LS', 'colors', 0, 255, nothing)
cv2.createTrackbar('US', 'colors', 255, 255, nothing)
cv2.createTrackbar('LV', 'colors', 0, 255, nothing)
cv2.createTrackbar('UV', 'colors', 255, 255, nothing)
cv2.createTrackbar('erosion_kernelx', 'colors', 1, 20, nothing)
cv2.createTrackbar('erosion_kernely', 'colors', 1, 20, nothing)
cv2.createTrackbar('erosion_iteration', 'colors', 1, 20, nothing)
cv2.createTrackbar('gradient', 'colors', 0, 1, nothing)
cv2.createTrackbar('closing_kernelx', 'colors', 1, 20, nothing)
cv2.createTrackbar('closing_kernely', 'colors', 1, 20, nothing)
cv2.resizeWindow('colors', 600,600)

while True:
    frame = cv2.imread(r'PATH TO IMAGE')
    dst = frame
    #dst = cv2.fastNlMeansDenoisingColored(frame,None,2,2,10,5)
    #Define custom matrice kernel
    #kernel = np.array([[0, 0, 0],
    #                   [0, 1, 0],
    #                   [0, 0, 0]], np.uint8)

    #customFilter = cv2.filter2D(frame,-1,kernel)
    #GaussianFilter = cv2.GaussianBlur(dst,(9,9),0)
    hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)

    l_h = cv2.getTrackbarPos('LH', 'colors')
    u_h = cv2.getTrackbarPos('UH', 'colors')    
    l_s = cv2.getTrackbarPos('LS', 'colors')
    u_s = cv2.getTrackbarPos('US', 'colors')    
    l_v = cv2.getTrackbarPos('LV', 'colors')
    u_v = cv2.getTrackbarPos('UV', 'colors')
    
    ex = cv2.getTrackbarPos('erosion_kernelx', 'colors')
    ey = cv2.getTrackbarPos('erosion_kernely', 'colors')
    eit = cv2.getTrackbarPos('erosion_iteration', 'colors')
    grad = cv2.getTrackbarPos('gradient', 'colors')
    cx = cv2.getTrackbarPos('closing_kernelx', 'colors')
    cy = cv2.getTrackbarPos('closing_kernely', 'colors')

    #Mask értékek HSV-ben
    lower = np.array([l_h,l_s,l_v]) #50,10/0,0 kékek sávja
    upper = np.array([u_h,u_s,u_v]) #150,255,255#
    
    mask = cv2.inRange(hsv, lower, upper)
    erosion_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(ex,ey))
    closing_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(cx,cy))
    #closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # closing
    #closed = cv2.dilate(mask,kernel,iterations = 1) # dilation
    erosion = cv2.erode(mask,erosion_kernel,iterations = eit)
    closed = cv2.morphologyEx(erosion, cv2.MORPH_CLOSE, closing_kernel)
    if grad == 1:
        closed = cv2.morphologyEx(closed, cv2.MORPH_GRADIENT, closing_kernel)
		
    resultSkeleton = mask_to_graph.skeletonize_mask(closed)
    resultSkeletonF = np.float32(resultSkeleton)
    cv2.imshow('frame', frame)
    cv2.imshow('mask', mask)
    cv2.imshow('closed', closed)
    cv2.imshow('thinned',np.float32(resultSkeletonF))
    key = cv2.waitKey(1)
    if key == 27:
        break
#Write image
#cv2.imwrite('result.tif',resultSkeletonF)
cv2.destroyAllWindows()
