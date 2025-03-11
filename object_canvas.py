# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 13:14:27 2021

@author: Maarten
"""
#%% import packages
import tkinter as tk
from tkinter import ttk

from rename_object import RenameObject

#%%

class ObjectCanvas(ttk.Notebook):

    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)

        #assign master
        self.master = master

        #assign image object
        self.image = self.master.master.image

        self.master.master.master.update_idletasks()

        # tab with all objects
        self.objects = tk.Frame(master=self)

        #create listbox and scrollbar
        self.list_objects = tk.Listbox(master=self.objects)
        self.scrollbar = tk.Scrollbar(self.objects,
                                      orient="vertical",
                                      width=20)

        #configure scrollbar
        self.scrollbar.config(command=self.list_objects.yview)
        self.list_objects.config(yscrollcommand=self.scrollbar.set)

        #bind events to self.list_objects
        self.list_objects.bind("<<ListboxSelect>>",
                               lambda event: self.activate_object())
        self.list_objects.bind("<Control-Delete>",
                               lambda event: self.delete_object())
        self.list_objects.bind("<Delete>",
                               lambda event : self.delete_point())
        self.list_objects.bind("<Double-1>",
                               lambda event: self.rename_object())
        #<Double-1> = double click of left mouse button

        #create button_frame
        self.object_buttons_frm = tk.Frame(master=self.objects)
        self.btn_draw_new_object = tk.Button(master=self.object_buttons_frm,
                                             text="draw new",
                                             command=self.draw_new_object)
        self.btn_delete_object = tk.Button(master=self.object_buttons_frm,
                                           text='delete',
                                           command=self.delete_object)


        #tab with all mask objects
        self.mask_objects = tk.Frame(master=self)

        #create listbox and scrollbar
        self.list_masks = tk.Listbox(master=self.mask_objects)
        self.scrollbar_masks = tk.Scrollbar(self.mask_objects,
                                      orient="vertical",
                                      width=20)

        #configure scrollbar
        self.scrollbar_masks.config(command=self.list_masks.yview)
        self.list_masks.config(yscrollcommand=self.scrollbar_masks.set)

        #bind events to self.list_objects

        self.list_masks.bind("<<ListboxSelect>>",
                               lambda event: self.activate_mask())
        self.list_masks.bind("<Control-Delete>",
                              lambda event: self.delete_mask())
        self.list_masks.bind("<Delete>",
                             lambda event: self.delete_mask_point())
        self.list_masks.bind("<Double-1>",
                               lambda event: self.rename_mask())
        #<Double-1> = double click of left mouse button

        #create button_frame
        self.masks_buttons_frm = tk.Frame(master=self.mask_objects)
        self.btn_draw_new_mask = tk.Button(master=self.masks_buttons_frm,
                                             text="draw new",
                                             command=self.draw_new_mask)
        self.btn_hide_show_masks = tk.Button(master=self.masks_buttons_frm,
                                             text="hide all",
                                             command=self.hide_show_masks)
        self.btn_delete_mask = tk.Button(master=self.masks_buttons_frm,
                                           text='delete',
                                           command=self.delete_mask)

        #position all elements

        #add tabs to notebook
        self.add(self.objects, text="Objects")
        self.add(self.mask_objects, text='masks')

        #format self.objects
        self.btn_draw_new_object.grid(row=0,
                                      column=0,
                                      sticky='news')
        self.btn_delete_object.grid(row=0,
                                    column=1,
                                    sticky='news')
        self.object_buttons_frm.columnconfigure(0, weight=1)
        self.object_buttons_frm.columnconfigure(1, weight=1)


        self.object_buttons_frm.pack(side='bottom',
                               fill="x")
        self.list_objects.pack(side="left",
                               fill=tk.BOTH,
                               expand=True)
        self.scrollbar.pack(side="left",
                            fill="y")

        #format self.mask_objects
        self.btn_draw_new_mask.grid(row=0,
                                    column=0,
                                    sticky='news')
        self.btn_hide_show_masks.grid(row=0,
                                      column=1,
                                      sticky='news')
        self.btn_delete_mask.grid(row=0,
                                  column=2,
                                  sticky='news')
        self.masks_buttons_frm.columnconfigure(0, weight=1)
        self.masks_buttons_frm.columnconfigure(1, weight=1)
        self.masks_buttons_frm.columnconfigure(2, weight=1)

        self.masks_buttons_frm.pack(side='bottom',
                               fill="x")
        self.list_masks.pack(side="left",
                               fill=tk.BOTH,
                               expand=True)
        self.scrollbar_masks.pack(side="left",
                            fill="y")

        #bind method to tab change
        self.bind('<<NotebookTabChanged>>',
                  lambda event: self.check_mode())


        #set attributes containing information about the application state
        self.active_object_index = None
        #index (within listbox) of currently active object
        self.active_mask_index = None
        #index (within listbox) of currently active mask
        self.mode = 0 #0 = object mode; 1 = mask mode
        self.masks_visible = True

    def reset(self):
        #delete all current objects
        self.list_objects.delete(0, tk.END)

    def add_object(self, obj_name):
        self.list_objects.insert(tk.END, obj_name)

    def load_objects(self):
        #delete all current objects
        self.list_objects.delete(0, tk.END)

        #load new objects
        names = self.image.names
        for i in names.index:
            self.list_objects.insert(tk.END, names.loc[i,"name"])

    def delete_object(self):
        if len(self.list_objects.curselection()) == 0:
            #if no objects are selected (or declared), no object may be deleted
            return

        obj_name=self.list_objects.get(self.list_objects.curselection()[0])
        self.list_objects.delete(self.list_objects.curselection()[0])
        self.image.delete_object(obj_name=obj_name)

    def delete_point(self):
        if len(self.list_objects.curselection()) == 0:
            #if no objects are selected (or declared), no point may be deleted
            return

        #delete current point
        self.image.delete_point()

    def activate_object(self, list_index=None):
        #change active object
        if self.mode == 1:
            #this method should do nothing when in mask mode
            return

        if list_index is None:
            current_selection = self.list_objects.curselection()
            if len(current_selection) > 0:
                self.active_object_index = current_selection[0]
        else:
            self.active_object_index = list_index

        if self.active_object_index is not None:
            obj_name = self.list_objects.get(self.active_object_index)
            self.image.update_active_object(obj_name=obj_name)

    def rename_object(self):
        #get current name of object
        self.active_object_index = self.list_objects.curselection()[0]
        obj_current_name=self.list_objects.get(self.active_object_index)

        #get new name of object
        RenameObject(self, obj_current_name)

        #activate renamed object
        self.activate_object(list_index=self.active_object_index)

    def draw_new_object(self):
        self.active_object_index = None
        self.list_objects.select_clear(0, tk.END)
        self.image.newbbox()

    def load_masks(self):
        #delete all current objects
        self.list_masks.delete(0, tk.END)

        #load new masks
        names = self.image.names_masks
        for i in names.index:
            self.list_masks.insert(tk.END, names.loc[i,"name"])

    def activate_mask(self, list_index=None):
        if self.mode == 0:
            #this method should do nothing when in object mode
            return

        if not self.masks_visible:
            #if the masks are not visible, no mask may be activated
            return

        #change active mask
        if list_index is None:
            current_selection = self.list_masks.curselection()
            if len(current_selection) > 0:
                self.active_mask_index = current_selection[0]
        else:
            self.active_mask_index = list_index

        if self.active_mask_index is not None:
            mask_name = self.list_masks.get(self.active_mask_index)
            self.image.update_active_mask(mask_name=mask_name)

    def delete_mask(self):

        if not self.masks_visible:
            #if the masks are not visible, no mask may be deleted
            return

        if len(self.list_masks.curselection()) == 0:
            #if no masks are selected (or declared), no mask can be deleted
            return

        mask_index = self.list_masks.curselection()[0]
        mask_name=self.list_masks.get(mask_index)
        self.list_masks.delete(mask_index)
        self.image.delete_mask(mask_name=mask_name)

    def delete_mask_point(self):
        if not self.masks_visible:
            #if the masks are not visible, no mask points may be deleted
            return

        if len(self.list_masks.curselection()) == 0:
            #if no masks are selected (or declared), no mask point can be deleted
            return

        #delete currently active point
        self.image.delete_mask_point()

    def rename_mask(self):

        if not self.masks_visible:
            #if the masks are not visible, no mask may be renamed
            return

        #get current name of mask
        self.active_mask_index = self.list_masks.curselection()[0]
        mask_current_name=self.list_masks.get(self.active_mask_index)

        #get new name of mask
        RenameObject(self, mask_current_name)

        #activate renamed mask
        self.activate_mask(list_index=self.active_mask_index)

    def draw_new_mask(self):

        if not self.masks_visible:
            #if the masks are not visible, no new mask may be drawn
            return

        self.active_mask_index = None
        self.image.mask_mode = True
        self.image.newbbox()

    def hide_show_masks(self):
        self.master.master.annotation_canvas.show_mask =\
            not self.master.master.annotation_canvas.show_mask

        if self.master.master.annotation_canvas.show_mask:
            self.masks_visible = True
            self.btn_hide_show_masks.configure(text="hide all")
            #re-activate buttons and listboxes
            self.list_masks.configure(state = tk.NORMAL)
            self.btn_draw_new_mask.configure(state = tk.ACTIVE)
            self.btn_delete_mask.configure(state = tk.ACTIVE)
        else:
            self.masks_visible = False
            self.btn_hide_show_masks.configure(text="show all")
            #disable buttons and listboxes so no wrong things can happen
            self.list_masks.configure(state = tk.DISABLED)
            self.btn_draw_new_mask.configure(state = tk.DISABLED)
            self.btn_delete_mask.configure(state = tk.DISABLED)

        self.master.master.annotation_canvas.updateImage()

    def add_mask(self, obj_name):
        self.list_masks.insert(tk.END, obj_name)

    def check_mode(self):
        self.mode = self.index(self.select())

        self.image.newbbox()

        if self.mode == 0 :
            #mode: making annotations
            self.image.mask_mode = False

            #enabling radio buttons in class_canvas
            self.master.class_canvas.class_var.set(self.image.class_last)
            for radio_button in self.master.class_canvas.radiobuttons:
                radio_button.configure(state = tk.ACTIVE)

        else:
            #mode: creating masks
            self.image.mask_mode = True

            #disabling radio buttons in class_canvas
            self.master.class_canvas.class_var.set(None)
            for radio_button in self.master.class_canvas.radiobuttons:
                radio_button.configure(state = tk.DISABLED)









