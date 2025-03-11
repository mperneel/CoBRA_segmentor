# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:15:19 2021

@author: Maarten
"""

#%% import packages
import tkinter as tk

#%%

class ClassCanvas(tk.Canvas):
    
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        
        
        #assign master
        self.master = master
        
        #assign image object
        self.image = self.master.image
        
        self.classes = self.master.master.project.obj_classes
        
        self.class_var = tk.IntVar()
        self.class_var.set(0)
        
        self.radiobuttons = []
        
        for i in range(len(self.classes['id'])):
            class_id = self.classes.loc[i, 'id']
            class_name = self.classes.loc[i, 'name']
            button = tk.Radiobutton(self,
                                     text=class_name,
                                     variable=self.class_var,
                                     value=class_id,
                                     command=self.change_class)
            self.radiobuttons.append(button)
            button.pack(anchor='w')
            
            
    def change_class(self):
        self.image.current_object_confirmed = False
        self.image.class_last = self.class_var.get()
        
    def update(self):
        """
        Update class canvas
        """
        self.classes = self.master.master.project.obj_classes
        
        #remove all radiobuttons currently present
        for radiobutton in self.radiobuttons:
            radiobutton.pack_forget()
            
        #reset self.radiobuttons
        self.radiobuttons = []
        
        #create new radiobuttons
        for i in range(len(self.classes['id'])):
            class_id = self.classes.loc[i, 'id']
            class_name = self.classes.loc[i, 'name']
            button = tk.Radiobutton(self,
                                     text=class_name,
                                     variable=self.class_var,
                                     value=class_id,
                                     command=self.change_class)
            self.radiobuttons.append(button)
            button.pack(anchor='w')
        
        
        
        
        
        
        
        
        
        