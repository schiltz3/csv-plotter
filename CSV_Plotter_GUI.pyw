"""CSV Plotter"""
# coding: utf-8

# In[4]:


import os
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from dataclasses import dataclass
import types
import csv
from functools import partial
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

import numpy as np

LARGE_FONT= ("Verdana", 12)



# In[11]:

class CsvPlotter(tk.Tk):
    """CSV Plotter"""
    use_cols_titles = []
    data_array = None
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "CSV Plotter")

        container = tk.Frame(self)
        container.pack(side="top",
                       fill="both",
                       expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.filename = ""
        self.frames = {}

        for F in (StartPage, GraphPage, SelectColumns):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0,
                       column=0,
                       sticky="nsew")

        #self.show_frame(StartPage)
        self.show_frame(SelectColumns)

    def show_frame(self, cont):
        """Show Frame"""
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    """Start Page"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = ttk.Label(self, text="Home", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self,
                            text="Select Columns",
                            command=lambda: controller.show_frame(SelectColumns))
        button.pack()

class SelectColumns(tk.Frame):
    """Select colum from csv"""
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.title_label = ttk.Label(self, text="Open File", font=LARGE_FONT)
        self.title_label.pack(pady=10,padx=10)
        self.parent = parent
        self.controller = controller

        self.widget_list = []
        self.chech_box = []
        self.check_box_int = []
        self.title_row = []
        self.use_cols = []
        self.title_row_num = 1
        self.spam = False
        self.controller.use_cols_titles = []
        self.controller.data_array = None

        # Open file and get filename
        def select_file():
            self.controller.filename = askopenfilename(parent = self.controller, filetypes=[("CSV","*.csv")])

            if controller.filename != '':
                print(controller.filename)
                if len(self.widget_list) > 0:
                    for bt in self.widget_list:
                        print(bt)
                        bt.destroy()

                button.pack()
                self.widget_list.append(button)
                print("Entering main")
                self.main_init()

        button = ttk.Button(self,
                            text="Select CSV",
                            command=select_file)
        button.pack()


    # Open file and pull out column header data
    def get_title_row(self):
        """Returns title row"""
        with open(self.controller.filename, newline='') as csvfile:
            filedata = csv.reader(csvfile, delimiter=',')
            for row in filedata:
                if filedata.line_num == self.title_row_num :
                    self.title_row = row


    def var_states(self):
        """Prints the state of the checkbox variables"""
        print("check_box")
        for check in self.chech_box:
            print(check.get())

    def convert_boxes(self):
        """Converts checkbox to check_box_int"""
        self.check_box_int = []
        for box in self.chech_box:
            self.check_box_int.append(box.get())
        #print(f"check_box: {self.check_box}")

    def confirm_check(self):
        """Confirms that there is a checkbox selected"""
        #self.var_states()
        self.convert_boxes()
        #print(f"check_box in confirm: {self.check_box}")
        for box in self.check_box_int:
            if box == 1:
                return True
        return False


    def graph(self):
        """The command to move out of the user input loop"""
        if self.confirm_check() is True:
            self.main()
        else:
            if self.spam is False:
                print("Select at least one Box")
                lable = ttk.Label(self,
                                 text="Select at least one Box")
                lable.pack()
                self.widget_list.append(lable)
                self.spam = True
            else:
                self.widget_list.pop().destroy()
                lable = ttk.Label(self,
                                  text="Select at least one Box",
                                  font=('bold'))
                lable.pack()
                self.widget_list.append(lable)

    def create_checkboxes(self):
        """start new top level checkbox window and return list of checked boxes"""
        self.chech_box = []
        self.title_label['text'] = os.path.basename(self.controller.filename)
        for  _title in self.title_row:
            check = tk.IntVar()
            button = ttk.Checkbutton(self,
                           text=_title,
                           variable=check
                           )
            button.pack()
            self.widget_list.append(button)
            self.chech_box.append(check)

        button = ttk.Button(self,
                           text="Go To Graph Page",
                           command=self.graph)
        button.pack()
        self.widget_list.append(button)

#        button = ttk.Button(self,text="Show",command=self.var_states)
#        button.pack()
#        self.widget_list.append(button)

    def get_column_titles(self):
        """Returns Names and Indexes of tiles"""
        self.use_cols = []
        self.convert_boxes()
        self.controller.use_cols_titles = []
        # num is the column index
        for num, check in enumerate(self.check_box_int):
            if check == 1:
                self.use_cols.append(num)
                self.controller.use_cols_titles.append(self.title_row[num])
#        col = None
#        for col in self.use_cols:
#            self.use_cols_titles.append(self.title_row[col])

    def main_init(self):
        """Only used when opening new Files"""
        self.controller.use_cols_titles = []

        # Get the title row from doc
        self.get_title_row()
        print(self.title_row)
        # Create Check box menue from title row
        self.create_checkboxes()
        print("Created menue")

    def main(self):
        """Main method of SelectColumns"""
        # Get columns and column Titles selected in the checkbox menue from doc
        self.get_column_titles()
        print(f"Main use_cols_titles: {self.controller.use_cols_titles}")


        # Open file and create 2D array from data
        self.controller.data_array = np.genfromtxt(self.controller.filename,
                                  dtype=int,
                                  delimiter=",",
                                  skip_header=self.title_row_num,
                                  usecols = self.use_cols,
                                  autostrip=True,
                                  filling_values=0)
        #print(np.info(dataArray))
        print(self.controller.data_array)
        #self.controller.frames.GraphPage.main()
        self.controller.show_frame(GraphPage)


class GraphPage(tk.Frame):
    """Page Three"""
    #data_array = None
    #use_cols_titles = []
    #parent = None
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self,
                         text="Graph Page",
                         font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self,text="Select Columns",
                             command=lambda:controller.show_frame(SelectColumns))
        button1.pack()
        button = ttk.Button(self, text="Update Graph",
                            command=self.main)
        button.pack()

        self.controller = controller
        self.parent = parent
        self.widget_list = []

        #self.update_graph_menue()

    def main(self):
        print ("Graph Main:")
        print (f"data_array:\n{self.controller.data_array}")
        print (f"use_cols_titles: {self.controller.use_cols_titles}")

        for widget in self.widget_list:
            widget.destroy()

        self.ln2, self.fig = self.plotcsv(self.controller.data_array,
                self.controller.use_cols_titles,
                self.get_array(self.controller.data_array, -1),
                self.controller.use_cols_titles[-1])
        self.update_graph_menu()

        self.controller.eval('tk::PlaceWindow . center')


    def plotcsv(self, plot_data, legends, data_array, legends_2):
        """Create Two plots, and fills the top with selected data"""
        #top (general) plot
        #plt.ion()
        figure = plt.figure(figsize=(16,6))
        axes_1 = figure.add_subplot(211)
        axes_1.plot(plot_data)
        plt.grid()
        plt.autoscale(enable=True,axis='both',tight=True)
        plt.ylabel('Magnetic field [LSB]',backgroundcolor='white')
        plt.legend(legends,loc=1,bbox_to_anchor=(1.085,1))

        #bottem (specialty) plot
        axes_2 = figure.add_subplot(212)
        line_2 = axes_2.plot(data_array)
        plt.grid()

        plt.autoscale(enable=True,axis='both',tight=True)
        plt.ylabel('Magnetic field [LSB]',backgroundcolor='white')

        axes_2.legend((line_2[0],),(legends_2,),loc=1,bbox_to_anchor=(1.085,1))
        #plt.pause(0.1)


        canvas = FigureCanvasTkAgg(figure, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM,
                                  fill=tk.BOTH,
                                  expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        self.widget_list.append(toolbar)

        graph_widget = canvas._tkcanvas
        graph_widget.pack(side=tk.TOP,
                              fill=tk.BOTH,
                              expand=True)
        self.widget_list.append(graph_widget)
        return line_2, figure

    def get_array(self, data_array, _col):
        """Wrapper for selecting col from data_array to prevent IndexError"""
        if len(data_array.shape) > 1:
            return data_array[:,_col]
        return data_array
# dynamically make menue of lines to switch bottem graph to
    def update_graph_menu(self):
        """Updates the Graph Menu"""

        #pylint: disable=invalid-name
        _column = 0
        #self = tk.Toplevel()
        for _column, title in enumerate(self.controller.use_cols_titles):
            button = ttk.Button(self,
                      text=title,
                      command=partial(self.update_graph,
                      self.ln2,
                      self.fig,
                      self.get_array(self.controller.data_array,_column),
                      title)
                      )
            button.pack(side=tk.LEFT,pady=4)
            self.widget_list.append(button)
        #pylint: enable-msg=invalid-name

    #pylint: disable=too-many-arguments
    def update_graph(self, lines, figure, data_array, _use_cols_titles, x_data=None, xlab=None, ylab=None):
        """Update bottem graph with new array"""
        y_data = data_array

        #x_data, y_data, xlab, ylab = fourier(data_array)

        lines[0].set_ydata(y_data)
        if x_data is not None:
            lines[0].set_xdata(x_data)
        axes = figure.get_axes()
        axes[1].legend((lines[0],),
                       (_use_cols_titles,),
                       loc=1,
                       bbox_to_anchor=(1.085,1))
        if xlab is not None:
            axes[1].set_xlabel(xlab)
        if ylab is not None:
            axes[1].set_ylabel(ylab)
        axes[1].relim()
        axes[1].autoscale(enable=True,
                          axis='both',
                          tight=True)
        figure.canvas.draw()
        figure.canvas.flush_events()
    #pylint: enable-msg=too-many-arguments



app = CsvPlotter()

# Places window in center
app.eval('tk::PlaceWindow . center')

app.protocol("WM_DELETE_WINDOW",app.quit)
app.mainloop()
app.destroy()




def fourier(signal):
    """Performs a fourier transformation on the 1D array"""
    fourier_data = np.fft.fft(signal)
    number_of_elements = len(signal)
    timestep = float(0.01)
    freq = np.fft.fftfreq(number_of_elements, d=timestep)
    return freq, fourier_data, "frequency", "fourier"

# Named tuple to store name and function reference3 in

@dataclass
class Transformation:
    """Class for storing transformation name and function pointer"""
    name: str
    function: types.FunctionType

#transformations.append(trans("Fourier",fourier))

