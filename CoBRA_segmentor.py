# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 11:00:22 2021

@author: Maarten
"""
#%% Load packages
import os
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import numpy as np
import json
import shutil
from tkinter import messagebox

from export_dataset import ExportDataset
from annotation_canvas import AnnotationCanvas
from data_canvas import DataCanvas
from image_object import ImageObject
from project import Project
from color_manager import ColorManager
from category_manager import CategoryManager
from linewidth_dialog import LinewidthDialog

#%% Main application

class Application(tk.Frame):
    """
    code for master window of application
    """
    def __init__(self, master=None, program_dir=None):
        #initiate frame
        tk.Frame.__init__(self, master)
        self.pack()
        self.master = master

        #initiate main panel
        self.main_panel = tk.PanedWindow(bd=0,
                                         bg="black",
                                         orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH,
                             expand=True)

        #set title
        self.master.title("CoBRA segmentor")

        #make sure the application fills the whole window
        self.master.state('zoomed')
        root.update()

        #set useable width and height (expressed in pixels)
        uw = root.winfo_width() #useable_width
        uh = root.winfo_height() #useable_height
        self.uw = uw
        self.uh = uh

        #declare project
        self.project = Project(master=self)

        #declare ImageObject containing all annotation information
        self.image = ImageObject(master=self)

        #canvas to show image
        self.annotation_canvas = AnnotationCanvas(master=self,
                                                  bd=0,
                                                  width=self.uw * 0.7,
                                                  height=self.uh)

        #canvas to show objects
        self.data_canvas = DataCanvas(master=self,
                                      bg='black',
                                      bd=0,
                                      orient=tk.VERTICAL,
                                      width=self.uw * 0.3,
                                      height=self.uh)

        #add annotation canvas
        self.main_panel.add(self.annotation_canvas)

        #add skeleton canvas
        self.main_panel.add(self.data_canvas)

        root.update()

        #set path to software files
        self.program_dir = program_dir

        #Declare attributes containing configuration/status information


        #format application

        #format window/canvas to show image
        self.master.update()

        #configure menu
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar, tearoff=False)
        self.file_menu.add_command(label="Open project",
                                   command=lambda : self.open_project())
        self.file_menu.add_command(label="New project",
                                  command=lambda : self.newproject())
        self.file_menu.add_command(label="Modify categories",
                                  command=lambda : CategoryManager(master=self))
        self.file_menu.add_command(label="Modify colors",
                                  command=lambda : ColorManager(master=self))
        self.file_menu.add_command(label="Open image (Ctrl+O)",
                                  command=self.open_image)
        self.file_menu.add_command(label="Save annotations (Ctrl+S)",
                                  command=self.image.save)
        self.file_menu.add_command(label="Return (Ctrl+Z)",
                                  command=self.image.returnbbox)
        self.file_menu.add_command(label="Previous image (F7)",
                                  command=lambda : self.switch_image(direction=-1))
        self.file_menu.add_command(label="Next image (F8)",
                                  command=lambda : self.switch_image(direction=1))
        self.file_menu.add_command(label='Import Images (Ctrl+I)',
                                   command=lambda: self.import_image())
        self.file_menu.add_command(label="Export dataset (F5)",
                                  command=self.export_dataset)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        self.master.bind("<Control-o>", lambda event: self.open_image())
        self.master.bind("<Control-s>", lambda event: self.image.save())
        self.master.bind("<Control-z>", lambda event:self.image.returnbbox())
        self.master.bind("<F7>", lambda event: self.switch_image(direction=-1))
        self.master.bind("<F8>", lambda event: self.switch_image(direction=1))
        self.master.bind("<F5>", lambda event: self.export_dataset())

        self.file_menu.entryconfig("Modify categories", state="disabled")
        self.file_menu.entryconfig("Modify colors", state="disabled")
        self.file_menu.entryconfig("Save annotations (Ctrl+S)", state="disabled")
        self.file_menu.entryconfig("Return (Ctrl+Z)", state="disabled")
        self.file_menu.entryconfig("Previous image (F7)", state="disabled")
        self.file_menu.entryconfig("Next image (F8)", state="disabled")
        self.file_menu.entryconfig("Import Images (Ctrl+I)", state="disabled")
        self.file_menu.entryconfig("Export dataset (F5)", state="disabled")

        self.mode_menu = tk.Menu(self.menubar, tearoff=False)
        self.mode_menu.add_command(label="Classic bbox",
                                  command=lambda:self.set_mode(0))
        self.mode_menu.add_command(label="Convex hull",
                                  command=lambda:self.set_mode(1))
        self.mode_menu.add_command(label="Convex hull + rotated bbox",
                                  command=lambda:self.set_mode(2))
        self.mode_menu.add_command(label="Segmentation",
                                  command=lambda:self.set_mode(3))
        self.mode_menu.add_command(label="Segmentation + rotated bbox",
                                  command=lambda:self.set_mode(4))
        self.mode_menu.add_command(label="Segmentation + convex hull + rotated bbox",
                                  command=lambda:self.set_mode(5))
        self.menubar.add_cascade(label="Mode", menu=self.mode_menu)


        self.settings_menu = tk.Menu(self.menubar, tearoff=False)
        self.settings_menu.add_command(label="Linewidth",
                                       command=lambda:self.set_linewidth())
        self.menubar.add_cascade(label="Settings", menu=self.settings_menu)

        self.help_menu = tk.Menu(self.menubar, tearoff=False)
        self.help_menu.add_command(label="Help (F1)", command=self.launch_help)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

        self.master.bind("<F1>", lambda event: self.launch_help())

        self.master.bind("<Configure>", lambda event:self.annotation_canvas.resize_app())


        self.master.bind("<Key-Return>",
                  lambda event: self.image.newbbox())

        #bind return key to invoke currently active button
        self.master.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())

        #dimension self.annotation_canvas properly
        self.annotation_canvas.resize_app()


        #maximum distance of edge/point to reactivate it
        self.dist_max = 3


    def open_image(self, file=None):
        """
        Open an image
        """
        if self.project.wdir is not None:
            #check if a project is loaded

            if file is None:
                #ask for a filepath
                filepath = tkfiledialog.askopenfilename()
            else:
                filepath = file

            if filepath!="":
                if os.path.isabs(filepath):
                    #file is an absolute file directory

                    #check if image is in project directory, if this is not the
                    #case, import image
                    if os.path.split(filepath)[0] != self.project.wdir:
                        self.import_image(filepath)

                #load the image (and annotations)
                self.image.load_image(filepath)

    def launch_help(self):
        """
        launch the help file
        """
        os.startfile(os.path.join(self.program_dir, "./help/help.pdf"))

    def reset_parameters(self):

        self.point_active = False
        self.annotation_canvas_image = self.annotation_canvas.create_image(0,0, anchor='nw')

    def export_dataset(self):
        """
        Export the dataset
        """
        if self.project.wdir is not None:
            ExportDataset(master=self)

    def set_mode(self, mode):
        """
        Set display parameters of application
        """
        self.annotation_canvas.set_mode(mode)

    def switch_image(self, direction=1):
        """
        Load the next/previous image in the working directory
        """

        if self.project.wdir is not None and self.image.image_name is not None:
            #Check if there is an image loaded

            #list all files within working directory
            files = np.array(os.listdir(self.project.wdir))

            #get index of current image
            file_number = np.argmax(files == self.image.image_name)

            #look for next/previous image
            keep_looking = True
            while keep_looking is True:
                if file_number==len(files) - 1:
                    if direction==1:
                        file_number = 0
                    else:
                        file_number += direction
                elif file_number==0:
                    if direction==-1:
                        file_number = len(files) - 1
                    else:
                        file_number += direction
                else:
                    file_number += direction

                image_name = files[file_number]

                #check if file extension is correct
                if (len(image_name.split("."))>1) and\
                    (image_name.split(".")[1] in ['jpg', 'png']):
                    keep_looking = False
                    #remark: if current image is the only image in the
                    #folder, the while loop will be ended once we
                    #re-encounter the name of the current image

            #load image
            self.image.load_image(image_name)

    def newproject(self):
        #create a new project
        directory = tkfiledialog.asksaveasfilename()

        os.mkdir(directory)
        os.chdir(directory)

        self.close_project()

        CategoryManager(self)

        self.configure_menus()

        #save project configurations
        self.project.save()

    def open_project(self):
        #open a project folder
        directory = tkfiledialog.askdirectory()

        self.project.load_project(directory)

        if self.project.valid is False:
            #project wasn't configured correctly or project wasn't configured
            #at all
            return

        self.configure_menus()

        #if an image is present in the project directory, load the first one
        files = os.listdir()

        file_opened = False
        i = -1

        while not file_opened:
            i += 1
            if i == len(files):
                file_opened = True
            else:
                file = files[i]
                if file.split(".")[-1] in ["jpg", "png"]:
                    self.image.load_image(file)
                    file_opened = True

    def import_image(self, file=None):

        #process arguments
        if file is None:
            files = tkfiledialog.askopenfilenames()
        else:
            files = (file,)

        current_files = os.listdir(self.project.wdir)

        for file in files:
            if (len(file.split(".")) == 2) and\
                (file.split(".")[-1] in ["jpg", "png", "jpeg"]):
                #valid image
                src = file
                dst = os.path.join(self.project.wdir, os.path.split(file)[1])

                if os.path.exists(dst):
                    #filename is not unique

                    core_name = file.split("/")[-1]
                    core_name = core_name.split(".")[0]
                    extension = file.split('.')[1]

                    if len(core_name) < 2:
                        #core name is too short to be already an indexed name
                        core_name += "_1"

                    else:
                        #core name is sufficiently long
                        index = 0
                        unique_name = False
                        while not unique_name:
                            index += 1
                            new_name = core_name + "_" + str(index) + "." + extension
                            if new_name not in current_files:
                                unique_name = True
                                core_name += "_" + str(index)

                    dst = self.project.wdir + "/" + core_name + "." + extension
                    shutil.copyfile(src, dst)

                else:
                    #filename is unique in project directory

                    #copy image
                    shutil.copyfile(src, dst)

        #open last imported image
        self.open_image(file=dst)


    def update_application(self):

        self.data_canvas.class_canvas.update()
        self.annotation_canvas.updateImage(from_scratch=True)

    def set_linewidth(self):
        LinewidthDialog(self)

    def close_project(self):
        #declare empty project
        self.project.reset()

        #declare empty ImageObject containing all annotation information
        self.image.reset_full()

        #update application
        self.update_application()

    def configure_menus(self):
        """
        Enable/disable entries within the menus
        """

        if self.project.wdir is None:
            self.file_menu.entryconfig("Modify categories", state="disabled")
            self.file_menu.entryconfig("Modify colors", state="disabled")
            self.file_menu.entryconfig("Open image (Ctrl+O)", state="disabled")
            self.file_menu.entryconfig("Save annotations (Ctrl+S)", state="disabled")
            self.file_menu.entryconfig("Return (Ctrl+Z)", state="disabled")
            self.file_menu.entryconfig("Previous image (F7)", state="disabled")
            self.file_menu.entryconfig("Next image (F8)", state="disabled")
            self.file_menu.entryconfig("Import Images (Ctrl+I)", state="disabled")
            self.file_menu.entryconfig("Export dataset (F5)", state="disabled")

        else: #self.project.wdir is not None:
            self.file_menu.entryconfig("Modify categories", state="normal")
            self.file_menu.entryconfig("Modify colors", state="normal")
            self.file_menu.entryconfig("Open image (Ctrl+O)", state="normal")
            self.file_menu.entryconfig("Save annotations (Ctrl+S)", state="normal")
            self.file_menu.entryconfig("Return (Ctrl+Z)", state="normal")
            self.file_menu.entryconfig("Previous image (F7)", state="normal")
            self.file_menu.entryconfig("Next image (F8)", state="normal")
            self.file_menu.entryconfig("Import Images (Ctrl+I)", state="normal")
            self.file_menu.entryconfig("Export dataset (F5)", state="normal")

#%% Start mainloop
root = tk.Tk()

#set application icon
if os.path.exists("icon/CoBRA_segmentor_icon.ico"):
    #this case will be executed when the application is run from the .py file
    root.iconbitmap("icon/CoBRA_segmentor_icon.ico")
elif os.path.exists("_internal/icon/CoBRA_segmentor_icon.ico"):
    #this case will be executed when the application is run from a .exe file
    #generated with pyinstaller
    root.iconbitmap("_internal/icon/CoBRA_segmentor_icon.ico")

soft_dir = os.getcwd()
app = Application(master=root, program_dir=soft_dir)
app.mainloop()
