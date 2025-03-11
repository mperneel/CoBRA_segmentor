# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 14:57:55 2021

@author: Maarten
"""
#%% packages
import numpy as np

#%% main code
def classic_bbox(points):
    """
    Calculate a classic bbox surrounding a point cloud

    Parameters
    ----------
    points : numpy array
        numpy array with x-coordinates in the first column and y-coordinates in
        the second column

    Returns
    -------
    bbox : numpy array
        numpy array of the form [x_center, y_center, width, height]
        containing the bbox coordinates in absolute yolo format
    """

    #calculate x_min, x_max, y_min and y_max
    x_min = points[:,0].min()
    x_max = points[:,0].max()
    y_min = points[:,1].min()
    y_max = points[:,1].max()

    #calculate width and height
    w = x_max - x_min
    h = y_max - y_min

    #calcualte center coordinates
    x_c = x_min + w/2
    y_c = y_min + h/2

    #assembly bbox
    bbox = np.array([x_c, y_c, w, h])
    return bbox