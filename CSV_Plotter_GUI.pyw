"""!
Plots CSV files, preforms analysis on the data, and displays it in multiple graphs
"""
# coding: utf-8



import os
import csv
import sys
import re
from typing import Callable
from typing import List
from typing import Dict
from functools import partial

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from dataclasses import dataclass
from dataclasses import field
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib
matplotlib.use("TkAgg")



## Font for Titles
# @var LARGE_FONT
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

    ## Touple for x_range
    x_range:        tuple = field(default=(0,0))
    x_range_text:   tk.StringVar     = field(default_factory=tk.StringVar)

    ## Touple for y_range
    y_range:        str = field(default="")
    y_range_text:        str = field(default="")

    ## List of check boxes in column menu
    check_box:      List[tk.IntVar]= field(default_factory=list)

    select_columns_widgets: Dict[str, tk.Widget] = field(default_factory=dict)

    ## The current column being plotted
    current_plot:    np.ndarray = field(init=False)
    current_legend:  str = field(default="")
    current_transformation:  str = field(default="None")

    ## GraphPage Widgets
    graph_widgets: Dict[str, tk.Widget] = field(default_factory=dict)


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

class PlotterEvents:
    """!
    Class that handles events for csv_plotter_gui
    """
    def __init__(self, data_class):
        self.context = data_class
        self.events = {str:Callable}

    def trigger_event(self, event_id, **kwargs):
        """!
        Runs function specified by event_id with args
        @param  event_id    The key for the function in the events dictionary
        @param  kwargs        The keyword arguments passed to the function
        """
        self.events.get(event_id)(**kwargs)

    def register_event(self, event_id, function):
        """!
        registers a function to a hook
        @param  parent      The parent class of the function
        @param  event_id    The String of one of the handles in self.events
        @param  function    The function pointer
        @return returns the preevious event list if one existed
        """
        _return = self.events.get(event_id)
        self.events[event_id] = function
        return _return

    def get_list_of_events(self):
        """!
        returns a dictionary of event keys
        @return self.events keys
        """
        return self.events.keys()



class CsvPlotter(tk.Tk):
    """!
    Parent class for application
    """
    ## Constructor
    def __init__(self, *args, **kwargs):
        filename = ""
        if "filename" in kwargs:
            filename = str(kwargs.pop("filename"))
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "CSV Plotter")

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.resizable(True, True)

        ## Frame that all other pages are added to
        container = tk.Frame(self)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        container.grid(sticky=tk.NSEW)


        context = PlotterData()
        context.filename = filename
        self.context = context

        events = PlotterEvents(context)
        #events = context
        ## Stores the frames that make up the app pages
        # @var frames

        for F in (GraphPage, SelectColumns):
            frame = F(container, self, context, events)
            context.frames[F] = frame
            frame.grid(row=0,
                       column=0,
                       sticky=tk.NSEW)
            frame.grid_remove()

        events.trigger_event("SelectFile")
        self.show_frame(SelectColumns)

    def show_frame(self, cont):
        """!
        Brings the selected Frame to front
        @param    self    the object pointer
        @param    cont    pointer to frame to raise
        """
        for F in self.context.frames.values():
            F.grid_remove()
        frame = self.context.frames[cont]
        frame.grid()
        frame.tkraise()
        self.update()
        self.geometry("")
        self.eval('tk::PlaceWindow . center')


