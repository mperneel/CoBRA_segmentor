# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 14:51:25 2021

@author: Maarten
"""
#%%packages
import numpy as np
from scipy.spatial import ConvexHull

#%% main code
def surrounding_polygons(points):
    """
    Calculate the convex hull and the smallest surrounding rectangle of a point
    cloud

    Parameters
    ----------
    points : numpy array
        numpy array with x-coordinates in the first column and y-coordinates in
        the second column

    Returns
    -------
    convex_hull : numpy array
        numpy array containing the coordinates of the vertices of the conves
        hull
    bbox : numpy array
        numpy array of the form [x_center, y_center, width, height, theta]
        containing the bbox coordinates in absolute yolo format

    """
    #Calculate convex hull
    convex_hull = points[ConvexHull(points).vertices,:]

    """
    calculate smallest surrounding rectangle
    for this, we have to consider only the points which set up the convex hull

    the smallest surrounding rectangle has the property that at least one of
    its sides fall together with a side of the convex hull.

    To find the smallest rectangle, the following procedure is followed:
        for each edge of the convex hull:
            rotate convex hull until edge is parallel with x-axis
            determine a rectangle parallel with the axis
            calculate the area of that rectangle
        choose the smallest rectangle and determine all parameters of this
        rectangle in absolute yolo format
    """

    #initiate an empty array to store the areas of all possible rectangles
    A = np.zeros(shape=(len(convex_hull)))

    #calculate the area of each possible rectangle
    for i in range(len(convex_hull)):
        #determine theta (rotation angle)
        P1 = convex_hull[i,:]
        P2 = convex_hull[(i + 1)%len(convex_hull),:]
        if (P2[0] - P1[0])==0:
            theta = -1*np.pi/2
        else:
            tan_theta = -1*np.divide((P2[1] - P1[1]), (P2[0] - P1[0]))
            theta = np.arctan(tan_theta)

        #determine transformation matrix
        s = np.sin(-1*theta)
        c = np.cos(-1*theta)
        M = np.array([[c, s],
                     [-s, c]])

        #rotate convex hull
        M = M.transpose()
        ch_rotated = np.matmul(convex_hull,M)

        #calculate area of smallest rectangle parralel with axis
        xmax = np.max(ch_rotated, axis=0)[0]
        ymax = np.max(ch_rotated, axis=0)[1]
        xmin = np.min(ch_rotated, axis=0)[0]
        ymin = np.min(ch_rotated, axis=0)[1]
        A[i] = (xmax-xmin) * (ymax - ymin)

    #check which side of the convex hull delivers smallest rectangle
    i = np.argmin(A)

    #calculate theta
    P1 = convex_hull[i,:]
    P2 = convex_hull[(i + 1)%len(convex_hull),:]
    tan_theta = -1*np.divide((P2[1] - P1[1]), (P2[0] - P1[0]))
    theta = np.arctan(tan_theta)

    #theta is angle between edge and x axis
    #turn theta radials back to let edge be on x axis
    s = np.sin(-1*theta)
    c = np.cos(-1*theta)
    M = np.array([[c, s],
                 [-s, c]])
    M = M.transpose()
    ch_rotated = np.matmul(convex_hull,M)

    #calculate rectangle in rotated axis set
    xmax = np.max(ch_rotated, axis=0)[0]
    ymax = np.max(ch_rotated, axis=0)[1]
    xmin = np.min(ch_rotated, axis=0)[0]
    ymin = np.min(ch_rotated, axis=0)[1]
    w = xmax - xmin
    h = ymax - ymin

    x = xmin + w/2
    y = ymin + h/2

    #rotate center of rectangle back to original axis set
    center = np.array([x, y])
    center = np.matmul(center, np.linalg.inv(M))
    x_c, y_c = center

    #convert theta to degrees
    theta = theta * 360 / (np.pi *2)

    #convert theta to value in range [0, 360]
    if theta >= 0:
        theta = theta % 360
    else: # theta < 0
        a = -theta % 360
        theta = 360-a

    #convert theta to value in range [0,180]
    if theta>180:
        theta -= 180

    #Pconvert theta to value in range [0, 90]
    if theta>90:
        theta -= 90
        w_copy = w.copy()
        w = h
        h = w_copy

    #convert angle to value in range [-45, 45]
    if theta>45:
        theta -= 90
        w_copy = w.copy()
        w = h
        h = w_copy

    #assembly bbox
    bbox = np.array([x_c, y_c, w, h, theta])
    return (convex_hull, bbox)