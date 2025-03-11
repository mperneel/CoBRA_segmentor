# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 09:02:10 2021

@author: Maarten
"""

#%% packages
import tkinter as tk



#%% main code

class RenameObject(tk.Toplevel):
    """
    Child window to rename an object
    """
    def __init__(self, master, current_name):
        #initiate frame
        tk.Toplevel.__init__(self, master)
        self.master = master

        #set title of child window
        self.title("Rename object")
        self.current_name = current_name

        self.bind("<Return>",
                  lambda event: self.confirm())

        self.var_name = tk.StringVar()
        self.var_name.set(self.current_name)
        self.entry_field = tk.Entry(master=self,
                                    textvar=self.var_name,
                                    width=50)
        self.entry_field.grid(row=0, column=0, padx=0, pady=0)
        self.entry_field.select_range(0, tk.END)
        self.entry_field.focus_set()

        #format buttons
        self.btn_frame = tk.Frame(self)
        
        self.ok_btn = tk.Button(self.btn_frame,
                                text='OK',
                                command=self.confirm,
                                width=10)
        self.cancel_btn = tk.Button(self.btn_frame,
                                    text="Cancel",
                                    #command=self.destroy(),
                                    width=10)
        self.ok_btn.grid(row=0, column=0, padx=10, pady=10)
        self.cancel_btn.grid(row=0, column=1, padx=10, pady=10)
        self.btn_frame.grid(row=2, column=0)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        #general settings for a child window
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)
        
    def confirm(self):
        obj_new_name = self.var_name.get()
        
        #change annotation datasets
        if self.master.image.mask_mode:
            self.master.image.rename_mask(current_name=self.current_name,
                                          new_name=obj_new_name)
            
            #update listbox
            self.master.load_masks()
        else:
            self.master.image.rename_object(current_name=self.current_name,
                                            new_name=obj_new_name)
            
            #update listbox
            self.master.load_objects()
            
        #destroy child windows
        self.destroy()
        