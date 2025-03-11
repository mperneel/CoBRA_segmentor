# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 22:14:32 2021

@author: Maarten
"""

#%% packages
import tkinter as tk
from tkinter import ttk

#%% functions

def rgb2hex(rgb):
    return '#%02x%02x%02x' % rgb

#%% main code
class ColorManager(tk.Toplevel):
    """
    Child window to modify colors of categories
    """
    def __init__(self, master):
        #initiate frame
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.project = master.project
        
        self.title("Colors")
        
        #labels
        lab_cat = tk.Label(self, text="category:")
        lab_R = tk.Label(self, text='R:')
        lab_G = tk.Label(self, text='G:')
        lab_B = tk.Label(self, text='B:')
        
        #combobox for category selection
        self.cat = tk.StringVar()
        self.combobox_cat = ttk.Combobox(self,
                                         textvar=self.cat)
        self.combobox_cat['values'] = self.project.obj_classes['name'].to_list()
        
        self.cat.trace("w",
                        lambda name, index, mode : self.load_cat())  
        
        self.cat_index = 0
        
        #entryfields
        self.var_R = tk.StringVar()
        self.var_G = tk.StringVar()
        self.var_B = tk.StringVar()
        
        self.entry_R = tk.Entry(self,
                                width=3,
                                textvar=self.var_R)
        self.entry_G = tk.Entry(self,
                                width=3,
                                textvar=self.var_G)
        self.entry_B = tk.Entry(self,
                                width=3,
                                textvar = self.var_B)
        
        self.entry_R.bind('<FocusOut>', lambda event, var=self.var_R : self.check_RGB_entry(var))
        self.entry_G.bind('<FocusOut>', lambda event, var=self.var_G : self.check_RGB_entry(var))
        self.entry_B.bind('<FocusOut>', lambda event, var=self.var_B : self.check_RGB_entry(var))
        
        #frame for color example
        self.frm_color = tk.Frame(self,
                                  bg='red',
                                  width=45,
                                  height=45)
        
        #lay out all elements        
        lab_cat.grid(row=0, column=0, sticky="e")
        lab_R.grid(row=1, column=0, sticky="e")
        lab_G.grid(row=2, column=0, sticky="e")
        lab_B.grid(row=3, column=0, sticky="e")
        
        self.combobox_cat.grid(row=0, column=1, columnspan=2, sticky='we')
        
        self.entry_R.grid(row=1, column=1)
        self.entry_G.grid(row=2, column=1)
        self.entry_B.grid(row=3, column=1)
        
        self.frm_color.grid(row=1, column=2, rowspan=3)
        
        self.columnconfigure(2, weight=1)
        
        #load first_category and set focus on combobox
        self.combobox_cat.set(self.combobox_cat['values'][0])
        self.load_cat(cat_index=0)    
        self.combobox_cat.focus()
        self.combobox_cat.select_range(0, tk.END)

        #general settings for a child window
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)
        
    def check_RGB_entry(self, var):
        value = var.get()
        
        new_value = ""
        for character in value:
            if character.isnumeric():
                new_value += character                
        value = new_value
        
        if value == '':
            value='0'
            
        value = int(value)
        value = max(0,min(255, value))
        
        var.set(str(value))
        
        self.save_color()
        self.update_color_frame()
    
    def load_cat(self, cat_index=None):
        #preprocess arguments
        if cat_index is None:
            cat = self.combobox_cat.get()
            if cat == '':
                return
            else:
                cat_index = self.project.obj_classes.loc[self.project.obj_classes['name'] == cat, 'id'].iloc[0]
            
        color = self.project.colors[cat_index]
        self.cat_index = cat_index
        self.var_R.set(str(color[0]))
        self.var_G.set(str(color[1]))
        self.var_B.set(str(color[2]))
        self.update_color_frame()
        
    def update_color_frame(self):
        #convert rgb to hex
        r = int(self.var_R.get())
        g = int(self.var_G.get())
        b = int(self.var_B.get())
        color = rgb2hex((r,g,b))
        
        #change color of frame
        self.frm_color.configure(bg=color)
        
    def save_color(self):
        r = int(self.var_R.get())
        g = int(self.var_G.get())
        b = int(self.var_B.get())
        self.project.colors[self.cat_index] = (r, g, b)
        self.project.configure_from_frames()
        self.project.save()
        
        self.master.update_application()
        