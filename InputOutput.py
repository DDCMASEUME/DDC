import json
import os
from tkinter import Toplevel, Label, Entry, Button


class popup(object):
    def __init__(self,master):
        top=self.top=Toplevel(master)
        self.label = Label(top,text="Insert filename")
        self.label.pack()
        self.entry=Entry(top)
        self.entry.pack()
        self.btn=Button(top, text='OK', command=self.close)
        self.btn.pack()
    def close(self):
        v=self.entry.get()
        if os.path.isfile(v+".json"):
            self.label.config(text="File exists. Choose different "
                                   "name. ")
        else:
            self.value = v
            self.top.destroy()

#for saving and loading pointset instances as json
def save(name, points):
    with open(name + ".json", 'w') as file:
        json.dump(points, file, indent=4)
    file.close()

def load(name):
    with open(name, "r") as file:
        p = json.load(file)
    file.close()
    return p