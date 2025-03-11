# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 15:51:59 2022

@author: Maarten
"""
#%% import packages
import tkinter as tk

#%% 

class RenameCategory(tk.Toplevel):
    
    def __init__(self, master, category):
        
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.category = category
        self.project = self.master.project
        
        self.new_name = tk.StringVar()
        self.new_name.set(self.master.list_categories.get(self.category))
        
        self.entrybox = tk.Entry(master=self,
                                 textvar = self.new_name)
        
        self.btn_ok = tk.Button(master=self,
                                text='OK',
                                command=self.confirm)
        
        self.entrybox.pack(fill='x')
        self.btn_ok.pack()
        
        #select entrybox
        self.entrybox.focus()
        self.entrybox.select_range(0, tk.END)
        
        self.bind('<Key-Return>', lambda event: self.confirm())
        
        #general settings for a child window
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)
    
    def confirm(self):
        #get new name
        new_name = self.new_name.get()
        
        #update project
        self.project.project_dict[str(self.category)]['name'] = new_name
        self.project.configure_from_dict()
        
        #update category manager
        self.master.load_categories()
                
        #destroy window
        self.destroy()
        