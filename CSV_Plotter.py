"""CSV Plotter"""
# coding: utf-8

# In[4]:


import matplotlib.pyplot as plt

from dataclasses import dataclass
import types
import threading
import csv
from functools import partial
import tkinter as tk
from tkinter.filedialog import askopenfilename
import numpy as np

LARGE_FONT= ("Verdana", 12)



# In[11]:
root = tk.Tk()
root.withdraw()
filename = askopenfilename(filetypes=[("CSV","*.csv")])
print(filename)

# Structure varialbes
use_cols_titles = ()
TITLE_ROW_NUM = 3


# Open file and pull out column header data
def get_title_row(_filename, _title_row_num):
    """Returns title row"""
    _return = None
    with open(_filename, newline='') as csvfile:
        filedata = csv.reader(csvfile, delimiter=',')
        for row in filedata:
            if filedata.line_num == _title_row_num :
                _return = row
    return _return

def create_checkboxes(_title_row):
    """start new top level checkbox window and return list of checked boxes"""
    checkbox_menu = tk.Toplevel()
#    def var_states():
#        print("chbx")
#        for check in chbx:
#            print(check.get())
    def convert_boxes():
        for box in chbx:
            check_box_int.append(box.get())
    def confirm_check():
        for box in chbx:
            if box.get() == 1:
                checkbox_menu.quit()
        tk.Label(checkbox_menu,
                 text="Select at least one Box"
                 ).grid(row=_column+3,
                        sticky=tk.W,
                        pady=4)
    check_box_int = []
    chbx = []
    _column = 0
    for _column, _title in enumerate(_title_row):
        ch_p = tk.IntVar()
        tk.Checkbutton(checkbox_menu,
                       text=_title,
                       variable=ch_p
                       ).grid(row=_column,
                                           sticky=tk.W)
        chbx.append(ch_p)
    tk.Button(checkbox_menu,
              text="Ok",
              command=confirm_check).grid(row=_column+1,
                                          sticky=tk.W,
                                          pady=4)
#    tk.Button(master,text="Show",command=var_states).grid(row=col+2, sticky=tk.W, pady=4)
    tk.mainloop()
    checkbox_menu.destroy()
    convert_boxes()
    return check_box_int

def get_column_titles(titles, chbx):
    """Returns Names and Indexes of tiles"""
    columns = []
    column_titles = []
    #user loop
    for num, check in enumerate(chbx):
        if check == 1:
            columns.append(num)
    for col in columns:
        column_titles.append(titles[col])
    return column_titles, columns # names and indexes of titles

# Get the title row from doc
title_row = get_title_row(filename, TITLE_ROW_NUM)

# Create Check box menue from title row
check_box = create_checkboxes(title_row)

# Get columns and column Titles selected in the checkbox menue from doc
use_cols_titles, use_cols = get_column_titles(title_row, check_box)

print(use_cols_titles)
print(use_cols)

# Open file and create 2D array from data
dataArray = np.genfromtxt(filename,
                          dtype=int,
                          delimiter=",",
                          skip_header=TITLE_ROW_NUM,
                          usecols = use_cols,
                          autostrip=True,
                          filling_values=0)

#print(np.info(dataArray))
print(dataArray)

def plotcsv(plot_data, legends, data_array, legends_2):
    """Create Two plots, and fills the top with selected data"""
    #top (general) plot
    plt.ion()
    figure = plt.figure()
    axes_1 = figure.add_subplot(211)
    axes_1.plot(plot_data)
    figure.set_size_inches(16,6)
    plt.grid()
    plt.autoscale(enable=True,
                  axis='both',
                  tight=True)
    plt.ylabel('Magnetic field [LSB]',backgroundcolor='white')
    plt.legend(legends,
               loc=1,
               bbox_to_anchor=(1.085,1))

    #bottem (specialty) plot
    axes_2 = figure.add_subplot(212)
    line_2 = axes_2.plot(data_array)
    figure.set_size_inches(16,6)
    plt.grid()

    plt.autoscale(enable=True,
                  axis='both',
                  tight=True)
    plt.ylabel('Magnetic field [LSB]',backgroundcolor='white')

    axes_2.legend((line_2[0],),
            (legends_2,),
            loc=1,
            bbox_to_anchor=(1.085,1))
    plt.pause(0.1)
    return line_2, figure

def get_array(data_array, _col):
    """Wrapper for selecting col from dataArray to prevent IndexError"""
    if len(dataArray.shape) > 1:
        return data_array[:,_col]
    return data_array

# Initalise the plot
ln2, fig = plotcsv(dataArray,
                   use_cols_titles,
                   get_array(dataArray, -1),
                   use_cols_titles[-1])

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

#pylint: disable=too-many-arguments
def update_graph(lines, figure, data_array, _use_cols_titles, x_data=None, xlab=None, ylab=None):
    """Update bottem graph with new array"""
    y_data = data_array

    x_data, y_data, xlab, ylab = fourier(data_array)

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
    plt.pause(0.1)
    graph_menu.lift()
#pylint: enable-msg=too-many-arguments

def lift_window():
    """lifts the window"""
    print("lift")
    graph_menu.lift()
# dynamically make menue of lines to switch bottem graph to

#pylint: disable=invalid-name
_column = 0
graph_menu = tk.Toplevel()
threading.Timer(1,lift_window).start()
for _column, title in enumerate(use_cols_titles):
    tk.Button(graph_menu,
              text=title,
              command=partial(update_graph,
              ln2,
              fig,
              get_array(dataArray,_column),
              title)
              ).grid(row=_column,
                    sticky=tk.W,
                    pady=4)

tk.Button(graph_menu,
          text="quit",
          command=graph_menu.quit
          ).grid(row=_column+1,
                 sticky=tk.W,
                 pady=4)

tk.mainloop()

#timer.cancel()
graph_menu.destroy()
#pylint: enable-msg=invalid-name
