# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:14:28 2021

@author: Maarten
"""
#%%
import tkinter as tk
import numpy as np
import pandas as pd
import cv2
import os
from PIL import Image, ImageTk
import json

from surrounding_polygons import surrounding_polygons
from classic_bbox import classic_bbox

#%%

class AnnotationCanvas(tk.Canvas):

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)

        #assign master
        self.master = master

        #assign image object
        self.image = self.master.image

        self.tk_image = self.create_image(0,0, anchor='nw')

        #bind events to methods
        self.bind("<Button-1>",
                         lambda event: self.add_point(event))
        self.bind("<MouseWheel>",
                         lambda event: self._on_mousewheel(event))
        self.bind("<B3-Motion>",
                         lambda event: self.move_image(event))
        self.bind("<B1-Motion>",
                         lambda event: self.move_point(event))
        self.bind("<Button-3>",
                         lambda event: self.move_image_activate(event))

        #declare attributes containing information about dimensions canvas
        self.uw = self.winfo_width() #useable_width
        self.uh = self.winfo_height() #useable_height

        #declare attributes containing variables
        self.mouse_x = 0 #x position of mouse
        self.mouse_y = 0 #y position of mouse
        self.nominal_scale = 1.0 #nominal scale (scale to show image as large
        #as possible in the current window size)
        self.zoom_level = 1.0 #zoom level, relative to nominal scale
        self.x_zoom_center_image = 0 #x-coordinate of zooming center
        self.y_zoom_center_image = 0 #y-coordinate of zooming center
        self.zoom_delta_x = 0 #left intercept for self.shown_image
        self.zoom_delta_y = 0 #top intercept for self.shown_image
        self.image_inter = None #image matrix with all confirmed objects drawn
        self.image_shown = None #matrix with shown image
        self.image_inter_scale = 1.0 #scale of self.image_inter
        self.point_active = False #is there an active point?
        self.linewidth = 1 #linewidth

        #Declare attributes containing configuration/status information
        self.show_pbbox = False #show classic bbox parallel with image axes
        self.show_rbbox = True #show rotated bboc
        self.show_convex_hull = True #show convex hull
        self.show_segment = True #show segment
        self.show_mask = True #show mask


    def add_point(self, event):
        """
        Add/reactivate a point. If possible, self.bbox, self.convex_hull and
        self.pbbox are recalculated
        """
        #execute method only if an image is loaded
        if self.image.image is not None:

            #calculate x and y position on original image
            s = self.zoom_level * self.nominal_scale
            x = (event.x + self.zoom_delta_x) / s
            y = (event.y + self.zoom_delta_y) / s

            valid = self.image.add_point(x, y, scale=s)

            if valid:
                #update attributes related to mouse position
                self.mouse_x = event.x
                self.mouse_y = event.y

                #update image
                self.updateImage(from_scratch=False)


    def _on_mousewheel(self, event):
        """
        Zoom image
        """
        if self.image.image is not None:
            #get current scale
            s = self.zoom_level * self.nominal_scale

            #determine zooming center on original image
            self.x_zoom_center_image = (event.x + self.zoom_delta_x) / s
            self.y_zoom_center_image = (event.y + self.zoom_delta_y) / s

            #increase self.zoom_level with 5%
            self.zoom_level *= (1.05)**(event.delta/120)

            #recalculate scale
            s = self.zoom_level * self.nominal_scale

            #calculate intercepts
            #at least 0
            self.zoom_delta_x = max(0,self.x_zoom_center_image * s - event.x)
            self.zoom_delta_y = max(0,self.y_zoom_center_image * s - event.y)
            #if image fits on self.annotation_canvas, intercepts have to be 0
            self.zoom_delta_x = min(max(0,self.image.image.shape[1] * self.zoom_level *\
                                        self.nominal_scale - self.winfo_width()),
                                    self.zoom_delta_x)
            self.zoom_delta_y = min(max(0,self.image.image.shape[0] * self.zoom_level *\
                                        self.nominal_scale - self.winfo_height()),
                                    self.zoom_delta_y)
            #convert intercepts to integers
            self.zoom_delta_x = int(self.zoom_delta_x)
            self.zoom_delta_y = int(self.zoom_delta_y)

            #update image
            self.updateImage()

    def move_image(self, event):
        """
        Move image
        """

        if self.image.image is not None:
            #adapt intercepts
            self.zoom_delta_x += (self.mouse_x - event.x)
            self.zoom_delta_y += (self.mouse_y - event.y)
            #At least 0
            self.zoom_delta_x = max(0, self.zoom_delta_x)
            self.zoom_delta_y = max(0, self.zoom_delta_y)
            #if image fits on self.annotation_canvas, intercepts have to be 0
            self.zoom_delta_x = min(max(0,self.image.image.shape[1] * self.zoom_level *\
                                        self.nominal_scale - self.winfo_width()),
                                    self.zoom_delta_x)
            self.zoom_delta_y = min(max(0,self.image.image.shape[0] * self.zoom_level *\
                                        self.nominal_scale - self.winfo_height()),
                                    self.zoom_delta_y)
            #convert intercepts to integers
            self.zoom_delta_x = int(self.zoom_delta_x)
            self.zoom_delta_y = int(self.zoom_delta_y)

            #update mouse position parameters
            self.mouse_x = event.x
            self.mouse_y = event.y

            #update image
            self.updateImage(from_scratch=False)

    def move_point(self, event):
        """
        update the position of the point which is currently active
        """

        #check if there is currently a point active
        if self.image.point_active:
            #Calculate scale
            s = self.zoom_level * self.nominal_scale

            #calculate new coordinates
            x = (event.x - self.mouse_x) / s
            y = (event.y - self.mouse_y) / s

            self.image.update_point(x, y)

            #update atributes considering mouse position
            self.mouse_x = event.x
            self.mouse_y = event.y

            #update image
            self.updateImage(from_scratch=False)

    def move_image_activate(self, event):
        """
        Get initial variables considering mouse position
        """
        self.mouse_x = event.x
        self.mouse_y = event.y

    def updateImage(self, from_scratch=True):
        """
        Update image
        """

        if self.image.image is None:
            #display an image, but don't store it
            #result: no image is shown at all
            self.image_shown = np.uint8(np.zeros(shape=(100,100,3)))
            image_shown = Image.fromarray(self.image_shown)
            image_shown = ImageTk.PhotoImage(image_shown)
            self.itemconfigure(self.tk_image, image=image_shown)

            return

        #get image height and width
        image_height, image_width = self.image.image.shape[:2]

        #get scale
        s = self.zoom_level * self.nominal_scale

        #get intercepts
        dx = self.zoom_delta_x
        dy = self.zoom_delta_y

        if (from_scratch is True) or (self.image_inter_scale!=s):
            #draw all bboxes, convex hulls and segments of confirmed objects

            #initiate self.image_inter(mediate)
            self.image_inter = self.image.image.copy()
            self.image_inter_scale = s

            #resize self.image_inter according to scale s
            self.image_inter = cv2.resize(self.image_inter,
                                          dsize=(int(image_width * s),
                                                 int(image_height * s)))

            #draw all bboxes, convex hulls and segments of confirmed objects
            for i in self.image.names["obj"]:
                if i != self.image.obj_id:
                    pbbox = self.image.pbboxes.loc[self.image.pbboxes["obj"]==i,].iloc[0,].copy()
                    bbox = self.image.bboxes.loc[self.image.bboxes["obj"]==i,].iloc[0,].copy()
                    obj_class = self.image.annotation_classes.\
                        loc[self.image.annotation_classes["obj"] ==i, "class"].iloc[0]
                    color = self.master.project.colors[obj_class]
                    convex_hull = self.image.convex_hulls[str(i)].copy()
                    segment = self.image.annotation_points.loc[self.image.annotation_points["obj"]==i,\
                                                         ["x", "y"]].to_numpy()

                    if self.show_pbbox is True:
                        #draw classic bbox
                        pbbox["theta"] = 0
                        self.image_inter = self.draw_bbox(self.image_inter, pbbox, s, color)

                    if self.show_rbbox is True:
                        #draw rotated bbox
                        self.image_inter = self.draw_bbox(self.image_inter, bbox, s, color)

                    if self.show_convex_hull is True:
                        #draw conves hull
                        self.image_inter = self.draw_convex_hull(self.image_inter,\
                                                                 convex_hull, s, color)

                    if self.show_segment is True:
                        #draw segment
                        if (self.show_rbbox is True) and (self.show_convex_hull) is True:
                            segment_color = [0, 0, 255]
                        else:
                            segment_color = color
                        self.image_inter = self.draw_segment(self.image_inter, segment,\
                                                             s, color=segment_color)

            #draw all confirmed masks
            if self.show_mask:
                for i in self.image.names_masks["obj"]:
                    if i != self.image.mask_id:
                        mask = self.image.annotation_points_masks.loc[self.image.annotation_points_masks["obj"]==i,\
                                                             ["x", "y"]].to_numpy()
                        color = [0, 0, 0]

                        self.image_inter = self.draw_mask(self.image_inter, mask,\
                                                          s, color=color)

        #draw points, bbox, convex hull and segment of current object
        self.image_shown = self.image_inter.copy()

        #draw points of current object
        for point in self.image.points:
            x = int(point[0] * s)
            y = int(point[1] * s)
            self.image_shown= cv2.circle(self.image_shown,(x,y),
                                        radius=3,
                                        color=[0,255,0],
                                        thickness=-1)

        color = [255, 255, 0] #yellow
        segment = self.image.points.copy()

        if (self.show_pbbox is True) and (len(self.image.points)>=2):
            #draw bbox parallel to axes
            pbbox = self.pbbox.copy().loc[0]
            pbbox["theta"] = 0
            self.image_shown = self.draw_bbox(self.image_shown, pbbox, s, color)

        if len(segment)>=3:
            bbox = self.image.bbox.copy().loc[0]
            convex_hull = self.image.convex_hull.copy()

            if self.show_rbbox is True:
                #draw rotated bbox
                self.image_shown = self.draw_bbox(self.image_shown, bbox, s, color)

            if self.show_convex_hull is True:
                #draw convex hull
                self.image_shown = self.draw_convex_hull(self.image_shown, convex_hull, s, color)

            if self.show_segment is True:
                #draw segment
                if (self.show_rbbox is True) and (self.show_convex_hull) is True:
                    segment_color = [0, 0, 255]
                else:
                    segment_color = color
                self.image_shown = self.draw_segment(self.image_shown, segment,\
                                                     s, color=segment_color)

        #draw points of current mask
        if self.show_mask:
            for point in self.image.points_mask:
                x = int(point[0] * s)
                y = int(point[1] * s)
                self.image_shown= cv2.circle(self.image_shown,(x,y),
                                            radius=3,
                                            color=[0,255,0],
                                            thickness=-1)

            color = [255, 255, 0] #yellow
            mask = self.image.points_mask.copy()

            if len(mask)>=3:
                #draw segment
                #identical to drawing segments of active object
                mask_color = color
                self.image_shown = self.draw_segment(self.image_shown, mask,\
                                                     s, color=mask_color)


        #slice self.image_shown so slice fits in self.annotation_canvas
        if self.zoom_level>1:
            uw = self.winfo_width()
            uh = self.winfo_height()
            self.image_shown = self.image_shown[dy : dy + uh,
                                                dx: dx + uw,
                                                :]

        #show image
        image_shown = Image.fromarray(self.image_shown)
        image_shown = ImageTk.PhotoImage(image_shown)
        self.itemconfigure(self.tk_image, image=image_shown)
        self.image_shown = image_shown

    def draw_bbox(self, image, bbox, z, color):
        """
        Draw bbox on image

        bbox has to be of the form [x_center, y_center, width, height, theta]
        in absolute YOLO format

        z is the scale of the image relative to the original image
        """

        #calculate corner coordinates of rectangle in rotated axes set centered
        #around center of bbox
        w = bbox["w"]
        h = bbox["h"]
        coordinates = np.array([[w/2, h/2],
                                [-w/2, h/2],
                                [-w/2, -h/2],
                                [w/2, -h/2]])

        #rotate bbox towards axes set of image
        theta = np.radians(bbox["theta"])
        s = np.sin(theta)
        c = np.cos(theta)
        M = np.array([[c, s],
                      [-s, c]])
        M = M.transpose()
        coordinates = np.matmul(coordinates,M)

        #shift bbox to right center position
        center = np.array([bbox["x"], bbox["y"]])
        coordinates = coordinates * z + center * z

        #round coordintes and draw bbox
        coordinates = np.int64(coordinates).reshape((-1, 1, 2))

        image= cv2.polylines(image,
                            [coordinates],
                            isClosed=True,
                            color=color,
                            thickness=self.linewidth)
        return image

    def draw_convex_hull(self, image, convex_hull, z, color):
        """
        Draw convex hull on image

        convex_hull contains the vertices of the convex hull

        z is the scale of the image relative to the original image
        """
        #rescale coordinates of convex_hull
        convex_hull *= z

        #round coordinates and draw convex hull on image
        convex_hull = np.int64(convex_hull).reshape((-1, 1, 2))

        image= cv2.polylines(image,
                              [convex_hull],
                              isClosed=True,
                              color=color,
                              thickness=self.linewidth)
        return image

    def draw_segment(self, image, segment, z, color):
        """
        Draw segment on image

        Segments contains all the points which define the segment

        z is the scale of the image relative to the original image
        """
        #rescale coordinates within segment
        segment *= z

        #round coordinates and draw segment on image
        segment = np.int64(segment).reshape((-1, 1, 2))

        image= cv2.polylines(image,
                            [segment],
                            isClosed=True,
                            color=color,
                            thickness=self.linewidth)
        return image

    def draw_mask(self, image, mask, z, color):
        """
        Draw mask on image

        a mask is a polygon defined by a list of points
        """
        #rescale coordinates within mask
        mask *= z

        #round coordinates and draw mask on image
        mask = np.int64(mask).reshape((-1, 1, 2))

        image= cv2.fillPoly(image,
                            [mask],
                            color=color)

        return image

    def resize_app(self):
        """
        Adjust the size of self.annotation_canvas (where the image is displayed) to the
        application size
        """
        uw = self.winfo_width() #useable_width
        uh = self.winfo_height() #useable_height
        if self.uw!=uw or self.uh!=uh:
            self.uw = uw
            self.uh = uh
            self.config(width=uw,
                        height=uh)
            if self.image.image is not None:
                self.set_nominal_scale()
                self.updateImage()


    def set_nominal_scale(self):
        """
        Calculate nominal scale: factor with which the image has to be rescaled
        to show it as large as possible in self.annotation_canvas if there is not zoomed
        """
        image_height, image_width = self.image.image.shape[:2]
        uw = self.winfo_width()
        uh = self.winfo_height()
        self.nominal_scale = min(uw/image_width, uh/image_height)

    def reset(self):

        #reset attributes containing variables
        self.zoom_level = 1.0
        self.x_zoom_center_image = 0
        self.y_zoom_center_image = 0
        self.zoom_delta_x = 0
        self.zoom_delta_y = 0
        self.mouse_x = 0
        self.mouse_y = 0

    def set_mode(self, mode):
        """
        Set display parameters of application
        """
        if mode==0:
            #Classic bbox
            self.show_pbbox = True
            self.show_rbbox = False
            self.show_convex_hull = False
            self.show_segment = False
        elif mode==1:
            #Convex hull
            self.show_pbbox = False
            self.show_rbbox = False
            self.show_convex_hull = True
            self.show_segment = False
        elif mode==2:
            #convex hull + rotated bbox
            self.show_pbbox = False
            self.show_rbbox = True
            self.show_convex_hull = True
            self.show_segment = False
        elif mode==3:
            #Segmentation
            self.show_pbbox = False
            self.show_rbbox = False
            self.show_convex_hull = False
            self.show_segment = True
        elif mode==4:
            #Segmentation + rotated bbox
            self.show_pbbox = False
            self.show_rbbox = True
            self.show_convex_hull = False
            self.show_segment = True
        elif mode==5:
            #Segmentation + convex hull + rotated bbox
            self.show_pbbox = False
            self.show_rbbox = True
            self.show_convex_hull = True
            self.show_segment = True

        #Update image
        self.updateImage(from_scratch=True)
