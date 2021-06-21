"""!
Plots CSV files, preforms analysis on the data, and displays it in multiple graphs
"""
# coding: utf-8



import os
import csv
import types
from functools import partial

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from dataclasses import dataclass
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")



LARGE_FONT= ("Verdana", 12)

@dataclass
class PlotterData:
    """!
    Class used to store and retrieve all data as well as modify it
    """


class CsvPlotter(tk.Tk):
    """!
    Parent class for application
    """
    ## Constructor
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "CSV Plotter")

        ## Frame that all other pages are added to
        container = tk.Frame(self)

        container.pack(side="top",
                       fill="both",
                       expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        ## Stores filename of CSV
        # @var string filename
        self.filename = ""

        ## Titles of the selected column in @link SelectColumns.use_cols use_cols@endlink
        # @var use_cols_titles
        self.use_cols_titles = []

        ## 2d array of data pulled from CSV
        # @var data_array
        self.data_array = None

        ## Stores the frames that make up the app pages
        # @var frames
        self.frames = {}

        for F in (GraphPage, SelectColumns):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0,
                       column=0,
                       sticky="nsew")

        self.show_frame(SelectColumns)

    def show_frame(self, cont):
        """!
        Brings the selected Frame to front
        @param    self    the object pointer
        @param    cont    pointer to frame to raise
        """
        frame = self.frames[cont]
        frame.tkraise()

##
class SelectColumns(tk.Frame):
    """!
    Tk Frame that displays the data selection screen
    @extends  tk.Frame
    """
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        ## Page Title widget handle
        # @var title_label
        self.title_label = ttk.Label(self, text="Open File", font=LARGE_FONT)
        self.title_label.pack(pady=10,padx=10)

        ## Object pointer to parent frame
        # @var parent
        self.parent = parent

        ## Object pointer to @link  CsvPlotter  controller  @endlink
        # @var controller
        self.controller = controller

        ## List of widgets in frame
        # @var widget_list
        self.widget_list = []

        ## List of check boxes in column menu
        # @var check_box
        self.check_box = []

        ## @link check_box @endlink represented as intigers
        # @var check_box_int
        self.check_box_int = []

        ## List of column titles
        # @var title_row
        self.title_row = []

        ## List of column indexes to import
        # @var use_cols
        self.use_cols = []

        ## Row the title starts on in CSV
        # @var title_row_num
        self.title_row_num = 1

        ## Prevents user from spamming button
        # @var spam
        self.spam = False

        def select_file():
            """!
            Open file and get filename
            @par    Methods Called
            @link   main_init                                   @endlink
            @par    Global Variables Affected
            @link   self.controller.filename    widget_list     @endlink \n
            @link   SelectColumns.widget_list   widget_list     @endlink
            """
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


    def get_title_row(self):
        """!
        Open file and pull out column header data
        @param    self                The object pointer
        @par      Global Variables Affected
        @link     CsvPlotter.filename filename        @endlink\n
        @link     title_row_num       title_row_num   @endlink\n
        @link     title_row           title_row       @endlink\n
        """
        with open(self.controller.filename, newline='') as csvfile:
            filedata = csv.reader(csvfile, delimiter=',')
            for row in filedata:
                if filedata.line_num == self.title_row_num :
                    self.title_row = row


    def var_states(self):
        """!
        Prints the state of the checkbox variables
        @param    self    The object pointer
        """
        print("check_box")
        for check in self.check_box:
            print(check.get())

    def convert_boxes(self):
        """!
        Converts checkbox to check_box_int
        @param    self    The object pointer
        @par      Global Variables Affected
        @link     check_box_int   @endlink\n
        @link     check_box       @endlink\n
        """
        self.check_box_int = []
        for box in self.check_box:
            self.check_box_int.append(box.get())
        #print(f"check_box: {self.check_box}")

    def confirm_check(self):
        """!
        Confirms that there is a checkbox selected
        @param  self    The object pointer
        @par    Methods Called
        @link   convert_boxes   @endlink

        @return True    if at least one box is checked\n
        False   if no boxes are checked
        """
        #self.var_states()
        self.convert_boxes()
        #print(f"check_box in confirm: {self.check_box}")
        for box in self.check_box_int:
            if box == 1:
                return True
        return False


    def graph(self):
        """!
        The command to move out of the user input loop
        @param  self    The object pointer
        @par    Methods Called
        @link   confirm_check   @endlink\n
        @link   main            @endlink

        @par Global Variables Affected
        @link   widget_list     @endlink\n
        @link   spam            @endlink
        """
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
        """!
        Inserts checkbox menue
        @param  self        The object pointer
        @par    Global Variables Affected
        @link   check_box   @endlink\n
        @link   title_label @endlink\n
        @link   widget_list @endlink
        """
        self.check_box = []
        self.title_label['text'] = os.path.basename(self.controller.filename)
        for  _title in self.title_row:
            check = tk.IntVar()
            button = ttk.Checkbutton(self,
                           text=_title,
                           variable=check
                           )
            button.pack()
            self.widget_list.append(button)
            self.check_box.append(check)

        button = ttk.Button(self,
                           text="Go To Graph Page",
                           command=self.graph)
        button.pack()
        self.widget_list.append(button)

