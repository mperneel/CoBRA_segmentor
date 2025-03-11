# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 14:17:37 2021

@author: Maarten
"""
#%% packages
import pandas as pd
import os
import json
import tkinter as tk
from tkinter import messagebox

from category_manager import CategoryManager

#%%main code

class Project():

    def __init__(self, master):
        """
        Class containing all information about the annotation project
        """
        self.master = master

        #working directory
        self.wdir = None

        #possible classes
        self.project_dict = {}

        #initiate attributes
        self.obj_classes = pd.DataFrame(data=None,
                                        columns=['id', 'name'])

        self.colors = []
        self.valid = True #boolean indicating if the project contains a
        #sufficient number of categories

    def configure_from_dict(self):
        """
        configure all frames and lists based on project dictionarry
        """

        #attribute to store colors
        self.colors = []

        #initiate lists to store class ids (integers) and names of classes
        id_ints = []
        names = []

        for key, class_dict in self.project_dict.items():
            id_ints.append(int(key))
            names.append(class_dict['name'])
            self.colors.append(class_dict['color'])

        #store class ids and class names in a dataframe attribute
        obj_classes_dict = {"id": id_ints,
                            "name": names}
        self.obj_classes = pd.DataFrame(obj_classes_dict)

        #update application
        self.master.update_application()

    def configure_from_frames(self):
        """
        configure project dictionary based on frames and lists
        """

        project_dict = {}

        for i, name in enumerate(self.obj_classes['name']):
            project_dict[str(i)] = {'name': name,
                                    'color': self.colors[i]}

        self.project_dict = project_dict
        self.master.update_application()

    def save(self):
        if not os.path.exists("project"):
            os.mkdir("project")

        with open("project/project.json", "w") as f:
            json.dump(self.project_dict, f,
                      indent=4)

        #update application
        self.master.update_application()

    def load_project(self, directory):
        """
        load the 'project.json' file if available
        """
        #change working directory
        self.wdir = directory
        os.chdir(self.wdir)

        if "project" in os.listdir() and\
            "project.json" in os.listdir("project"):
            with open('project//project.json') as f:
                self.project_dict = json.load(f)
            self.configure_from_dict()

        else:
            #no project.json file present in directory -> no valid project
            #ask if folder has to be configured to a project

            boolean_new_project = tk.messagebox.askokcancel(
                title="Invalid project folder",
                message="The selected folder is an invalid:\n" +
                "project.json file is missing \n\n"+
                "Do you want to configure the project?")

            if boolean_new_project:
                #a new project.json file should be created within this directory

                self.valid = False
                while self.valid is False:
                    CategoryManager(master=self.master)

                    #check if sufficient classes were created
                    n_classes_created = len(self.project_dict)
                    n_classes_needed = 0

                    #loop over all annotation files
                    files = os.listdir()
                    for file in files:
                        if (file.split(".")[-1] in ["png", "jpg"]) and\
                            (file.split(".")[0] + ".json" in files):
                            #file is an image with an according annotation json file

                            #read json file
                            file_object = open(file.split(".")[0] + ".json")
                            annotations = json.load(file_object)
                            file_object.close()

                            for key in annotations:
                                class_id = annotations[key]["category"]
                                if class_id > n_classes_needed:
                                    n_classes_needed = class_id

                    n_classes_needed += 1

                    if n_classes_created < n_classes_needed:
                        messagebox.showerror(
                              title="Insufficient number of categories",
                              message="At least " + str(n_classes_needed) +\
                                " categories were expected, but only " +\
                                str(n_classes_created) + " categories were added")
                    else:
                       self.valid = True
            else:
                self.valid = False

    def reset(self):
        """
        reset all parameters
        """

        #working directory
        self.wdir = None

        #possible classes
        self.project_dict = {}

        #initiate attributes
        self.obj_classes = pd.DataFrame(data=None,
                                        columns=['id', 'name'])

        self.colors = []