class SelectColumns(tk.Frame):
    """!
    Tk Frame that displays the data selection screen
    @extends  tk.Frame
    """
    def __init__(self, parent, controller, context, handler):

        tk.Frame.__init__(self, parent)

        self.columnconfigure(0, weight=1)

        ## Object pointer to parent frame
        # @var parent
        self.parent = parent

        ## Object pointer to @link  CsvPlotter  controller  @endlink
        # @var controller
        self.controller = controller

        ## Object pointer to @link PlotterData @endlink
        # @var context
        self.context = context

        self.handler = handler

        ## Page Title widget handle
        # @var title_label
        context.title_label = ttk.Label(self, text="Open File", font=LARGE_FONT)
        context.title_label.grid(column=0, sticky=tk.N)

        ## Prevents user from spamming button
        # @var spam
        self.spam = False

        button = ttk.Button(self,
                            text="Select CSV",
                            command=lambda:self.select_file(True))
        button.grid(column=0, sticky=tk.NSEW)
        context.select_columns_widgets["SelectCSV"] = button
        self.handler.register_event("SelectFile", self.select_file)

    def clear_frame(self):
        """!
        Clear widget list
        """
        if len(self.context.select_columns_widgets) > 0:
            for button in self.context.select_columns_widgets.values():
                button.destroy()

    def select_file(self, new_file = False):
        """!
        Open file and get filename
        @par    Methods Called
        @link   main_init                   @endlink
        @par    Global Variables Affected
        PlotterData.filename\n
        SelectColumns.widget_list
        """
        if self.context.filename == "" or new_file is True:
            self.context.filename = ''
            self.context.filename = askopenfilename(parent = self.controller,
                                                filetypes=[("CSV","*.csv")])

        if self.context.filename != '':
            self.clear_frame()
            button = ttk.Button(self,
                                text="Select CSV",
                                command=lambda:self.select_file(True))
            self.context.select_columns_widgets["SelectCSV"] = button
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
        widget_list\n
        spam
        """
        if self.context.confirm_check() is True:
            if self.spam is True:
                self.context.select_columns_widgets.get("Spam").destroy()
            self.spam = False
            self.main()
        elif self.spam is False:
            label = ttk.Label(self,
                             text="Select at least one Box",
                             font=('bold'),
                             anchor='center',
                             background="red")
            self.context.select_columns_widgets["Spam"] = label
            self.spam = True
            self.render_page()

    def create_checkboxes(self):
        """!
        Inserts checkbox menue
        @param  self        The object pointer
        @par    Global Variables Affected
        @link   check_box   @endlink\n
        @link   PlotterData.title_label @endlink\n
        @link   widget_list @endlink
        """
        self.context.check_box = []
        self.context.title_label['text'] = os.path.basename(self.context.filename).split('.')[0]
        checkbutton_frame = tk.Frame(self)
        checkbutton_frame.columnconfigure(0, weight=1)
        for  _title in self.context.title_row:
            check = tk.IntVar()
            button = ttk.Checkbutton(checkbutton_frame,
                           text=_title,
                           variable=check
                           )
            button.grid(column=0)
            self.context.check_box.append(check)


        self.context.select_columns_widgets["CheckButtonFrame"] = checkbutton_frame
        button = ttk.Button(self,
                           text="Go To Graph Page",
                           command=self.graph)
        self.context.select_columns_widgets["Graph"] = button

        self.render_page()

    def render_page(self):

        self.columnconfigure(0,weight=10)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=10)
        self.rowconfigure(0,weight=10)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=10)

        self.context.title_label.grid(column=1,
                row=0,
                sticky=tk.S)
        self.context.select_columns_widgets.get("SelectCSV").grid(column=1,
                row=1,
                sticky=tk.NSEW)
        self.context.select_columns_widgets.get("CheckButtonFrame").grid(column=1,
                row=2,)
        self.context.select_columns_widgets.get("Graph").grid(column=1,
                row=3,
                sticky=tk.NSEW)
        if self.spam is True:
            self.context.select_columns_widgets.get("Spam").grid(column=1,
                    row=4,
                    sticky=tk.NSEW)


    def get_column_titles(self):
        """!
        Generates Names and Indexes of tiles
        @param  self     The object pointer
        @par Global Variables Affected
        @link   PlotterData.use_cols                            @endlink\n
        @link   PlotterData.convert_boxes                                   @endlink\n
        @link   PlotterData.use_cols_titles  use_cols_titles     @endlink\n
        @link   PlotterData.checkboxes                          @endlink\n
        @link   PlotterData.title_row                                       @endlink\n
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
        # Create Check box menu from title row
        self.create_checkboxes()

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

        # Open file and create 2D array from data
        self.context.file_data = np.genfromtxt(self.context.filename,
                                  dtype=int,
                                  delimiter=",",
                                  skip_header=self.context.title_row_num,
                                  usecols = self.context.use_cols,
                                  autostrip=True,
                                  filling_values=0)
        #print(np.info(dataArray))
        self.handler.trigger_event("Graph")
        self.controller.show_frame(GraphPage)


