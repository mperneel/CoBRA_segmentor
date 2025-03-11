# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 14:30:09 2022

@author: Maarten
"""

#%% packages
import tkinter as tk


#%% main code
class LinewidthDialog(tk.Toplevel):
    """
    Child window to set the Linewidth in the annotation_canvas
    """
    def __init__(self, master):
        #initiate frame
        tk.Toplevel.__init__(self, master)
        self.master = master
        
        #define variables
        self.var_linewidth = tk.StringVar(self)
        self.var_linewidth.set(str(self.master.annotation_canvas.linewidth))
        
        #define label
        self.lab_linewidth = tk.Label(self,
                                      text="Linewidth")
        
        #define entryfield
        self.entry_linewidth = tk.Entry(self,
                                        textvar = self.var_linewidth)   
        self.entry_linewidth.bind('<FocusOut>',
                                  lambda event : self.check_linewidth_entry())
                    
        
        #define buttons
        self.btn_ok = tk.Button(self,
                                text='OK',
                                command=self.confirm)
        
        #layout all elements
        self.lab_linewidth.grid(row=0, column=0)
        self.entry_linewidth.grid(row=0, column=1, sticky='we')
        self.btn_ok.grid(row=1, column=0, columnspan=2, sticky='s')
        
        #program bindings
        """
        self.btn_ok.bind("<Key-Return>",
                         lambda event : self.confirm())
        """
        
        #set focus
        self.btn_ok.focus()
        
        #general settings for a child window
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)
        
    def check_linewidth_entry(self):
        value = self.var_linewidth.get()
        
        try:
            value = int(value)
            value = max(0, value)
        except:
            value = self.master.annotation_canvas.linewidth
            
        self.var_linewidth.set(str(value))   
        
    def confirm(self):
        self.master.annotation_canvas.linewidth = int(self.var_linewidth.get())
        self.master.update_application()
        self.destroy()