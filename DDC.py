import os
from time import sleep
from collections import defaultdict
from tkinter import *
from tkinter.ttk import Combobox, Separator

from InputOutput import *
from CanvasDrawer import CanvasDrawer
from GenerateInstances import oneinstance, ninstances
from SolveOpt import get_solution


pressed = False

class DDC(Frame):
    def __init__(self, root):
        super().__init__()
        self.initUI(root)

    #move canvas
    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)
    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    #update x,y pos (cursor
    def update_pos(self, event):
        self.pos.config(text = '{}, {}'.format(self.canvas.canvasx(event.x),
                                               self.canvas.canvasy(event.y)))

    #windows zoom
    def zoomer(self, event):
        if (event.delta > 0):
            self.canvas.scale("all", 0, 0, 1.1, 1.1)
            self.scale *= 1.1
        elif (event.delta < 0):
            self.canvas.scale("all", 0, 0, 0.9, 0.9)
            self.scale *= 0.9

    #linux zoom
    def zoomerP(self,event):
        self.canvas.scale("all", 0, 0, 1.1, 1.1)
        self.scale *= 1.1
        #self.canvas.configure(scrollregion = self.canvas.bbox("all"))
    def zoomerM(self,event):
        self.canvas.scale("all", 0, 0, 0.9, 0.9)
        self.scale *= 0.9

    def create_widgets(self):
        self.canvas = Canvas(self.frame, width=0.60 * self.screenw, height=0.74 * self.screenh, background="bisque")
        self.canvas.pack()
        self.scale = 1.0
        self.origin = [0,0]
        self.canvas.create_oval(-1,-1,1,1, fill="black")

        self.drawer = CanvasDrawer(self.canvas)

        self.drawer.draw_xaxis()
        self.drawer.draw_yaxis()

        # create combobox for colorselection for points
        self.selected_color = StringVar()
        self.color_cb = Combobox(self.content, textvariable=self.selected_color)
        self.color_cb['values'] = ["black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        self.color_cb.current(0)
        self.color_cb['state'] = 'readonly'


        def solve_s():
            print(chr(27) + "[2J")
            get_solution(self.points, False, drawer = self.drawer)

        def solve_r():
            print(chr(27) + "[2J")
            get_solution(self.points, True, drawer = self.drawer)

        self.solve_s = Button(self.content, text="Solve Sim.",
                              command=solve_s)
        self.solve_r = Button(self.content, text="Solve Ref.",
                              command=solve_r)

        self.choose_predef_lbl = Label(self.content, text="predef. instance ")

        self.predef_instance = StringVar()
        self.predef_cb = Combobox(self.content,
                                  textvariable=self.predef_instance)

        #create combobox for selection of solver

        self.sel_solver = StringVar()
        self.solver_cb = Combobox(self.content, textvariable=self.sel_solver)
        self.solver_cb['values'] = ["choose Solver",
                                    "filter", "CONOPT",
                                    "Ipopt", "Knitro",
                                    "SNOPT", "MINOS",
                                    "scip", "BARON",
                                    "Couenne", "OCTERACT"]
        self.solver_cb.current(0)
        self.solver_cb['state'] = 'readonly'

        #list all json files in workingdir
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]

        self.predef_cb['values'] = ['-']+ json_files
        self.predef_cb.current(0)
        self.predef_cb['state'] = 'readonly'

        def load_():
            self.drawer.reset(self.points)
            self.points = defaultdict(list)
            p = load(self.predef_cb.get())
            for color in p:
                for pt in p[color]:
                    self.drawer.draw_point(pt[0],pt[1], self.points, color)

        self.load = Button(self.content, text = "Load", command=load_)

        self.reset = Button(self.content, text="Reset",
            command= lambda: self.drawer.reset(self.points))

        def popup(self):
            self.w = popup(self.master)
            self.save["state"] = "disabled"
            self.master.wait_window(self.w.top)
            if hasattr(self.w,'value'):
                print(self.points)
                save(self.w.value, self.points)
            self.save["state"] = "normal"


        self.save = Button(self.content, text="Save", command=lambda:popup(
            self))

        self.sep = Separator(self.content, orient='horizontal')

        self.nset_lbl = Label(self.content, text="#pointsets:")

        self.nset_entry = Entry(self.content)

        self.nins_lbl = Label(self.content, text="#instances:")

        self.nins_entry = Entry(self.content)

        self.maxp_lbl = Label(self.content, text="max. #points/set:")

        self.maxp_entry = Entry(self.content)

        def random_instance():
            nsets = self.nset_entry.get()
            maxp = self.maxp_entry.get()
            n = self.nins_entry.get()

            sizex, sizey = self.canvas.winfo_width(), self.canvas.winfo_height()
            print(sizex)
            print(sizey)
            if nsets.isdigit() and maxp.isdigit() and n.isdigit():
                nsets, maxp, n  = int(nsets), int(maxp), int(n)
                ninstances(n,sizex, sizey, nsets, maxp, self.drawer)
            else:
                self.input_val_lbl.config(text="please insert integers")
                sleep(2)
                self.random.config(text="Random instance")

        self.random = Button(self.content, text ="Random instance",
                             command=random_instance)

        self.pos = Label(self.content, text="")

        self.input_val_lbl = Label(self.content, text="")

    def place_widgets(self):
        self.content.grid(column=1, row=0)
        self.frame.grid(column=0, row=0, rowspan=16)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.grid_columnconfigure(0, weight=8)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.choose_predef_lbl.grid(column=1, row=0, columnspan=2)
        self.predef_cb.grid(column=1,row=1,columnspan=2)

        self.load.grid(column=1, row=2)
        self.reset.grid(column=2, row=2)

        self.solver_cb.grid(column=1,row=3,columnspan=2)
        self.solve_s.grid(column=1, row=4)
        self.solve_r.grid(column=2, row=4)

        self.pos.grid(column=1, row=5,columnspan=2)
        self.color_cb.grid(column=1, row=6, columnspan=2)
        self.save.grid(column=1,row=7)

        self.sep.grid(column =1, row =8, columnspan=2, sticky="ew")

        self.nset_lbl.grid(column = 1, row = 9,columnspan=2)
        self.nset_entry.grid(column=1, row = 10, columnspan =2)
        self.maxp_lbl.grid(column=1, row =11, columnspan=2)
        self.maxp_entry.grid(column=1,row =12,columnspan=2)
        self.nins_lbl.grid(column=1, row=13, columnspan=2)
        self.nins_entry.grid(column=1, row=14, columnspan=2)
        self.input_val_lbl.grid(column=1, row=15, columnspan=2)
        self.random.grid(column=1,row = 16,columnspan=2)

    def initUI(self, root):
        self.screenw = root.winfo_screenwidth()
        self.screenh = root.winfo_screenheight()
        root.geometry("%dx%d" % (0.75 * self.screenw, 0.75 * self.screenh))

        self.content = Frame(root)
        self.frame = Frame(self.content, borderwidth=5, relief="ridge")

        self.points = defaultdict(list)
        self.create_widgets()
        self.place_widgets()

        self.canvas.bind("<ButtonPress-1>", self.move_start)
        self.canvas.bind("<B1-Motion>", self.move_move)
        self.canvas.bind('<Motion>', self.update_pos)

        def add_point(event):
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            self.drawer.draw_point(x,y, self.points, self.selected_color.get())
        self.canvas.bind('<ButtonPress-2>', add_point)
        self.canvas.bind('<ButtonPress-3>', add_point)

        # scrolling under linux
        self.canvas.bind("<Button-4>", self.zoomerP)
        self.canvas.bind("<Button-5>", self.zoomerM)
        #scrolling under windows
        self.canvas.bind("<MouseWheel>", self.zoomer)

        root.bind_all("<MouseWheel>", self.zoomer)

if __name__ == "__main__":
    root = Tk()
    root.title("Disjoint Disc Covering")
    DDC(root)
    root.mainloop()