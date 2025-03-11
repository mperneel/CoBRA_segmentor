# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 11:14:27 2022

@author: Maarten
"""

#%% import packages
import tkinter as tk

#%% main code

class WrittenConfirmationClassRemoval(tk.Toplevel):
    """
    Child window to modify the categories of the project
    """
    def __init__(self, master, class_name):
        #initiate frame
        tk.Toplevel.__init__(self, master, width=500)
        self.master = master
        
        #define correct confirmation-sentence
        self.confirmation_sentence = "I know all objects of class " +\
            class_name + " will be lost irreversibly"
               
        #define label
        
        message = "To activate the removal operation, type following sentence:\n\n" +\
            self.confirmation_sentence
        
        self.update() #update application, so width is available
        self.lab_message = tk.Label(self,
                                    text = message,
                                    wraplength=self.winfo_width(),
                                    justify="left")
        self.bind('<Configure>', lambda event : self.lab_message.config(wraplength=self.winfo_width()))
        
        #define entry
        self.var_sentence = tk.StringVar()
        self.entry_sentence = tk.Entry(self,
                                       textvariable=self.var_sentence)
        
        #define button  
        self.btn_ok = tk.Button(self,
                                text= "OK",
                                command=self.confirm)
        self.btn_cancel = tk.Button(self,
                                text="Cancel",
                                command=self.cancel)
        
        #layout all elements
        self.lab_message.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.entry_sentence.grid(row=1, column=0, columnspan=2, sticky="we", padx=5, pady=5)
        self.btn_ok.grid(row=2, column=0, sticky="se", padx=5, pady=5)  
        self.btn_cancel.grid(row=2, column=1, sticky="sw", padx=5, pady=5)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        #focus on self.btn_cancel
        self.btn_cancel.focus()
        
        
            
        #general settings for a child window
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)
        
    def confirm(self):
        #check if right confirmation sentence was entered
        
        input_sentence = self.var_sentence.get()
        if input_sentence == self.confirmation_sentence:
            #correct confirmation sentence was entered, all objects of the class
            #may be removed
            self.master.go_on = True
            self.destroy()
        else:
            #wrong confirmation sentence was entered, class deletion procedure
            #has to be aborted
            self.master.go_on = False
            self.destroy()
    
    def cancel(self):
        #abort class deletion procedure
        self.master.go_on = False
        self.destroy()





