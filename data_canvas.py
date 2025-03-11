# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:13:51 2021

@author: Maarten
"""

#%% import packages

#%% import packages
import tkinter as tk

from class_canvas import ClassCanvas
from object_canvas import ObjectCanvas

#%%

class DataCanvas(tk.PanedWindow):
    
    def __init__(self, master, **kwargs):
        super().__init__(**kwargs)
        
        #assign master
        self.master = master
        
        #assign image object
        self.image = self.master.image
        
        #initiate main panel
        self.master.master.update()
        self.uh = self.master.master.winfo_height()   
        
        self.class_canvas = ClassCanvas(self,
                                        bd=5)
        
        self.object_canvas = ObjectCanvas(self)
        
        self.add(self.class_canvas)
        self.add(self.object_canvas)
        
        self.class_canvas.configure(height=self.uh*0.2)
        
