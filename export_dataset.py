# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 12:22:44 2021

@author: Maarten
"""

#%% import packages
import os
import numpy as np
import cv2
import json
import pandas as pd
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox


#%%
class ExportDataset(tk.Toplevel):
    """
    Child window to export a dataset
    """
    def __init__(self, master):
        #initiate frame
        tk.Toplevel.__init__(self, master)
        self.master = master

        #set title of child window
        self.title("Export dataset")

        #declare list of possible dataset_types
        self.dataset_types = ["Classic bbox",
                              "Rotated bbox"]

        #format listbox

        #create listbox
        self.listbox = tk.Listbox(self, width=30, height=5)
        #height is expressed in number of lines

        #add items to listbox
        for i, dataset_type in enumerate(self.dataset_types):
            self.listbox.insert(i, dataset_type)

        #select first item in listbox
        self.listbox.select_set(0)

        #bind double click on class to self.select_class
        self.listbox.bind("<Double-1>", lambda event:self.select_dataset_type())
        self.listbox.bind("<Return>", lambda event: self.select_dataset_type())

        self.listbox.grid(row=0, column=0, padx=0, pady=0)
        self.listbox.focus_set()

        #format buttons
        self.btn_frame = tk.Frame(self, width=200, height=40)
        self.btn_frame.grid(row=1, column=0, padx=0, pady=0)

        self.btn_frame.selectBtn = tk.Button(self.btn_frame, text='Select',
                                            command=self.select_dataset_type)
        self.btn_frame.selectBtn.grid(row=0, column=0, padx=10, pady=10)

        #general settings for a child window
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)

    def select_dataset_type(self):
        """
        Select dataset type and export dataset
        """

        #get selected dataset_type
        self.dataset_type = self.listbox.curselection()[0]

        #Check if there are unsaved changes and save them if user request it
        if self.master.image.currently_saved is False:
            #there are currently unsaved changes in the annotations
            answer = tkmessagebox.askyesnocancel("Save modifications",
                    "do you want to save the annotation changes you made \nfor the current image?")
            if answer is True:
                self.master.image.save_annotations()
            elif answer is None:
                self.destroy()
            #nothing has to be done if answer is False

        if self.dataset_type==0:
            #Classic bbox
            self.export_dataset_bbox()
            self.destroy()

        else: #self.dataset_type==1
            #rotated bbox
            self.export_dataset_rbbox()
            self.destroy()

    def export_dataset_rbbox(self):
        """
        Export a dataset to train a YOLO-detector to detect rotated bounding
        boxes
        """

        #ask for dataset filepath
        dataset_path = tkfiledialog.asksaveasfilename()

        #create directory
        os.mkdir(dataset_path)
        os.chdir(dataset_path)

        #set size of exported images
        size_result = 1920

        #set number of (random chosen) angles that will be applied on each image
        n_angles = 10

        angles = np.linspace(-45,45, num=n_angles, endpoint=False)
        step = 90/n_angles

        #export images
        file_list = os.listdir(self.master.project.wdir)
        for file in file_list:
            #check if file is an image (.jpg or .png) and if there is an
            #annotation file (.json)
            if (len(file.split("."))==2) and\
                (file.split(".")[1] in ["jpg", "png"]) and\
                (file.split(".")[0] + ".json" in file_list):

                #get image
                image = cv2.imread(os.path.join(self.master.project.wdir, file))

                #read mask (if present)
                filename_masks = file.split(".")[0] + "_mask.json"
                if filename_masks in os.listdir(self.master.project.wdir):
                    json_file = open(os.path.join(self.master.project.wdir, file.split(".")[0] + "_mask.json"))
                    masks = json.load(json_file)
                    json_file.close()

                    #apply masks
                    for key in masks:
                        #extract edges of mask
                        points_dict = masks[key]["points"]
                        mask = np.empty(shape=(0,2))
                        for point_key in points_dict:
                            x = points_dict[point_key]['x']
                            y = points_dict[point_key]['y']
                            mask = np.append(mask,[[x, y]], axis=0)

                        #round coordinates and draw mask on image
                        mask = np.int64(mask).reshape((-1, 1, 2))

                        image= cv2.fillPoly(image,
                                            [mask],
                                            color=[0,0,0])

                #read annotations
                with open(os.path.join(self.master.project.wdir, file.split(".")[0] + ".json")) as f:
                    data = json.load(f)

                #write data in annotations to right dataframes
                classes = pd.DataFrame(data=None,
                                       columns=["obj", "class"])
                points = pd.DataFrame(data=None,
                                      columns=["obj", "x", "y"])
                obj_id = 0

                for key, dict_object in data["objects"].items():

                    #add class to classes
                    new_obj = pd.DataFrame(data=[[obj_id, dict_object["class"]]],
                                          columns=classes.columns)
                    if len(classes)==0:
                        classes = new_obj
                    else:
                        classes = pd.concat((classes, new_obj), axis=0).\
                            reset_index(drop=True)

                    #add points to points
                    points_dict = dict_object["points"]
                    points_list = []
                    for j in points_dict.keys():
                        x = points_dict[j]["x"]
                        y = points_dict[j]["y"]
                        points_list.append([x, y])
                    points_obj_df = pd.DataFrame(data=points_list,
                                      columns=["x", "y"])
                    points_obj_df["obj"] = obj_id
                    if len(points)==0:
                        points = points_obj_df
                    else:
                        points = pd.concat((points, points_obj_df), axis=0).\
                            reset_index(drop=True)

                    #increase self.obj_id with 1
                    obj_id += 1

                w = image.shape[1]
                h = image.shape[0]
                image_original = image

                """
                #stretch image along shortest axis to make it square
                w = image.shape[1]
                h = image.shape[0]
                scale_x = max(w, h) / w
                scale_y = max(w, h) / h

                image_original = cv2.resize(image,dsize=(max(w, h), max(w, h)))

                w = max(w, h)
                h = max(w, h)

                #adapt points to stretching of image
                points["x"] *= scale_x
                points["y"] *= scale_y
                """

                #export for each angle an image
                for i, theta in enumerate(angles):
                    #sample a random angle in interval [theta, theta + step]
                    theta = int(np.round(np.random.uniform(theta, theta + step, size=1)))

                    #convert theta to value in range [0, 360]
                    if theta >= 0:
                        theta = theta % 360
                    else: # theta < 0
                        a = -theta % 360
                        theta = 360-a

                    #convert theta to radians and calculate sin and cos
                    theta_radians = np.radians(theta)
                    s = np.sin(theta_radians)
                    c = np.cos(theta_radians)

                    #calculate new width and height of figure
                    if theta<=90:
                        w2 = w * c + h * s
                        h2 = w * s + h * c
                    elif theta<=180:
                        w2 = -w * c + h * s
                        h2 = w * s - h * c
                    elif theta<=270:
                        w2 = -w * c - h * s
                        h2 = -w * s - h * c
                    else:#theta<=360
                        w2 = w * c - h * s
                        h2 = -w * s + h * c

                    #rotate image along specified angle
                    w2 = int(w2)
                    h2 = int(h2)
                    dx = max(0,int((w2 - w)/2))
                    dy = max(0,int((h2 - h)/2))
                    M = np.float32([[1,0,dx],[0,1,dy]])
                    image = cv2.warpAffine(image_original,M, dsize=(w + 2*dx, h + 2*dy))

                    M = cv2.getRotationMatrix2D(((w - 1)/2+dx,(h - 1)/2+dy),theta,1)
                    #the -1 correction for w and h is essential to obtain the right rotation center

                    if dx==0:
                        dx=int((w - w2)/2)
                    else:
                        dx = 0
                    if dy==0:
                        dy=int((h2 - h)/2)
                    else:
                        dy = 0

                    image = cv2.warpAffine(image,M, dsize=(w2+dx, h2+dy))

                    M = np.float32([[1,0,-dx],[0,1,-dy]])
                    image = cv2.warpAffine(image,M, dsize=(w2, h2))

                    #rotate points along specified angle

                    #center points relative to size of image
                    coordinates = points[["x", "y"]].to_numpy()
                    coordinates[:,0] -= (w - 1)/2
                    coordinates[:,1] -= (h - 1)/2
                    #the -1 correction for w and h is essential to obtain the right rotation center

                    #rotate x and y coordinates around origin (which is center of image)
                    M = np.array([[c, s],
                                  [-s, c]])
                    M = M.transpose()
                    coordinates = np.matmul(coordinates, M)

                    #express x and y coordinates relative to new width of figure
                    coordinates[:,0] /= (w2 - 1)
                    coordinates[:,1] /= (h2 - 1)

                    #set center of axis system again to top left corner of image
                    coordinates += 0.5

                    #calculate bboxes
                    bboxes = np.zeros(shape=(len(classes),5))
                    for obj in classes["obj"]:
                        obj_points = coordinates[points["obj"]==obj,:]
                        x_min = np.min(obj_points[:,0])
                        x_max = np.max(obj_points[:,0])
                        y_min = np.min(obj_points[:,1])
                        y_max = np.max(obj_points[:,1])
                        w_box = x_max - x_min
                        h_box = y_max - y_min
                        x_c = x_min + w_box/2
                        y_c = y_min + h_box/2

                        bboxes[obj,:] = [classes.loc[obj,"class"],
                                         x_c, y_c, w_box, h_box]

                    #resize result to specified specified size
                    image = cv2.resize(image,dsize=(size_result, size_result))

                    #save image in jpg format
                    cv2.imwrite(file.split(".")[0] + "_" + str(i + 1).zfill(3) + ".jpg",\
                                image)

                    #save annotations in corresponding .txt file
                    np.savetxt(file.split(".")[0] + "_" + str(i + 1).zfill(3) + ".txt",
                               X=bboxes,
                               delimiter=" ",
                               fmt=['%.0f', '%.6f', '%.6f', '%.6f', '%.6f'])
                    """
                    %.0f = floating point number, no decimals
                    %.6f = floating point number, 6 decimals
                    """

        #set working directory back to working directory of images
        os.chdir(self.master.project.wdir)

    def export_dataset_bbox(self):
        """
        export dataset as classic bbox
        """

        #ask for dataset filepath
        dataset_path = tkfiledialog.asksaveasfilename()

        #create directory
        os.mkdir(dataset_path)
        os.chdir(dataset_path)

        file_list = os.listdir(self.master.project.wdir)
        for file in file_list:
            #check if file is an image (.jpg or .png) and if there is an
            #annotation file (.json)
            if (len(file.split("."))==2) and\
                (file.split(".")[1] in ["jpg", "png"]) and\
                (file.split(".")[0] + ".json" in file_list):

                #get image
                image = cv2.imread(os.path.join(self.master.project.wdir, file))

                #read mask (if present)
                filename_masks = file.split(".")[0] + "_mask.json"
                if filename_masks in os.listdir(self.master.project.wdir):
                    json_file = open(os.path.join(self.master.project.wdir, file.split(".")[0] + "_mask.json"))
                    masks = json.load(json_file)
                    json_file.close()

                    #apply masks
                    for key in masks:
                        #extract edges of mask
                        points_dict = masks[key]["points"]
                        mask = np.empty(shape=(0,2))
                        for point_key in points_dict:
                            x = points_dict[point_key]['x']
                            y = points_dict[point_key]['y']
                            mask = np.append(mask,[[x, y]], axis=0)

                        #round coordinates and draw mask on image
                        mask = np.int64(mask).reshape((-1, 1, 2))

                        image= cv2.fillPoly(image,
                                            [mask],
                                            color=[0,0,0])

                #read annotations
                with open(os.path.join(self.master.project.wdir, file.split(".")[0] + ".json")) as f:
                    data = json.load(f)

                #write data in annotations to right dataframes
                classes = pd.DataFrame(data=None,
                                       columns=["obj", "class"])
                points = pd.DataFrame(data=None,
                                      columns=["obj", "x", "y"])
                obj_id = 0

                for key, dict_object in data["objects"].items():

                    #add class to classes
                    new_obj = pd.DataFrame(data=[[obj_id, dict_object["class"]]],
                                          columns=classes.columns)
                    if len(classes) == 0:
                        classes = new_obj
                    else:
                        classes = pd.concat((classes, new_obj), axis=0).\
                            reset_index(drop=True)

                    #add points to points
                    points_dict = dict_object["points"]
                    points_list = []
                    for j in points_dict.keys():
                        x = points_dict[j]["x"]
                        y = points_dict[j]["y"]
                        points_list.append([x, y])
                    points_obj_df = pd.DataFrame(data=points_list,
                                      columns=["x", "y"])
                    points_obj_df["obj"] = obj_id
                    if len(points)==0:
                        points = points_obj_df
                    else:
                        points = pd.concat((points, points_obj_df), axis=0).\
                            reset_index(drop=True)

                    #increase self.obj_id with 1
                    obj_id += 1

                #extract x and y coordinates out of points
                coordinates = points[["x", "y"]].to_numpy()

                #normalize coordinates according to the width and height of the image
                coordinates[:,0] = coordinates[:,0] / image.shape[1]
                coordinates[:,1] = coordinates[:,1] / image.shape[0]

                #calculate bboxes
                bboxes = np.zeros(shape=(len(classes),5))
                for obj in classes["obj"]:
                    obj_points = coordinates[points["obj"]==obj,:]
                    x_min = np.min(obj_points[:,0])
                    x_max = np.max(obj_points[:,0])
                    y_min = np.min(obj_points[:,1])
                    y_max = np.max(obj_points[:,1])
                    w_box = x_max - x_min
                    h_box = y_max - y_min
                    x_c = x_min + w_box/2
                    y_c = y_min + h_box/2

                    bboxes[obj,:] = [classes.loc[obj,"class"],
                                     x_c, y_c, w_box, h_box]

                #save image in jpg format
                cv2.imwrite(file.split(".")[0] + ".jpg",\
                            image)

                #save annotations in corresponding .txt file
                np.savetxt(file.split(".")[0] + ".txt",
                           X=bboxes,
                           delimiter=" ",
                           fmt=['%.0f', '%.6f', '%.6f', '%.6f', '%.6f'])
                """
                %.0f = floating point number, no decimals
                %.6f = floating point number, 6 decimals
                """

        #set working directory back to working directory of images
        os.chdir(self.master.project.wdir)