#        button = ttk.Button(self,text="Show",command=self.var_states)
#        button.pack()
#        self.widget_list.append(button)

    def get_column_titles(self):
        """!
        Generates Names and Indexes of tiles
        @param  self     The object pointer
        @par Global Variables Affected
        @link   use_cols                                        @endlink\n
        @link   convert_boxes                                   @endlink\n
        @link   CsvPlotter.use_cols_titles  use_cols_titles     @endlink\n
        @link   check_box_int                                   @endlink\n
        @link   title_row                                       @endlink\n
        """
        self.use_cols = []
        self.convert_boxes()
        self.controller.use_cols_titles = []
        # num is the column index
        for num, check in enumerate(self.check_box_int):
            if check == 1:
                self.use_cols.append(num)
                self.controller.use_cols_titles.append(self.title_row[num])

    def main_init(self):
        """!
        Called when entering page for first time after init
        @param  self     The object pointer
        @par    Methods Called
        @link   get_column_titles   @endlink\n
        @link   get_title_row       @endlink\n
        @link   create_checkboxes   @endlink

        @par    Global Variables Affected
        @link   CsvPlotter.use_cols_titles    use_cols_titles     @endlink
        """
        self.controller.use_cols_titles = []

        # Get the title row from doc
        self.get_title_row()
        print(self.title_row)
        # Create Check box menu from title row
        self.create_checkboxes()
        print("Created menu")

    def main(self):
        """!
        Called when re-visiting SelectColumns page
        @param  self    The object pointer
        @par    Methods Called
        @link   get_column_titles                   @endlink\n
        @link   genfromtxt                          @endlink\n
        @link   CsvPlotter.show_frame   show_frame  @endlink

        @par    Global Variables Affected
        @link   CsvPlotter.data_array   data_array  @endlink\n
        """
        # Get columns and column Titles selected in the checkbox menu from doc
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
        self.controller.show_frame(GraphPage)


class GraphPage(tk.Frame):
    """!
    Tk Frame that handles graphing selected data
    @extends  tk.Frame
    """
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

        ## Object pointer to @link  CsvPlotter  controller  @endlink
        # @var controller
        self.controller = controller

        ## Object pointer to parent frame
        # @var parent
        self.parent = parent

        ## List of widgets in frame
        # @var widget_list
        self.widget_list = []

        ## Handle to 2nd array's Line
        # @var ln2
        self.ln2 = None

        ## Handle to the 2nd array's Figure
        # @var fig
        self.fig = None


    def main(self):
        """!
        Called when Update Graph is clicked
        @param  self    The object pointer
        @par    Global Variables Affected
        @link   widget_list                                 @endlink\n
        @link   CsvPlotter.data_array       data_array      @endlink\n
        @link   CsvPlotter.use_cols_titles  use_cols_titles @endlink\n
        @link   ln2                                         @endlink\n
        @link   fig                                         @endlink

        @par    Methods called
        @link   get_array                                   @endlink\n
        @link   update_graph_menu                           @endlink
        """
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
        """!
        Create Two plots, filling the top with selected data and the bottem
        with a single focused graph
        @param  self        The object pointer
        @param  plot_data   ndArray of data to plot
        @param  legend      Legends for the 2d Array
        @param  data_array  Array of data for 2nd graph
        @param  legends_2   Legend for the 2nd Array
        @par    Global variables affected
        @link   widget_list @endlink\n
        @retval line_2      Handle for the 2nd graph's Line
        @retval figure      Handle for the 2nd graph's figure
        """
        #top (general) plot
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
        """!
        Wrapper for selecting col from data_array to prevent IndexError
        @param  self        The object pointer
        @param  data_array  ndArray to slice
        @param  _col        the index of the column to return
        @return Returns either the 1d array denoted by @link _col @endlink
        or the entire array if it is already a 1d array
        """
        if len(data_array.shape) > 1:
            return data_array[:,_col]
        return data_array
    # dynamically make menu of lines to switch bottem graph to
    def update_graph_menu(self):
        """!
        Updates the Graph Menu
        @param  self    The object pointer
        @par    Global variables affected
        @link   use_cols_titles     @endlink\n
        @link   ln2                 @endlink\n
        @link   fig                 @endlink\n
        @link   widget_list         @endlink
        """

        #pylint: disable=invalid-name
        _column = 0
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
    def update_graph(self, lines, figure, data_array, _use_cols_titles, x_data=None, xlab=None, ylab=None, xrange=None, yrange=None):
        """!Update bottem graph with new array
        @param  self                The object pointer
        @param  lines               Lines to edit
        @param  figure              2nd graph's figure
        @param  data_array          Data to change graph's Y values to
        @param  _use_cols_titles    The legend to apply
        @param  x_data              [optional]  Data to change graph's X values to
        @param  xlab                [optional]  String to set X lable to
        @param  ylab                [optional]  String to set Y lable to
        @param  xrange              [optional]  Touple of lower and upper bounds
        for x range (Currently not implemented)
        @param  yrange              [optional]  Touple of lower and upper bounds
        for y range (Currently not implemented)
        """
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

# Named tuple to store name and function reference in

@dataclass
class Transformation:
    """Class for storing transformation name and function pointer"""
    name: str
    function: types.FunctionType

#transformations.append(trans("Fourier",fourier))

