# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:56:00 2021

@author: Maarten
"""
#%% packages
import numpy as np
import pandas as pd
import os
import cv2
import tkinter.messagebox as tkmessagebox
import json

from surrounding_polygons import surrounding_polygons
from classic_bbox import classic_bbox

#%%

class ImageObject():

    def __init__(self,
                 master):

        self.master = master
        self.project = self.master.project

        #names of objects
        self.names = pd.DataFrame(data=None,
                                  columns=["obj", "name"])

        #all annotated points
        self.annotation_points = pd.DataFrame(data=None,
                                              columns=["obj", "x", "y"])

        #annotated points of current object
        self.points = np.empty(shape=(0,2))

        #all (rotated) bbox information
        self.bboxes = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h", "theta"])

        #information about (rotated) bbox of current object
        self.bbox = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h", "theta"])

        #all bbox information for the bboxes parallel with the image axis
        self.pbboxes = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h"])

        #information about the bbox parallel with the image axis for the
        #current object
        self.pbbox = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h"])

        #classes of all annotated objects
        self.annotation_classes = pd.DataFrame(data=None,
                                              columns=["obj", "class"])

        #all convex hulls
        self.convex_hulls = {}

        #convex hull of the current object
        self.convex_hull = []

        #points of current masks
        self.points_mask = np.empty(shape=(0,2))
        #masks are defined as polygons

        #all points of masks
        self.annotation_points_masks = pd.DataFrame(data=None,
                                                   columns=["obj", "x", "y"])

        #names of masks
        self.names_masks = pd.DataFrame(data=None,
                                  columns=["obj", "name"])

        #declare attributes containing variables
        self.obj_id = 0 #id of current object
        self.point_id = 0 #id of last active point
        self.class_last = 0 #class of last confirmed object
        self.mask_id = 0 #id of current mask
        self.point_mask_last = 0 #id of last active point of mask

        self.image_name = None #name of the image
        self.image = None #image matrix

        #Declare attributes containing configuration/status information
        self.currently_saved = True #saved status
        self.current_object_confirmed = True
        #True if all properties of objects are stored in the overall dataframes
        self.mask_mode = False
        #True if the objects are modified, True if the masks are modified
        self.current_mask_confirmed = True
        #true if all properties of the masks are stored in the overall dataframes

    def reset_full(self):
        """
        Reset totally
        """

        self.image_name = None #name of the image
        self.image = None #image matrix

        self.reset_annotations()
        self.reset_masks()

        #Reset attributes containing configuration/status information
        self.currently_saved = True


    def reset(self):
        """
        Reset attributes to their default value
        """

        self.reset_annotations()
        self.reset_masks()

        #Reset attributes containing configuration/status information
        self.currently_saved = True

    def reset_annotations(self):
        """
        reset all attributes related to objects
        """

        #names of annotated objects
        self.names = pd.DataFrame(data=None,
                                  columns=["obj", "name"])

        #all annotated points
        self.annotation_points = pd.DataFrame(data=None,
                                              columns=["obj", "x", "y"])

        #annotated points of current object
        self.points = np.empty(shape=(0,2))

        #all (rotated) bbox information
        self.bboxes = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h", "theta"])

        #information about (rotated) bbox of current object
        self.bbox = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h", "theta"])

        #all bbox information for the bboxes parallel with the image axis
        self.pbboxes = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h"])

        #information about the bbox parallel with the image axis for the
        #current object
        self.pbbox = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h"])

        #classes of all annotated objects
        self.annotation_classes = pd.DataFrame(data=None,
                                              columns=["obj", "class"])

        #all convex hulls
        self.convex_hulls = {}

        #convex hull of the current object
        self.convex_hull = []

        #reset atributes containing variables
        self.obj_id = 0
        self.point_id = 0
        self.class_last = 0

        #Reset attributes containing configuration/status information
        self.current_object_confirmed = True

    def reset_masks(self):
        """
        reset all attributes related to masks
        """

        #points of current masks
        self.points_mask = np.empty(shape=(0,2))
        #masks are defined as polygons

        #all points of masks
        self.annotation_points_masks = pd.DataFrame(data=None,
                                                   columns=["obj", "x", "y"])

        #names of masks
        self.names_masks = pd.DataFrame(data=None,
                                  columns=["obj", "name"])

        #reset atributes containing variables
        self.mask_id = 0
        self.point_mask_last = 0

        #Reset attributes containing configuration/status information
        self.current_mask_confirmed = True

    def reset_active_object(self):

        #annotated points of current object
        self.points = np.empty(shape=(0,2))

        #information about (rotated) bbox of current object
        self.bbox = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h", "theta"])

        #information about the bbox parallel with the image axis for the
        #current object
        self.pbbox = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h"])

        #convex hull of the current object
        self.convex_hull = []

        #Reset attributes containing configuration/status information
        self.current_object_confirmed = True

        #reset object id
        if len(self.names["obj"])>0:
            self.obj_id = self.names["obj"].to_numpy().max() + 1
        else:
            #there is no object yet confirmed
            self.obj_id = 0

    def reset_active_mask(self):

        self.points_mask = np.empty(shape=(0,2))

        #reset mask id
        if len(self.names_masks["obj"])>0:
            self.mask_id = self.names_masks["obj"].to_numpy().max() + 1
        else:
            #there is no object yet confirmed
            self.mask_id = 0

    def load_image(self, filename):
        """
        Load an image, together with its annotations (if availabe)
        """

        #set self.project.wdir and self.filename
        if os.path.isabs(filename):
            #filename is an absolute path
            wdir, image_name = os.path.split(filename)
        else: #not os.path.isabs(filename):
            #filename is a relative path
            wdir = self.project.wdir
            image_name = filename

        #check if file is a valid image
        if (len(image_name.split("."))>1) and \
            image_name.split(".")[1] in ['jpg', 'png']:
            image_name_original = self.image_name

            if self.currently_saved is True and image_name_original is not None:
                #annotations are saved and there is currently yet an image shown
                self.project.wdir = wdir
                self.image_name = image_name
                self.import_image()

            elif self.currently_saved is False and image_name_original is not None:
                #there are currently unsaved changes in the annotations
                answer = tkmessagebox.askyesnocancel("Save modifications",
                        "do you want to save the annotation changes you made \n" +\
                            "for the current image?")
                if answer is True:
                    #Save changes
                    self.save()
                    self.project.wdir = wdir
                    self.image_name = image_name
                    self.import_image()
                elif answer is False:
                    #Discard changes
                    self.project.wdir = wdir
                    self.image_name = image_name
                    self.import_image()
                #else: #answer==None
                    #nothing has to be done

            else: #image_name_original==None
                #there is currently no image shown
                self.project.wdir = wdir
                self.image_name = image_name
                self.import_image()

        else:
            #there was selected an object, but it was not a supported image
            tkmessagebox.showerror("Invalid file",
                                    "Only files with the extension .jpg or .png are supported")

    def import_image(self):
        """
        Import image and load annotations (if available)
        """

        #Update title of application
        self.master.master.title("CoBRA annotation tool " + self.image_name)

        #reset parameters
        self.reset()
        self.master.annotation_canvas.reset()
        self.master.reset_parameters()

        #change working directory
        os.chdir(self.project.wdir)

        #import image
        image = cv2.imread(self.image_name)
        self.image= cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        #Set nominal scale
        self.master.annotation_canvas.set_nominal_scale()

        #Load annotations and masks
        self.load_data()

        self.master.data_canvas.object_canvas.load_objects()
        self.master.data_canvas.object_canvas.load_masks()
        self.master.annotation_canvas.updateImage()

    def load_data(self):
        """
        Load anotations
        """

        #reset all annotation related attributes to their default value
        self.reset_annotations()
        self.reset_masks()

        #look if there is a .json file with annotations
        data_file = self.image_name.split(".")[0] + ".json"

        if data_file not in os.listdir(self.project.wdir):
            #There is no .json file with annotations and masks available
            return

        #data_file in os.listdir(self.project.wdir)

        #read json file
        with open(self.image_name.split(".")[0] + ".json") as f:
            data = json.load(f)

        data_objects = data["objects"]

        if "masks" in data:
            data_masks = data["masks"]
        else:
            data_masks = {}

        if data_objects:
            #data_objects is not an empty dictionary

            #write data in data_objects to right attribute dataframes of self

            obj_ids = []
            classes = []
            names = []
            points_x = []
            points_y = []
            points_obj = []


            for key, object_dict in data_objects.items():

                obj_ids.append(int(key))

                if "class" in object_dict:
                    classes.append(object_dict["class"])
                elif "category" in object_dict:
                    #this case is present to keep compatability with previous
                    #versions of the software
                    classes.append(object_dict["category"])
                else:
                    classes.append(None)

                if "name" in object_dict:
                    names.append(object_dict["name"])
                else:
                    #this case is present to keep compatability with previous
                    #versions of the software
                    names.append(key)

                for point_key, point_dict in object_dict["points"].items():
                    points_x.append(point_dict["x"])
                    points_y.append(point_dict["y"])
                    points_obj.append(int(key))

            #assign names to self.names
            names_dict = {"obj": obj_ids,
                          "name": names}
            self.names = pd.DataFrame(names_dict)

            #assign classes to self.annotation_classes
            classes_dict = {"obj": obj_ids,
                            "class": classes}
            self.annotation_classes = pd.DataFrame(classes_dict)

            #assign points to self.annotation_points
            object_points_dict = {"obj": points_obj,
                                  "x": points_x,
                                  "y": points_y}
            self.annotation_points = pd.DataFrame(object_points_dict)


            #calculate for each object the convex hull, bbox and pbbox (bbox
            #parallel to image axes)
            for obj in self.names["obj"]:
                points = self.annotation_points.loc[
                    self.annotation_points["obj"]==obj,["x", "y"]].\
                    to_numpy()

                convex_hull, bbox = surrounding_polygons(points)
                pbbox = classic_bbox(points)

                bbox = pd.DataFrame(data=[bbox],
                                       columns=["x", "y", "w", "h", "theta"])
                bbox["obj"] = obj
                if len(self.bboxes)==0:
                    self.bboxes = bbox
                else:
                    self.bboxes = pd.concat((self.bboxes, bbox),axis=0).\
                        reset_index(drop=True)

                self.convex_hulls[str(obj)] = convex_hull

                pbbox = pd.DataFrame(data=[pbbox],
                                     columns=["x", "y", "w", "h"])
                pbbox["obj"] = obj
                if len(self.pbboxes)==0:
                    self.pbboxes = pbbox
                else:
                    self.pbboxes = pd.concat((self.pbboxes, pbbox), axis=0).\
                        reset_index(drop=True)

            #set self.obj_id to id of next object
            self.obj_id = obj_ids[-1] + 1


        if data_masks:
            #data_masks is not an empty dictionary

            #write data in masks to right attribute dataframes of self
            self.mask_id = 0
            for key, mask in data_masks.items():

                #add name to self.names
                df = self.names_masks
                if 'name' in mask:
                    new_mask = pd.DataFrame(data=[[self.mask_id, mask["name"]]],
                                          columns=df.columns)
                else:
                    #this case is present to keep compatability with annotations
                    #made with a previous version of CoBRA annotation tool
                    new_mask = pd.DataFrame(data=[[self.mask_id, key]],
                                          columns=df.columns)

                df = pd.concat((df, new_mask), axis=0).reset_index(drop=True)
                self.names_masks = df

                #add points to self.annotation_points_masks
                points_dict = mask["points"]
                points = []
                for j in points_dict.keys():
                    x = points_dict[j]["x"]
                    y = points_dict[j]["y"]
                    points.append([x, y])
                points = pd.DataFrame(data=points,
                                  columns=["x", "y"])
                points["obj"] = self.mask_id
                if len(self.annotation_points_masks) == 0:
                    self.annotation_points_masks = points
                else:
                    self.annotation_points_masks =\
                        pd.concat((self.annotation_points_masks, points), axis=0).\
                        reset_index(drop=True)

                #increase self.mask_id with 1
                self.mask_id += 1

    def add_point(self, x, y, scale):

        if self.mask_mode:
            #add a point to a mask
            return self.add_point_mask(x, y, scale)
        else:
            #add a point to an object
            return self.add_point_object(x, y, scale)

    def add_point_object(self, x, y, scale):
        s = scale
        #set saved state to false
        self.currently_saved = False

        #set object_confirmed state to False
        self.current_object_confirmed = False


        self.point_active = False
        if (x<=self.image.shape[1]) and (y<=self.image.shape[0]):
            #Check if a point in the image is activated and not a point
            #in the surrounding grey area
            self.point_active = True
            if len(self.points)>0:
                #check if you have to replace a yet existing point or if you have
                #to create a new point
                dist_to_points = np.sqrt(np.sum(np.square(\
                            self.points - np.array([[x, y]])), axis=1)) * s
                if min(dist_to_points)<=self.master.dist_max:
                    #replace a yet existing point
                    self.point_id = np.argmin(dist_to_points)
                else:
                    #add an extra point
                    if len(self.points) >=3:
                        #check if you have to add an extra point at the end, or you have to
                        #split an edge

                        #calculate orthogonal distance to edges
                        C = np.array([[x * s, y * s]])
                        points = self.points * s

                        A = points
                        B = np.concatenate((points[1:], [points[0]]), axis=0)
                        u = B-A
                        v = np.concatenate((-u[:,1].reshape(-1,1), u[:,0].\
                                            reshape(-1,1)), axis=1)
                        v = v / np.linalg.norm(v, axis=1).reshape(-1,1)

                        ac = A - C #vectors from A to C

                        #orthogonal distances to edges
                        d = np.abs((ac * v).sum(-1))

                        if min(d)<=self.master.dist_max:
                            #split (possibly) an edge
                            insert_index = np.argmin(d) + 1

                            #check if point is in sensitive zone
                            i = insert_index
                            A = self.points.copy()
                            A = np.concatenate((A, A[0,:].reshape(-1,2)), axis=0)
                            x_min = min(A[i - 1,0], A[i,0])
                            x_max = max(A[i - 1,0], A[i,0])
                            y_min = min(A[i - 1,1], A[i,1])
                            y_max = max(A[i - 1,1], A[i,1])
                            if (x<=x_max) and (x>=x_min) and\
                                (y<=y_max) and (y>=y_min):
                                #point is in sensitive zone
                                #split edge
                                self.points = np.concatenate(\
                                    (self.points[:insert_index].reshape(-1,2),
                                     [[x, y]],
                                     self.points[insert_index:].reshape(-1,2)),
                                    axis=0)
                                self.point_id = insert_index
                            else:
                                #point is not in sensitive zone
                                #add extra point at the end of self.points
                                self.point_id = len(self.points)
                                self.points = np.append(self.points,[[x, y]], axis=0)
                        else: #min(d)>dist_max
                            #add extra point at the end of self.points
                            self.point_id = len(self.points)
                            self.points = np.append(self.points,[[x, y]], axis=0)
                    else: #len(self.points)<3:
                        #add extra point at the end of self.points
                        self.point_id = len(self.points)
                        self.points = np.append(self.points,[[x, y]], axis=0)
            else: #len(self.points)==0:
                #add first point in self.points
                self.point_id = len(self.points)
                self.points = np.append(self.points,[[x, y]], axis=0)

            #update convex hull and rotated bbox
            if len(self.points)>=3:
                convex_hull, bbox = surrounding_polygons(np.array(self.points))
                self.convex_hull = convex_hull
                bbox = pd.DataFrame(data=[bbox],
                                    columns=["x", "y", "w", "h", "theta"])
                bbox["obj"] = self.obj_id
                self.bbox = bbox

            #update bbox parralel with axes of image
            if len(self.points)>=2:
                pbbox = classic_bbox(self.points)
                pbbox = pd.DataFrame(data=[pbbox],
                                    columns=["x", "y", "w", "h"])
                pbbox["obj"] = self.obj_id
                self.pbbox = pbbox

            #if a valid point was added, return True
            return True

        #if no valid point was added, return False
        return False

    def add_point_mask(self, x, y, scale):

        if not self.master.data_canvas.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        s = scale
        #set saved state to false
        self.currently_saved = False

        #set object_confirmed state to False
        self.current_mask_confirmed = False

        self.point_active = False
        if (x<=self.image.shape[1]) and (y<=self.image.shape[0]):
            #Check if a point in the image is activated and not a point
            #in the surrounding grey area

            #if a point is close to the borders, adapt x and y, so point is
            #drawn on the borders
            if x * s <= 20:
                x = 0
            elif (self.image.shape[1] - x) * s <= 20:
                x = self.image.shape[1] - 1

            if y * s <= 20:
                y = 0
            elif (self.image.shape[0] - y) * s <= 20:
                y = self.image.shape[0] - 1

            self.point_active = True
            if len(self.points_mask)>0:
                #check if you have to replace a yet existing point or if you have
                #to create a new point
                dist_to_points = np.sqrt(np.sum(np.square(\
                            self.points_mask - np.array([[x, y]])), axis=1)) * s

                if min(dist_to_points)<=self.master.dist_max:
                    #replace a yet existing point
                    self.point_id = np.argmin(dist_to_points)
                else:
                    #add an extra point
                    if len(self.points_mask) >=3:
                        #check if you have to add an extra point at the end, or you have to
                        #split an edge

                        #calculate orthogonal distance to edges
                        C = np.array([[x * s, y * s]])
                        points = self.points_mask * s

                        A = points
                        B = np.concatenate((points[1:], [points[0]]), axis=0)
                        u = B-A
                        v = np.concatenate((-u[:,1].reshape(-1,1), u[:,0].\
                                            reshape(-1,1)), axis=1)
                        v = v / np.linalg.norm(v, axis=1).reshape(-1,1)

                        ac = A - C #vectors from A to C

                        #orthogonal distances to edges
                        d = np.abs((ac * v).sum(-1))

                        if min(d)<=self.master.dist_max:
                            #split (possibly) an edge
                            insert_index = np.argmin(d) + 1

                            #check if point is in sensitive zone
                            i = insert_index
                            A = self.points_mask.copy()
                            A = np.concatenate((A, A[0,:].reshape(-1,2)), axis=0)
                            x_min = min(A[i - 1,0], A[i,0])
                            x_max = max(A[i - 1,0], A[i,0])
                            y_min = min(A[i - 1,1], A[i,1])
                            y_max = max(A[i - 1,1], A[i,1])
                            if (x<=x_max) and (x>=x_min) and\
                                (y<=y_max) and (y>=y_min):
                                #point is in sensitive zone
                                #split edge
                                self.points_mask = np.concatenate(\
                                    (self.points_mask[:insert_index].reshape(-1,2),
                                     [[x, y]],
                                     self.points_mask[insert_index:].reshape(-1,2)),
                                    axis=0)
                                self.point_id = insert_index
                            else:
                                #point is not in sensitive zone
                                #add extra point at the end of self.points_mask
                                self.point_id = len(self.points_mask)
                                self.points_mask = np.append(self.points_mask,[[x, y]], axis=0)
                        else: #min(d)>dist_max
                            #add extra point at the end of self.points
                            self.point_id = len(self.points_mask)
                            self.points_mask = np.append(self.points_mask,[[x, y]], axis=0)
                    else: #len(self.points)<3:
                        #add extra point at the end of self.points
                        self.point_id = len(self.points_mask)
                        self.points_mask = np.append(self.points_mask,[[x, y]], axis=0)
            else: #len(self.points)==0:
                #add first point in self.points
                self.point_id = len(self.points_mask)
                self.points_mask = np.append(self.points_mask,[[x, y]], axis=0)

            #if a valid point was added, return True
            return True

        #if no valid point was added, return False
        return False

    def update_point(self, x, y):
        """
        update the position of the point which is currently active
        """

        if self.mask_mode:

            if not self.master.data_canvas.object_canvas.masks_visible:
                #if masks are not visible, no modifications to the masks may be done
                return

            self.update_point_mask(x, y)
        else:
            self.update_point_object(x, y)

    def update_point_object(self, x, y):
        #set saved state to false
        self.currently_saved = False

        #set object_confirmed state to False
        self.current_object_confirmed = False

        #update position of currently active point
        self.points[self.point_id,:] += np.array([x, y])

        if len(self.points)>=3:
            #update self.convex_hull and self.bbox
            convex_hull, bbox = surrounding_polygons(np.array(self.points))
            self.convex_hull = convex_hull
            bbox = pd.DataFrame(data=[bbox],
                                columns=["x", "y", "w", "h", "theta"])
            bbox["obj"] = self.obj_id
            self.bbox = bbox

        if len(self.points)>=2:
            #update self.pbbox
            pbbox = classic_bbox(self.points)
            pbbox = pd.DataFrame(data=[pbbox],
                                columns=["x", "y", "w", "h"])
            pbbox["obj"] = self.obj_id
            self.pbbox = pbbox

    def update_point_mask(self, x, y):

        if not self.master.data_canvas.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        #set saved state to false
        self.currently_saved = False

        #set object_confirmed state to False
        self.current_mask_confirmed = False

        #update position of currently active point
        self.points_mask[self.point_id,:] += np.array([x, y])

    def newbbox(self):
        if self.mask_mode:
            self.newbbox_mask()
        else:
            self.newbbox_object()

    def newbbox_object(self):
        """
        Confirm current object
        """

        if len(self.points)>=3:
            #an object can be only confirmed if it has at least 3 points

            #save class
            if self.obj_id in self.annotation_classes["obj"]:
                #adapted object

                #update self.annotation_classes
                df = self.annotation_classes
                df.loc[df["obj"] == self.obj_id, "class"] = self.class_last

                #update self.annotation_points
                indices_to_drop = self.annotation_points.loc[self.annotation_points["obj"] == self.obj_id,].index
                self.annotation_points = self.annotation_points.drop(indices_to_drop)

                points = pd.DataFrame(data=self.points,
                                      columns=["x", "y"])
                points["obj"] = self.obj_id
                if len(self.annotation_points) == 0:
                    self.annotation_points = points
                else:
                    self.annotation_points =\
                        pd.concat((self.annotation_points, points), axis=0).\
                        reset_index(drop=True)
                self.points = np.empty(shape=(0,2))

                #add self.bbox to self.bboxes
                self.bboxes.loc[self.bboxes["obj"] == self.obj_id, ["x", "y", "w", "h", "theta"]] =\
                    self.bbox.loc[self.bbox["obj"] == self.obj_id, ["x", "y", "w", "h", "theta"]]

                self.bbox = pd.DataFrame(data=None,
                                         columns=["obj", "x", "y", "w", "h", "theta"])

                #add self.convex_hull to self.convex_hulls
                self.convex_hulls[str(self.obj_id)] = self.convex_hull
                self.convex_hull = []

                #add self.pbbox to self.pbboxes
                self.pbboxes.loc[self.pbboxes["obj"] == self.obj_id, ["x", "y", "w", "h"]] =\
                    self.pbbox.loc[self.pbbox["obj"] == self.obj_id, ["x", "y", "w", "h"]]

                self.pbbox = pd.DataFrame(data=None,
                                          columns=["obj", "x", "y", "w", "h"])

            else:
                #new object

                #save name of object (default)
                dict_name = {'obj': [self.obj_id,],
                             'name': [str(self.obj_id),]}
                df_name = pd.DataFrame(dict_name)
                if len(self.names) == 0:
                    self.names = df_name
                else:
                    self.names = pd.concat((self.names, df_name),
                                           axis=0,
                                           ignore_index=True)

                #save class
                df_obj = self.annotation_classes
                new_obj = pd.DataFrame(data=[[self.obj_id, self.class_last]],
                                      columns=df_obj.columns)
                if len(df_obj) == 0:
                    df_obj = new_obj
                else:
                    df_obj = pd.concat((df_obj, new_obj), axis=0).\
                        reset_index(drop=True)
                self.annotation_classes = df_obj

                #add self.points to self.annotation_points
                points = pd.DataFrame(data=self.points,
                                      columns=["x", "y"])
                points["obj"] = self.obj_id
                if len(self.annotation_points) == 0:
                    self.annotation_points = points.copy()
                else:
                    self.annotation_points =\
                        pd.concat((self.annotation_points, points), axis=0).\
                        reset_index(drop=True)
                self.points = np.empty(shape=(0,2))

                #add self.bbox to self.bboxes
                if len(self.bboxes) == 0:
                    self.bboxes = self.bbox.copy()
                else:
                    self.bboxes = pd.concat((self.bboxes, self.bbox), axis=0).\
                        reset_index(drop=True)
                self.bbox = pd.DataFrame(data=None,
                                         columns=["obj", "x", "y", "w", "h", "theta"])

                #add self.convex_hull to self.convex_hulls
                self.convex_hulls[str(self.obj_id)] = self.convex_hull
                self.convex_hull = []

                #add self.pbbox to self.pbboxes
                if len(self.pbboxes) == 0:
                    self.pbboxes = self.pbbox.copy()
                else:
                    self.pbboxes = pd.concat((self.pbboxes, self.pbbox), axis=0).\
                        reset_index(drop=True)
                self.pbbox = pd.DataFrame(data=None,
                                          columns=["obj", "x", "y", "w", "h"])

                #add object to listbox of object_canvas
                self.master.data_canvas.object_canvas.add_object(dict_name["name"])

            #set self.obj_id to object id of next object
            self.obj_id = self.names["obj"].max() + 1

            #set object_confirmed state to False
            self.current_object_confirmed = True

            #update image
            self.master.annotation_canvas.updateImage(from_scratch=True)

        elif (len(self.points)==2) and self.show_pbbox is True:
            #Classic bbox mode
            #only 2 corners of the rectangle were drawn
            #add a other corners to make the software doesn't crash if there is
            #switched of mode

            x_min = self.points[:,0].min()
            x_max = self.points[:,0].max()
            y_min = self.points[:,1].min()
            y_max = self.points[:,1].max()

            self.points = np.array([[x_min, y_min],
                                    [x_max, y_min],
                                    [x_max, y_max],
                                    [x_min, y_max]])

            #assign self.convex hull and self.bbox
            convex_hull, bbox = surrounding_polygons(np.array(self.points))
            self.convex_hull = convex_hull
            bbox = pd.DataFrame(data=[bbox],
                                columns=["x", "y", "w", "h", "theta"])
            bbox["obj"] = self.obj_id
            self.bbox = bbox

            #confirm object
            self.newbbox()

    def newbbox_mask(self):
        """
        Confirm current mask
        """

        if not self.master.data_canvas.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        if len(self.points_mask)>=3:
            #a mask can be only confirmed if it has at least 3 points

            #save class
            if self.mask_id in self.names_masks["obj"]:
                #adapted mask

                #update self.annotation_points_masks
                indices_to_drop = self.annotation_points_masks.loc[self.annotation_points_masks["obj"] == self.mask_id,].index
                self.annotation_points_masks = self.annotation_points_masks.drop(indices_to_drop)

                points = pd.DataFrame(data=self.points_mask,
                                      columns=["x", "y"])
                points["obj"] = self.mask_id
                if len(self.annotation_points_masks) == 0:
                    self.annotation_points_masks = points
                else:
                    self.annotation_points_masks =\
                        pd.concat((self.annotation_points_masks, points), axis=0).\
                        reset_index(drop=True)
                self.points_mask = np.empty(shape=(0,2))

            else:
                #new mask

                #save name of mask (default)
                dict_name = {'obj': [self.mask_id,],
                             'name': [str(self.mask_id),]}
                df_name = pd.DataFrame(dict_name)
                if len(self.names_masks) == 0:
                    self.names_masks = df_name
                else:
                    self.names_masks = pd.concat((self.names_masks, dict_name),
                                                 axis=0, ignore_index=True)

                #add self.points to self.annotation_points
                points = pd.DataFrame(data=self.points_mask,
                                      columns=["x", "y"])
                points["obj"] = self.mask_id
                if len(self.annotation_points_masks) == 0:
                    self.annotation_points_masks = points
                else:
                    self.annotation_points_masks =\
                        pd.concat((self.annotation_points_masks, points), axis=0).\
                        reset_index(drop=True)
                self.points_mask = np.empty(shape=(0,2))

                #add object to listbox of object_canvas
                self.master.data_canvas.object_canvas.add_mask(dict_name["name"])

            #set self.obj_id to object id of next object
            self.mask_id = self.names_masks["obj"].max() + 1

            #set object_confirmed state to False
            self.current_mask_confirmed = True

            #update image
            self.master.annotation_canvas.updateImage(from_scratch=True)

    def returnbbox(self):
        if self.master.project.wdir is None:
            #check if a project is loaded
            return

        if self.mask_mode:
            if not self.master.data_canvas.object_canvas.masks_visible:
                #if masks are not visible, no modifications to the masks may be done
                return

            self.return_mask()
        else:
            self.return_object()

    def return_object(self):
        """
        Undo last changes

        Sequence:
            - last point
            - points of current object in order
            - confirmed objects in order
        """

        #check if current object has points
        if len(self.points)>0:
            if len(self.points)>3:
                #delete point
                self.points = np.delete(self.points,self.point_id, axis=0)

                #update self.point_id
                self.point_id = len(self.points) - 1

                #update self.convex_hull and self.bbox
                convex_hull, bbox = surrounding_polygons(self.points)
                self.convex_hull = convex_hull
                bbox = pd.DataFrame(data=[bbox],
                                    columns=["x", "y", "w", "h", "theta"])
                bbox["obj"] = self.obj_id
                self.bbox = bbox

                #update self.pbbox
                pbbox = classic_bbox(self.points)
                pbbox = pd.DataFrame(data=[pbbox],
                                    columns=["x", "y", "w", "h"])
                pbbox["obj"] = self.obj_id
                self.pbbox = pbbox

            elif len(self.points)==3:
                #delete point
                self.points = np.delete(self.points,self.point_id, axis=0)

                #update self.point_id
                self.point_id = len(self.points) - 1

                #reset self.bbox and self.convex_hull
                self.bbox = pd.DataFrame(data=None,
                                   columns=["obj", "x", "y", "w", "h", "theta"])
                self.convex_hull = []

                #update self.pbbox
                pbbox = classic_bbox(self.points)
                pbbox = pd.DataFrame(data=[pbbox],
                                    columns=["x", "y", "w", "h"])
                pbbox["obj"] = self.obj_id
                self.pbbox = pbbox

            elif len(self.points)==2:
                #delete point
                self.points = np.delete(self.points,self.point_id, axis=0)

                #update self.point_id
                self.point_id = len(self.points) - 1

                #reset self.pbbox
                self.pbbox = pd.DataFrame(data=None,
                                          columns=["obj", "x", "y", "w", "h"])

            else: #len(self.points)==1:
                self.points = np.empty(shape=(0,2))
                self.point_id = 0

        else: #len(self.points)==0
            #current object is normally totally empty

            #lower current object id
            self.obj_id -= 1

            #remove all information of current object
            self.names = self.names.iloc[:-1,:]
            self.bboxes = self.bboxes.iloc[:-1,:]
            self.pbboxes = self.pbboxes.iloc[:-1,:]
            self.annotation_points = self.annotation_points.loc[\
                                    self.annotation_points["obj"]!=self.obj_id,:]
            _ = self.convex_hulls.pop(str(self.obj_id))
            self.annotation_classes = self.annotation_classes.iloc[:-1,:]

        #set self.currently_saved to False
        self.currently_saved = False

        #update image
        self.master.annotation_canvas.updateImage()

    def return_mask(self):
        """
        Undo last changes

        Sequence:
            - last point
            - points of current mask in order
            - confirmed masks in order
        """

        if not self.master.data_canvas.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        #check if current mask has points
        if len(self.points_mask)>0:
            if len(self.points_mask)>1:
                #delete point
                self.points_mask = np.delete(self.points_mask,self.point_id, axis=0)

                #update self.point_id
                self.point_id = len(self.points_mask) - 1

            else: #len(self.points_mask)==1:
                self.points_mask = np.empty(shape=(0,2))
                self.point_id = 0

        else: #len(self.points_mask)==0
            #current mask is normally totally empty

            #lower current mask id
            self.mask_id -= 1

            #remove all information of current object
            self.names_masks = self.names_masks.loc[self.names_masks["obj"]!=self.mask_id,:]
            self.annotation_points_masks = self.annotation_points_masks.loc[\
                                    self.annotation_points_masks["obj"]!=self.mask_id,:]

        #set self.currently_saved to False
        self.currently_saved = False

        #update image
        self.master.annotation_canvas.updateImage()

    def save(self):

        if self.image is None:
            #set saved state to True
            self.currently_saved = True

            #there is nothing to save, so return
            return

        #self.image is not None

        #get dictionary with object data

        #check if current (non-confirmed) object can be saved
        if len(self.points) > 0:
            #if it's possible to save the current (non-confirmed) object,
            #save this object
            self.newbbox()

        #all information of the objects that has to be saved is in
        #self.annotation_points and self.annotation_classes

        if len(self.annotation_points)==0:
            data_objects = {}
        else:
            #there is data to save
            #fuse self.names, self.annotation_points and self.annotation_classes
            #in one dictionary
            data_objects={}
            for obj_id in self.names["obj"]:
                #get obj_name
                obj_name = self.names.loc[self.names["obj"]==obj_id, 'name'].iloc[0]

                #get object class
                obj_class = self.annotation_classes.loc[self.annotation_classes["obj"]==obj_id, "class"].iloc[0]

                #get object points
                points = self.annotation_points.loc[self.annotation_points["obj"]==obj_id,\
                                                    ["x","y"]].round(2)

                #convert points pd.DataFrame to dict
                points_dict = {}
                for i in range(len(points)):
                    points_dict[i] = points.iloc[i,].to_dict(({}))

                #assembly dict for object
                obj = {"name": obj_name,
                       "class": int(obj_class),
                       "points": points_dict}

                #add object dict to data
                data_objects[obj_id] = obj

        #get dictionary with mask data

        #check if current (non-confirmed) mask can be saved
        if len(self.points_mask) > 0:
            #if it's possible to save the current (non-confirmed) mask,
            #save this mask
            self.newbbox()

        #all information that has to be saved is in self.annotation_points_masks and
        #self.names_masks

        if len(self.annotation_points_masks)==0:
            data_masks = {}
        else:
            #there is data to save
            #fuse self.names_masks, self.annotation_points_masks in one dictionary
            data_masks={}
            for mask_id in self.names_masks["obj"]:
                #get mask_name
                mask_name = self.names_masks.loc[self.names_masks["obj"]==mask_id, 'name'].iloc[0]

                #get mask points
                points = self.annotation_points_masks.loc[self.annotation_points_masks["obj"]==mask_id,\
                                                    ["x","y"]].round(2)

                #convert points from pd.DataFrame to dict
                points_dict = {}
                for i in range(len(points)):
                    points_dict[i] = points.iloc[i,].to_dict(({}))

                #assembly dict for object
                mask = {"name": mask_name,
                       "points": points_dict}

                #add object dict to data
                data_masks[mask_id] = mask


        #check if there is data to be saved
        if not data_objects and not data_masks:
            #empty dictionaries evaluate to False in Python

            #check if there exists a .json file for the opened image and
            #remove it if existing (empty .json files are unwanted)
            if self.image_name.split(".")[0] + ".json" in os.listdir(self.project.wdir):
                os.remove(self.image_name.split(".")[0] + ".json")

        else:
            #construct overall dictionary
            data = {"objects": data_objects,
                    "masks": data_masks}

            #save data to .json file
            with open(self.image_name[:-4] + ".json", 'w') as f:
                json.dump(data, f, indent=4)

        #set saved state to True
        self.currently_saved = True

    def save_annotations(self):
        """
        Save annotations

        The annotations will be saved in the directory of the image in a .json
        file with the same filename as the image
        """
        if self.image is not None:
            if len(self.points)>0:
                #if it's possible to save the current (non-confirmed) object,
                #save this object
                self.newbbox()

            #all information that has to be saved is in self.annotation_points and
            #self.annotation_classes

            if len(self.annotation_points)==0:
                #there is no data to be saved or all data was removed

                #check if there exists a .json file for the opened image and
                #remove it if existing (empty .json files are unwanted)
                if self.image_name.split(".")[0] + ".json" in os.listdir(self.project.wdir):
                    os.remove(self.image_name.split(".")[0] + ".json")
            else:
                #there is data to save
                #fuse self.names, self.annotation_points and self.annotation_classes
                #in one dictionary
                data={}
                for obj_id in self.names["obj"]:
                    #get obj_name
                    obj_name = self.names.loc[self.names["obj"]==obj_id, 'name'].iloc[0]

                    #get object class
                    obj_class = self.annotation_classes.loc[self.annotation_classes["obj"]==obj_id, "class"].iloc[0]

                    #get object points
                    points = self.annotation_points.loc[self.annotation_points["obj"]==obj_id,\
                                                        ["x","y"]].round(2)

                    #convert points pd.DataFrame to dict
                    points_dict = {}
                    for i in range(len(points)):
                        points_dict[i] = points.iloc[i,].to_dict(({}))

                    #assembly dict for object
                    obj = {"name": obj_name,
                           "class": int(obj_class),
                           "points": points_dict}

                    #add object dict to data
                    data[obj_id] = obj

                #save data to .json file
                with open(self.image_name[:-4] + ".json", 'w') as f:
                    json.dump(data, f, indent=4)

    def save_masks(self):
        """
        Save masks

        The annotations will be saved in the directory of the image in a .json
        file with following filename: imagename_mask.json
        """

        if self.image is not None:
            if len(self.points_mask)>0:
                #if it's possible to save the current (non-confirmed) mask,
                #save this mask
                self.newbbox()

            #all information that has to be saved is in self.annotation_points_masks and
            #self.names_masks

            if len(self.annotation_points_masks)==0:
                #there is no data to be saved or all data was removed

                #check if there exists a .json file for the opened image and
                #remove it if existing (empty .json files are unwanted)
                if self.image_name.split(".")[0] + "_mask.json" in os.listdir(self.project.wdir):
                    os.remove(self.image_name.split(".")[0] + "_mask.json")
            else:
                #there is data to save
                #fuse self.names_masks, self.annotation_points_masks in one dictionary
                data={}
                for mask_id in self.names_masks["obj"]:
                    #get mask_name
                    mask_name = self.names_masks.loc[self.names_masks["obj"]==mask_id, 'name'].iloc[0]

                    #get mask points
                    points = self.annotation_points_masks.loc[self.annotation_points_masks["obj"]==mask_id,\
                                                        ["x","y"]].round(2)

                    #convert points from pd.DataFrame to dict
                    points_dict = {}
                    for i in range(len(points)):
                        points_dict[i] = points.iloc[i,].to_dict(({}))

                    #assembly dict for object
                    mask = {"name": mask_name,
                           "points": points_dict}

                    #add object dict to data
                    data[mask_id] = mask

                #save data to .json file
                with open(self.image_name[:-4] + "_mask.json", 'w') as f:
                    json.dump(data, f, indent = 3)


    def update_active_object(self, obj_id=None, obj_name=None):

        #process arguments
        if obj_id is None and obj_name is None:
            raise ValueError("obj_id and obj_name may not be both None")
        elif obj_id is not None and obj_name is not None:
            raise ValueError("obj_id and obj_name may not be given both")
        elif obj_name is not None:
            #only obj_name is given
            #get obj_id
            obj_id = self.names.loc[self.names["name"]==obj_name, "obj"].iloc[0]


        #first store all adaptations to the current object (if necessary)
        #to the general dataframes
        if self.current_object_confirmed is False:
            self.newbbox()

        #set id of active object
        self.obj_id = obj_id #id of current object

        #set points of active object
        self.points = self.annotation_points.loc[self.annotation_points["obj"]==self.obj_id,
                                                 ["x", "y"]].to_numpy()

        #set id of last active point of object (set to last point of object)
        self.point_id = len(self.points) - 1

        #set class of active object
        self.class_last = self.annotation_classes.loc[self.annotation_classes["obj"]==self.obj_id, "class"].iloc[0]

        #set convex hull and rotated bbox
        if len(self.points)>=3:
            convex_hull, bbox = surrounding_polygons(np.array(self.points))
            self.convex_hull = convex_hull
            bbox = pd.DataFrame(data=[bbox],
                                columns=["x", "y", "w", "h", "theta"])
            bbox["obj"] = self.obj_id
            self.convex_hull = convex_hull
            self.bbox = bbox

        #set bbox parralel with axes of image
        if len(self.points)>=2:
            pbbox = classic_bbox(self.points)
            pbbox = pd.DataFrame(data=[pbbox],
                                columns=["x", "y", "w", "h"])
            pbbox["obj"] = self.obj_id
            self.pbbox = pbbox

        self.master.data_canvas.class_canvas.class_var.set(self.class_last)
        self.master.annotation_canvas.updateImage(from_scratch=True)

    def update_active_mask(self, mask_id=None, mask_name=None):

        if not self.master.data_canvas.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        #process arguments
        if mask_id is None and mask_name is None:
            raise ValueError("mask_id and mask_name may not be both None")
        elif mask_id is not None and mask_name is not None:
            raise ValueError("mask_id and mask_name may not be given both")
        elif mask_name is not None:
            #only mask_name is given
            #get mask_id
            mask_id = self.names_masks.loc[self.names_masks["name"]==mask_name, "obj"].iloc[0]


        #first store all adaptations to the current mask (if necessary)
        #to the general dataframes
        if self.current_mask_confirmed is False:
            self.newbbox()

        #set id of active object
        self.mask_id = mask_id #id of current object

        #set points of active object
        self.points_mask = self.annotation_points_masks.loc[self.annotation_points_masks["obj"]==self.mask_id,
                                                 ["x", "y"]].to_numpy()

        #set id of last active point of mask (set to last point of mask)
        self.point_id = len(self.points_mask) - 1

        self.master.data_canvas.class_canvas.class_var.set(None)
        self.master.annotation_canvas.updateImage(from_scratch=True)

    def delete_object(self, obj_id=None, obj_name=None):

        #process arguments
        if obj_id is None and obj_name is None:
            raise ValueError("obj_id and obj_name may not be both None")
        elif obj_id is not None and obj_name is not None:
            raise ValueError("obj_id and obj_name may not be given both")
        elif obj_name is not None:
            #only obj_name is given
            #get obj_id
            obj_id = self.names.loc[self.names["name"]==obj_name, "obj"].iloc[0]

        #delete object
        #remark that it's impossible to remove an object under construction
        #since an object under construction is automatically confirmed when
        #clicking in the object_canvas

        #delete name of object
        self.names = self.names.loc[self.names["obj"] != obj_id,]
        self.names = self.names.reset_index(drop=True)

        #delete points of object
        df = self.annotation_points
        df = df.loc[df['obj'] != obj_id,]
        self.annotation_points = df.reset_index(drop=True)

        #delete (rotated) bbox information
        self.bboxes = self.bboxes.loc[self.bboxes['obj'] != obj_id,]
        self.bboxes.reset_index(drop=True)

        #delete orthogonal bbox
        self.pbboxes = self.pbboxes.loc[self.pbboxes['obj'] != obj_id,]
        self.pbboxes.reset_index(drop=True)

        #delete class
        df = self.annotation_classes
        df = df.loc[df['obj'] != obj_id,]
        self.annotation_classes = df.reset_index(drop=True)

        #delete convex hull
        self.convex_hulls.pop(str(obj_id))

        #reset active object (because it is deleted):
        self.reset_active_object()

        #set saved status to False
        self.currently_saved = False

        self.master.annotation_canvas.updateImage(from_scratch=True)

    def delete_point(self, point_id=None):

        #check inputs
        if point_id is None:
            point_id = self.point_id

        #delete point
        self.points = np.delete(self.points, point_id, axis=0)

        #update self.point_id if necessary
        if point_id >= len(self.points):
            self.point_id = len(self.points) - 1

        self.master.annotation_canvas.updateImage(from_scratch=False)

    def delete_mask(self, mask_id=None, mask_name=None):

        if not self.master.data_canvas.object_canvas.masks_visible:
            #if masks are not visible, no modifications to the masks may be done
            return

        #process arguments
        if mask_id is None and mask_name is None:
            raise ValueError("mask_id and mask_name may not be both None")
        elif mask_id is not None and mask_name is not None:
            raise ValueError("mask_id and mask_name may not be given both")
        elif mask_name is not None:
            #only mask_name is given
            #get mask_id
            mask_id = self.names_masks.loc[self.names_masks["name"]==mask_name, "obj"].iloc[0]

        #delete mask
        #remark that it's impossible to remove a mask under construction
        #since a mask under construction is automatically confirmed when
        #clicking in the object_canvas

        #delete name of mask
        self.names_masks = self.names_masks.loc[self.names_masks["obj"] != mask_id,]
        self.names_masks = self.names_masks.reset_index(drop=True)

        #delete points of object
        df = self.annotation_points_masks
        df = df.loc[df['obj'] != mask_id,]
        self.annotation_points_masks = df.reset_index(drop=True)

        #reset active object (because it is deleted):
        self.reset_active_mask()

        #set saved status to False
        self.currently_saved = False

        self.master.annotation_canvas.updateImage(from_scratch=True)

    def delete_mask_point(self, point_id=None):
        #check inputs
        if point_id is None:
            point_id = self.point_id

        #delete point
        self.points_mask = np.delete(self.points_mask, point_id, axis=0)

        #update self.point_id if necessary
        if point_id >= len(self.points_mask):
            self.point_id = len(self.points_mask) - 1

        self.master.annotation_canvas.updateImage(from_scratch=False)

    def rename_object(self, current_name, new_name):
        self.names.loc[self.names["name"] == current_name, "name"] = new_name

    def rename_mask(self, current_name, new_name):
        self.names_masks.loc[self.names_masks["name"] == current_name, "name"] = new_name