class GraphPage(tk.Frame):
    """!
    Tk Frame that handles graphing selected data
    @extends  tk.Frame
    """
    def __init__(self, parent, controller, context, handler):
        tk.Frame.__init__(self, parent)

        ## Object pointer to @link  CsvPlotter  controller  @endlink
        # @var controller
        self.controller = controller

        ## Object pointer to parent frame
        # @var parent
        self.parent = parent

        ## Object pointer to @link PlotterData @endlink
        # @var context
        self.context = context

        self.handler = handler

        self.transformation = Transformations(context)

        handler.register_event("Graph", self.main)
        handler.register_event("UpdateGraph", self.update_graph)

    def main(self):
        """!
        Called when Update Graph is clicked
        @param  self    The object pointer
        @par    Global Variables Affected
        @link   file_data        file_data      @endlink\n
        @link   PlotterData.use_cols_titles use_cols_titles @endlink\n
        @link   PlotterData.line             line           @endlink\n
        @link   fig                                         @endlink

        @par    Methods called
        @link   get_array                                   @endlink\n
        @link   create_graph_menu                           @endlink
        """
        for widget in self.context.graph_widgets.values():
            widget.destroy()
        self.context.graph_widgets["FileTitle"] = tk.Label(self,
                                                      text="",
                                                      font=LARGE_FONT)

        self.context.graph_widgets["SelectColumns"] = ttk.Button(self, text="Select Columns",
                             command=lambda:self.controller.show_frame(SelectColumns))
        self.context.graph_widgets["FileTitle"]['text'] = os.path.basename(self.context.filename).split('.')[0]

        self.context.current_plot = self.get_array(self.context.file_data, -1)
        self.context.line, self.context.fig = self.plotcsv(self.context.file_data,
                self.context.use_cols_titles,
                self.context.current_plot,
                self.context.use_cols_titles[-1])

        self.create_graph_menu()
        self.create_transformation_menu()
        self.create_range_menu()
        self.render_page()

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
        @retval line_2      Handle for the 2nd graph's Line
        @retval figure      Handle for the 2nd graph's figure
        """
        #top (general) plot
        figure = plt.figure(figsize=(16,6))
        axes_1 = figure.add_subplot(211)
        axes_1.plot(plot_data)
        #plt.subplots_adjust(left=.08)
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
        self.context.current_legend = legends_2
        axes_2.legend((line_2[0],),(legends_2,),loc=1,bbox_to_anchor=(1.085,1))


        canvas = FigureCanvasTkAgg(figure, self)
        canvas.draw()
        self.context.graph_widgets["Canvas"] = canvas.get_tk_widget()
        self.context.graph_widgets["Toolbar"] = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        self.context.graph_widgets["Toolbar"].update()
        #self.context.graph_widgets["TKCanvas"] = canvas._tkcanvas
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
    def create_graph_menu(self):
        """!
        Updates the Graph Menu
        @param  self    The object pointer
        @par    Global variables affected
        @link   PlotterData.use_cols_titles @endlink\n
        @link   PlotterData.line    line    @endlink\n
        @link   fig                         @endlink\n
        """

        graph_menu = tk.Frame(self)
        graph_menu.columnconfigure(0,weight=1)
        for _column, title in enumerate(self.context.use_cols_titles):
            button = ttk.Button(graph_menu,
                    text=title,
                    command=partial(self.change_array,
                        self.get_array(self.context.file_data,_column),
                        title))
            button.grid(padx=1,
                    sticky=tk.NSEW)
        self.context.graph_widgets["GraphMenu"] = graph_menu

    def validate_range(self,  axis, newval, op):
        PATTERN = '^-?\d+,\d+$'
        PARTIAL_PATTERN = '^-?$|^-?\d+,?(\d+)?$'

        match = re.match(PATTERN, newval)
        valid = bool(match)

        if op=='key':
            ok_so_far = re.match(PARTIAL_PATTERN, newval) is not None
            if valid:
                if axis == "x":
                    self.context.x_range = tuple(map(int,newval.split(",")))
                    self.update_graph(x_range= self.context.x_range, normal_x_direction = True)
                    self.update_top_graph(x_range= self.context.x_range, normal_x_direction = True)
                elif axis == "y":
                    self.context.y_range = tuple(map(int,newval.split(",")))
                    self.update_graph(y_range= self.context.y_range, normal_y_direction = True)
                    self.update_top_graph(y_range= self.context.y_range, normal_y_direction = True)
            elif not ok_so_far:
                if axis == "x":
                    self.update_graph(x_autoscale=True)
                    self.update_top_graph(x_autoscale=True)
                elif axis == "y":
                    self.update_graph(y_autoscale=True)
                    self.update_top_graph(y_autoscale=True)
            return ok_so_far
        elif op == 'focusout' or op == 'focusin':
            if valid:
                if axis == "x":
                    self.context.x_range = tuple(map(int,newval.split(",")))
                    self.update_graph(x_range= self.context.x_range)
                    self.update_top_graph(x_range= self.context.x_range)
                if axis == "y":
                    self.context.y_range = tuple(map(int,newval.split(",")))
                    self.update_graph(y_range= self.context.y_range)
                    self.update_top_graph(y_range= self.context.y_range)
            else:
                if axis == "x":
                    self.update_graph(x_autoscale=True)
                    self.update_top_graph(x_autoscale=True)
                elif axis == "y":
                    self.update_graph(y_autoscale=True)
                    self.update_top_graph(y_autoscale=True)
        return valid

    def create_range_menu(self):
        """!
        Creates the widges for the the range entry boxes
        """
        range_frame = ttk.Frame(self)

        axis = "x"
        validate_range_wrapper = (range_frame.register(self.validate_range), axis, '%P', '%V')

        widget = ttk.Label(range_frame, text="X Range")
        #self.context.x_range_text.set("low,high")
        widget.grid(column=0, row=0)
        widget = ttk.Entry(range_frame,
                textvariable=self.context.x_range_text,
                validate="all",
                validatecommand=validate_range_wrapper)
        widget.grid(column=0, row=1)

        axis = "y"
        validate_range_wrapper_y = (range_frame.register(self.validate_range), axis, '%P', '%V')
        widget = ttk.Label(range_frame, text="Y Range")
        widget.grid(column=1, row=0)
        widget = ttk.Entry(range_frame,
                textvariable=self.context.y_range,
                validate="all",
                validatecommand=validate_range_wrapper_y)
        widget.grid(column=1, row=1)
        self.context.graph_widgets["RangeMenu"] = range_frame

    def create_transformation_menu(self):
        """!
        Creates the widges for the the transformation menu
        """
        transform_menu = tk.Frame(self)
        for count, trans in enumerate(self.transformation.get_list_of_transformations()):
            button = ttk.Button(transform_menu,
                    text=str(trans),
                    command=partial(self.change_transformation,
                        trans))
            button.grid(row=0,column=count,padx=1,pady=1)
        self.context.graph_widgets["TransformationMenu"] = transform_menu

    def render_page(self):
        """!
        Lays out all of the widgets on the graph page
        """
        NUM_OF_COLUMNS = 3
        self.columnconfigure(0, weight=1, minsize = 45)
        self.columnconfigure(1, weight=100)
        self.rowconfigure(0, weight=10, minsize=30)
        self.rowconfigure(1, weight=2, minsize=25)
        self.rowconfigure(2, weight=100)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=2)
        self.rowconfigure(6, weight=0)
        self.rowconfigure(7, weight=0)
        self.context.graph_widgets.get("FileTitle").grid(column=0,
                row=0,
                columnspan=NUM_OF_COLUMNS,
                sticky=tk.NS)
        self.context.graph_widgets.get("Toolbar").grid(column=1,
                row=1,
                sticky=tk.W+tk.S)
        self.context.graph_widgets.get("SelectColumns").grid(column=0,
                row=1,
                columnspan=NUM_OF_COLUMNS,
                sticky=tk.NS,
                padx=1,
                pady=1)
        self.context.graph_widgets.get("Canvas").grid(column=1,
                row=2,
                rowspan=4,
                sticky=tk.NSEW,
                padx=1,
                pady=1)
        self.context.graph_widgets.get("GraphMenu").grid(column=0,
                row=5,
                sticky=tk.S+tk.E+tk.W,
                padx=1,
                pady=1)
        self.context.graph_widgets.get("TransformationMenu").grid(column=1,
                row=6,
                columnspan=NUM_OF_COLUMNS,
                sticky=tk.W+tk.N,
                padx=1,
                pady=1)
        self.context.graph_widgets.get("RangeMenu").grid(column=1,
                row=6,
                columnspan=NUM_OF_COLUMNS,
                sticky=tk.N,
                ipady=5)
    def change_array(self, array, legend, **kwargs):
        """Set the current plot and current legend then update the graph
        using the current transformation"""
        self.context.current_plot = array
        self.context.current_legend = legend

        var1, var2 = self.transformation.call_transform(self.context.current_transformation,**kwargs)
        self.update_graph(**var1)
        if var2 is not None:
            self.update_top_graph(**var2)

    def change_transformation(self, transformation, **kwargs):
        """Set the transformation then update the graph using the current
        plot and legend"""
        self.context.current_transformation = transformation

        var1, var2 = self.transformation.call_transform(transformation,**kwargs)
        self.update_graph(**var1)
        if var2 is not None:
            self.update_top_graph(**var2)


    def update_top_graph(self, **kwargs):
        axis = self.context.fig.get_axes()[0]

        # Axis scaling
        axis.relim()
        if "x_autoscale" in kwargs:
            axis.autoscale(enable=kwargs.pop("x_autoscale"), axis='x', tight=True)
        if "y_autoscale" in kwargs:
            axis.autoscale(enable=kwargs.pop("y_autoscale"),axis='y',tight=True)

        # X and Y ranges
        if "x_range" in kwargs:
            axis.set_xlim(kwargs.pop("x_range"))
        if "y_range" in kwargs:
            axis.set_ylim(kwargs.pop("y_range"))

        if "normal_x_direction" in kwargs:
            if axis.xaxis_inverted():
                axis.invert_xaxis()
        if "normal_y_direction" in kwargs:
            if axis.yaxis_inverted():
                axis.invert_yaxis()

        # Force update
        self.context.fig.canvas.draw()
        self.context.fig.canvas.flush_events()

    def update_graph(self, **kwargs):
        """!Update bottem graph with new array
        @param  self                The object pointer
        @param  y_data              Array to change graph's Y values to
        @param  _use_cols_titles    The legend to apply
        @param  x_data              [optional]  Data to change graph's X values to
        @param  x_lab               [optional]  String to set X label to
        @param  y_lab               [optional]  String to set Y label to
        @param  x_range             [optional]  Touple of lower and upper bounds
        for x range (Currently not implemented)
        @param  y_range             [optional]  Touple of lower and upper bounds
        for y range (Currently not implemented)
        """
        # Update X and Y data
        if "x_data" in kwargs:
            self.context.line[0].set_xdata(kwargs.pop("x_data"))
        if "y_data"  in kwargs:
            self.context.line[0].set_ydata(kwargs.pop("y_data"))

        axis = self.context.fig.get_axes()[1]

        # Update legend
        if "legend" in kwargs:
            axis.legend((self.context.line[0],),
                           (kwargs.pop("legend"),),
                           loc=1,
                           bbox_to_anchor=(1.085,1))

        # X and Y labels
        if "x_lab" in kwargs:
            axis.set_xlabel(kwargs.pop("x_lab"))
        if "y_lab" in kwargs:
            axis.set_ylabel(kwargs.pop("y_lab"))

        # Axis scalling
        axis.relim()
        if "x_autoscale" in kwargs:
            axis.autoscale(enable=kwargs.pop("x_autoscale"), axis='x', tight=True)
        if "y_autoscale" in kwargs:
            axis.autoscale(enable=kwargs.pop("y_autoscale"),axis='y',tight=True)

        # X and Y ranges
        if "x_range" in kwargs:
            axis.set_xlim(kwargs.pop("x_range"))
        if "y_range" in kwargs:
            axis.set_ylim(kwargs.pop("y_range"))

        if "normal_x_direction" in kwargs:
            if axis.xaxis_inverted():
                axis.invert_xaxis()
        if "normal_y_direction" in kwargs:
            if axis.yaxis_inverted():
                axis.invert_yaxis()

        # Force update
        self.context.fig.canvas.draw()
        self.context.fig.canvas.flush_events()

class Transformations:
    """!
    Class that handles transforms for GraphPage
    """
    def __init__(self, context):
        """!
        @param context          A handle to the event handler
        """
        ## instence of @link DataClass @end
        self.context = context
        ## Dictionary for Transformation Title : transformation handle
        self.transforms = {}
        self.register_transform("ZeroCrossings", self.frequency)
        self.register_transform("Fourier", self.fourier)
        self.register_transform("None", self.none)

    def call_transform(self,transform_id, **kwargs):
        """!
        Runs function specified by transform_id with kwargs
        @param  transform_id    The key for the function in the transforms dictionary
        @param  kwargs          The keyword args passed to the function
        """
        return self.transforms.get(transform_id)(**kwargs)

    def register_transform(self, transform_id, function):
        """!
        registers a function to a hook
        @param  parent          The parent class of the function
        @param  transform_id    The String of one of the handles in self.transforms
        @param  function        The function pointer
        @return returns the previous function if one existed
        """
        _return = self.transforms.get(transform_id)
        self.transforms[transform_id] = function
        return _return

    def get_list_of_transformations(self):
        """!
        returns a list of of transforms keys
        @return self.transforms keys
        """
        return self.transforms.keys()

    def fourier(self, **kwargs):
        """!Performs a fourier transformation on the 1D array"""
        _return = kwargs
        _return2 = None
        _return["y_data"] = np.fft.fft(self.context.current_plot)
        number_of_elements = len(self.context.current_plot)
        timestep = float(0.01)
        _return["x_data"] = np.fft.fftfreq(number_of_elements, d=timestep)
        _return["y_lab"] = "Fourier"
        _return["x_lab"] = "Frequency"
        _return["legend"] = self.context.current_legend + " Fourier"
        _return["x_autoscale"] = True
        _return["y_autoscale"] = True
        _return2 = {}
        _return2["x_autoscale"] = True
        _return2["y_autoscale"] = True
        return (_return, _return2)

    def none(self, **kwargs):
        """!Does not apply a transformation Instead, just gets current_plot and passes kwargs though"""
        _return = kwargs
        _return2 = None
        _return["y_data"] = self.context.current_plot
        _return["x_data"] = np.array([*range(0,self.context.current_plot.size)])
        _return["legend"] = self.context.current_legend
        _return["x_lab"] = ".01 Second"
        _return["y_lab"] = "Magnetic field [LSB]"
        _return["x_autoscale"] = True
        _return["y_autoscale"] = True
        _return2 = {}
        _return2["x_autoscale"] = True
        _return2["y_autoscale"] = True
        return (_return, _return2)

    def frequency(self, **kwargs):
        """!Calculates the zero crossings and sets a boolean"""
        samples = 20
        _return = kwargs
        _return2 = None
        _return["x_data"] = np.array([*range(0,self.context.current_plot.size)])
        frequency = np.empty_like(self.context.current_plot)
        history = np.full(samples, -0, np.int16)
        pos = False
        for i, value in enumerate(self.context.current_plot):
            crossings = 0
            history[i%samples] = value
            for element in history:
                if element > 0 and pos is False:
                    crossings += 1
                    pos = True
                if element < 0 and pos is True:
                    crossings += 1
                    pos = False
            frequency[i] = crossings

        _return["y_data"] = frequency
        _return["x_lab"] = ".01 Second"
        _return["y_lab"] = "Zero Crossings"
        _return["legend"] = self.context.current_legend + " Zero Crossings"
        _return["x_autoscale"] = True
        _return["y_autoscale"] = True
        _return2 = {}
        _return2["x_autoscale"] = True
        _return2["y_autoscale"] = True
        return (_return, _return2)

# Named tuple to store name and function reference in


ARG_FILENAME = ""
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    ARG_FILENAME = os.path.join(os.path.abspath('./'), sys.argv[1])

app = CsvPlotter(filename=ARG_FILENAME)

# Places window in center
app.eval('tk::PlaceWindow . center')

app.protocol("WM_DELETE_WINDOW",app.quit)
app.mainloop()
app.destroy()
