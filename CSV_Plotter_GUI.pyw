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

from typing import List

from dataclasses import dataclass
from dataclasses import field
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib
matplotlib.use("TkAgg")



LARGE_FONT= ("Verdana", 12)

@dataclass
class PlotterData:
    """!
    Class used to store and retrieve all data as well as modify it
    """
    frames:     dict = field(default_factory=dict)
    ## Page Title widget handle
    title_label:    ttk.Label = field(init=False)

    ## Handle to the 2nd array's Figure
    fig:            matplotlib.figure.Figure = field(init=False)

    ## 2d array of data pulled from CSV
    file_data:      np.ndarray = field(init=False)

    ## Titles of the selected column in use_cols
    use_cols_titles: List[str] = field(default_factory=list)

    ## Stores filename of CSV
    filename:       str = field(default="")

    ## List of column titles
    title_row:      List[str] = field(default_factory=list)

    ## List of column indexes to import
    use_cols:       List[int] = field(default_factory=list)

    ## Row the title starts on in CSV
    title_row_num:  int = field(default=1)

    ## List of 2nd array's Line
    line:           list = field(default_factory=list)

    ## List of check boxes in column menu
    check_box:      List[tk.IntVar]= field(default_factory=list)

    select_columns_widgets:     list = field(default_factory=list)

    def var_states(self):
        """!
        Prints the state of the checkbox variables
        @param    self    The object pointer
        """
        print("check_box")
        for check in self.check_box:
            print(check.get())

    def confirm_check(self):
        """!
        Confirms that there is a checkbox selected
        @param  self    The object pointer
        @return True    if at least one box is checked\n
        False   if no boxes are checked
        """
        for box in self.check_box:
            if box.get() == 1:
                return True
        return False

    def get_title_row(self):
        """!
        Open file and pull out column header data
        @param    self                The object pointer
        @par      Global Variables Affected
        @link     CsvPlotter.filename filename        @endlink\n
        @link     title_row_num       title_row_num   @endlink\n
        @link     title_row           title_row       @endlink\n
        """
        with open(self.filename, newline='') as csvfile:
            file_handle = csv.reader(csvfile, delimiter=',')
            for row in file_handle:
                if file_handle.line_num == self.title_row_num :
                    self.title_row = row

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

        context = PlotterData()
        self.context = context

        ## Stores the frames that make up the app pages
        # @var frames

        for F in (GraphPage, SelectColumns):
            frame = F(container, self, context)
            context.frames[F] = frame
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
        frame = self.context.frames[cont]
        frame.tkraise()

