# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 22:15:16 2021

@author: Maarten
"""
#%% packages
import tkinter as tk
import seaborn as sns
from tkinter import messagebox
import os
import json

from rename_category import RenameCategory
from written_confirmation_class_removal import WrittenConfirmationClassRemoval

#%% main code
class CategoryManager(tk.Toplevel):
    """
    Child window to modify the categories of the project
    """
    def __init__(self, master):
        #initiate frame
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.project = self.master.project
        
        self.title("Categories")
        
        self.new_name = tk.StringVar()
        self.entry_category = tk.Entry(self,
                                       textvariable=self.new_name)
        self.entry_category.bind("<Key-Return>",
                                 lambda event: self.add_category())
        
        self.frm_categories = tk.Frame(self)
        
        self.list_categories = tk.Listbox(self.frm_categories)
        
        #load all categories        
        for i, name in enumerate(self.project.obj_classes['name']):
            self.list_categories.insert(i, name)
        
        self.scrollbar = tk.Scrollbar(self.frm_categories,
                                      orient="vertical",
                                      width=20)
    
        #configure scrollbar
        self.scrollbar.config(command=self.list_categories.yview)
        self.list_categories.config(yscrollcommand=self.scrollbar.set)
        
        
        self.btn_frm_modifications = tk.Frame(self)
        
        self.btn_add = tk.Button(self,
                                text="add",
                                width=10,
                                command=self.add_category)
        self.btn_delete = tk.Button(self.btn_frm_modifications,
                                   text="delete",
                                   width=10,
                                   command=self.delete_category)
        self.btn_rename = tk.Button(self.btn_frm_modifications,
                                    text="rename",
                                    width=10,
                                    command=self.rename_category)
                
        self.btn_frm_confirmation = tk.Frame(self)
        self.btn_ok = tk.Button(self.btn_frm_confirmation,
                                text= "OK",
                                command=self.confirm)        
        
        #layout all elements
        self.list_categories.pack(side='left',
                                  expand=True,
                                  fill=tk.BOTH)
        self.scrollbar.pack(side='left',
                            fill='y')
        
        self.btn_rename.grid(row=0, column=0, padx=5, pady=5)
        self.btn_delete.grid(row=1, column=0, padx=5, pady=5)       
        
        self.btn_ok.grid(row=0, column=0, padx=5, pady=5)
        
        self.entry_category.grid(row=0, column=0, sticky="we", padx=5, pady=5)
        self.btn_add.grid(row=0,column=1, padx=5, pady=5)
        self.frm_categories.grid(row=1,column=0, sticky="nswe", padx=5, pady=5)
        self.btn_frm_modifications.grid(row=1, column=1, sticky="ns")
        self.btn_frm_confirmation.grid(row=2, column=0, columnspan=2)   
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        #focus on self.entry_category
        self.entry_category.focus()     
            
        #configure tab sequence
        self.entry_category.lift()
        self.btn_add.lift()
        self.list_categories.tkraise()        
        self.btn_rename.tkraise()
        self.btn_delete.tkraise()
        self.btn_ok.lift()
        
        #declare some attributes
        self.go_on = False #attribute used during verification procedures
        
        #general settings for a child window
        #set child to be on top of the main window
        self.transient(master)
        #hijack all commands from the master (clicks on the main window are ignored)
        self.grab_set()
        #pause anything on the main window until this one closes (optional)
        self.master.wait_window(self)
        
    def add_category(self):
        #get properties of class
        class_id = len(self.project.obj_classes)        
        class_name = self.new_name.get()
        color = sns.color_palette('bright')[class_id%10]
        color = [int(i * 255) for i in color]
        
        #update project
        self.project.project_dict[str(class_id)] = {'name': class_name,
                                                    'color': color}
        self.project.configure_from_dict()
        
        #update stringvar and list with categories
        self.new_name.set('')
        self.list_categories.insert(tk.END, class_name)
    
    def delete_category(self):
        """
        Delete a category from the project
        
        Both the project.json file, as well as all the annotation files are
        updated during this procedure
        """
        class_id = self.list_categories.curselection()[0]
        class_name = self.project.obj_classes['name'].iloc[class_id]
        
        self.go_on = messagebox.askyesnocancel(
                    title="Delete class",
                    message="Deleting a class will irreversibly remove all objects " +
                    "within this project belonging to following class:\n\n" +
                    class_name + "\n\n" +
                    "Are you sure you want to delete this class?",
                    icon=messagebox.WARNING)
        
        if self.go_on is None:
            return
        
        if not self.go_on:
            return
        
        #second check: user has to type a sentence
        #sentence: "I know all objects of class {class_name} will be lost irreversibly"
        WrittenConfirmationClassRemoval(master=self,
                                        class_name=class_name)
       
        #WrittenconfirmationClassRemoval will update the value of self.go_on
        if not self.go_on:
            return
        
        #If the method is executed until this point, the deletion procedure may
        #be completed
        
        #update project.json file
        #read json file
        file_object = open("project.json")
        project_dict = json.load(file_object)
        file_object.close()
        
        #update projcet_dict
        project_dict_new = {}
        i = -1
        for key in project_dict:
            class_dict = project_dict[key]
            i += 1
            
            if i < class_id:
                #preserve class dict as such
                project_dict_new[str(i)] = class_dict
            elif i > class_id:
                #lower key of class dict by one
                project_dict_new[str(i-1)] = class_dict
            #else: #i == class_id
                #do nothing -> class will be removed
                
        #update self.project.project_dict
        self.project.project_dict = project_dict_new
        
        #write new project.json file
        file_object = open("project.json", "w")
        json.dump(project_dict_new, file_object, indent=4)
        file_object.close()
        
        #update annotation files
        files = os.listdir()
        for file in files:
            if (file.split(".")[-1] in ["png", "jpg"]) and\
                (file.split(".")[0] + ".json" in files):
                #file is an image with an according annotation json file
                
                #read json file
                file_object = open(file.split(".")[0] + ".json")
                annotations = json.load(file_object)
                file_object.close()
                
                #all objects for which
                #category id < class_id should be left unchanged
                #category id == class_id should be deleted
                #category id > class_id, the category id should be lowered by one
                annotations_new = {}
                i = 0
                for key in annotations:
                    obj_dict = annotations[key]
                    if obj_dict["category"] < class_id:
                        i += 1
                        annotations_new[str(i)] = obj_dict
                    elif obj_dict["category"] > class_id:
                        i += 1
                        obj_dict["category"] -= 1
                        annotations_new[str(i)] = obj_dict
                    #else: #obj_dict["category"] == class_id:
                        #do nothing -> object will be deleted
                        
                #write new json file                
                file_object = open(file.split(".")[0] + ".json", 'w')
                json.dump(annotations_new, file_object, indent=4)
                file_object.close()
                
        #update category manager and application
        self.master.image.load_annotations() #reload annotations of current image
        self.project.configure_from_dict() #reconfigure project
        self.master.update_application() #update application
        self.load_categories() #update category manager
    
    def rename_category(self):
        class_id = self.list_categories.curselection()[0]
        
        RenameCategory(master=self, category=class_id)
    
    def confirm(self):
        self.project.save()
        self.destroy()
        
    def load_categories(self):
        #reset self.list_categories
        self.list_categories.delete(0, tk.END)
        
        #load all category names
        for class_id in self.project.project_dict:
            class_name = self.project.project_dict[class_id]['name']
            self.list_categories.insert(tk.END, class_name)
            
        
        