class SelectColumns(tk.Frame):
    """!
    Tk Frame that displays the data selection screen
    @extends  tk.Frame
    """
    def __init__(self, parent, controller, context):

        tk.Frame.__init__(self, parent)


        ## Object pointer to parent frame
        # @var parent
        self.parent = parent

        ## Object pointer to @link  CsvPlotter  controller  @endlink
        # @var controller
        self.controller = controller

        ## Object pointer to @link PlotterData @endlink
        # @var context
        self.context = context

        ## Page Title widget handle
        # @var title_label
        context.title_label = ttk.Label(self, text="Open File", font=LARGE_FONT)
        context.title_label.pack(pady=10,padx=10)

        ## List of widgets in frame
        # @var widget_list

        ## Prevents user from spamming button
        # @var spam
        self.spam = False

        button = ttk.Button(self,
                            text="Select CSV",
                            command=self.select_file)
        button.pack()
        context.select_columns_widgets.append(button)

    def clear_frame(self):
        """!
        Clear widget list
        """
        if len(self.context.select_columns_widgets) > 0:
            for button in self.context.select_columns_widgets:
                print(button)
                button.destroy()

    def select_file(self):
        """!
        Open file and get filename
        @par    Methods Called
        @link   main_init                                   @endlink
        @par    Global Variables Affected
        @link   self.context.filename       filename        @endlink \n
        @link   SelectColumns.widget_list   widget_list     @endlink
        """
        self.context.filename = askopenfilename(parent = self.controller, filetypes=[("CSV","*.csv")])
        print(f"Context filename: {self.context.filename}")

        if self.context.filename != '':
            self.clear_frame()
            button = ttk.Button(self,
                                text="Select CSV",
                                command=self.select_file)
            button.pack()
            self.context.select_columns_widgets.append(button)
            print(self.context.filename)
            self.main_init()

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
        if self.context.confirm_check() is True:
            if self.spam is True:
                self.context.select_columns_widgets.pop().destroy()
            self.spam = False
            self.main()
        elif self.spam is False:
            print("Select at least one Box")
            lable = ttk.Label(self,
                             text="Select at least one Box",
                             font=('bold'))
            lable.pack()
            self.context.select_columns_widgets.append(lable)
            self.spam = True

    def create_checkboxes(self):
        """!
        Inserts checkbox menue
        @param  self        The object pointer
        @par    Global Variables Affected
        @link   check_box   @endlink\n
        @link   title_label @endlink\n
        @link   widget_list @endlink
        """
        self.context.check_box = []
        self.context.title_label['text'] = os.path.basename(self.context.filename)
        for  _title in self.context.title_row:
            check = tk.IntVar()
            button = ttk.Checkbutton(self,
                           text=_title,
                           variable=check
                           )
            button.pack()
            self.context.select_columns_widgets.append(button)
            self.context.check_box.append(check)

        button = ttk.Button(self,
                           text="Go To Graph Page",
                           command=self.graph)
        button.pack()
        self.context.select_columns_widgets.append(button)

    def get_column_titles(self):
        """!
        Generates Names and Indexes of tiles
        @param  self     The object pointer
        @par Global Variables Affected
        @link   PlotterData.use_cols                            @endlink\n
        @link   convert_boxes                                   @endlink\n
        @link   CsvPlotter.use_cols_titles  use_cols_titles     @endlink\n
        @link   PlotterData.checkboxes                          @endlink\n
        @link   title_row                                       @endlink\n
        """
        self.context.use_cols = []
        self.context.use_cols_titles = []
        # num is the column index
        for num, check in enumerate(self.context.check_box):
            if check.get() == 1:
                self.context.use_cols.append(num)
                self.context.use_cols_titles.append(self.context.title_row[num])

    def main_init(self):
        """!
        Called when entering page for first time after init
        @param  self     The object pointer
        @par    Methods Called
        @link   get_column_titles   @endlink\n
        @link   get_title_row       @endlink\n
        @link   create_checkboxes   @endlink

        @par    Global Variables Affected
        @link   PlotterData.use_cols_titles    use_cols_titles     @endlink
        """
        self.context.use_cols_titles = []

        # Get the title row from doc
        self.context.get_title_row()
        print(self.context.title_row)
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
        print(f"Main use_cols_titles: {self.context.use_cols_titles}")


        # Open file and create 2D array from data
        self.context.file_data = np.genfromtxt(self.context.filename,
                                  dtype=int,
                                  delimiter=",",
                                  skip_header=self.context.title_row_num,
                                  usecols = self.context.use_cols,
                                  autostrip=True,
                                  filling_values=0)
        #print(np.info(dataArray))
        print(self.context.file_data)
        self.controller.show_frame(GraphPage)


class GraphPage(tk.Frame):
    """!
    Tk Frame that handles graphing selected data
    @extends  tk.Frame
    """
    def __init__(self, parent, controller, context):
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

        ## Object pointer to @link PlotterData @endlink
        # @var context
        self.context = context

        ## List of widgets in frame
        # @var widget_list
        self.widget_list = []

    def main(self):
        """!
        Called when Update Graph is clicked
        @param  self    The object pointer
        @par    Global Variables Affected
        @link   widget_list                                 @endlink\n
        @link   PlotterData.file_data        file_data      @endlink\n
        @link   PlotterData.use_cols_titles use_cols_titles @endlink\n
        @link   PlotterData.line             line           @endlink\n
        @link   fig                                         @endlink

        @par    Methods called
        @link   get_array                                   @endlink\n
        @link   update_graph_menu                           @endlink
        """
        print ("Graph Main:")
        print (f"file_data:\n{self.context.file_data}")
        print (f"use_cols_titles: {self.context.use_cols_titles}")

        for widget in self.widget_list:
            widget.destroy()

        self.context.line, self.context.fig = self.plotcsv(self.context.file_data,
                self.context.use_cols_titles,
                self.get_array(self.context.file_data, -1),
                self.context.use_cols_titles[-1])
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
        @link   PlotterData.use_cols_titles @endlink\n
        @link   PlotterData.line    line    @endlink\n
        @link   fig                         @endlink\n
        @link   widget_list                 @endlink
        """

        #pylint: disable=invalid-name
        _column = 0
        for _column, title in enumerate(self.context.use_cols_titles):
            button = ttk.Button(self,
                      text=title,
                      command=partial(self.update_graph,
                      self.context.line,
                      self.context.fig,
                      self.get_array(self.context.file_data,_column),
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

