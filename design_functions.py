import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from PIL import Image, ImageTk
import serial
import serial.tools.list_ports

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation


def set_image(self,image,x,y,x_resize,y_resize):

    image_logo = Image.open(image)
    image_logo = image_logo.resize((x_resize,y_resize),Image.ANTIALIAS)
    test = ImageTk.PhotoImage(image_logo)
    label_image = tk.Label(self,image=test)
    label_image.image = test
    label_image.place(x= x,y = y)

def find_port(interval_labelframe, name,func,var):
    board_1_port = ttk.Menubutton(interval_labelframe, text=name, style='secondary.Outline.TMenubutton')
    com_button = tk.Menu(board_1_port)

    com_list = [comport.device for comport in serial.tools.list_ports.comports()]
    val = 0

    var = tk.IntVar()
    for Variable in com_list:

        com_button.add_radiobutton(label=Variable, value=val, variable=var, command =lambda: func())
        val = val+1

    board_1_port['menu']=com_button

    return board_1_port, var

def data_plot(graph_frame,dpi,f,a,canvas):



    f = Figure(figsize=(10,4), dpi=dpi)


    a = f.add_subplot(121)


    a.set_title('Measurement of the Charge')
    a.set_xlabel('Number of aquired Data')
    a.set_ylabel('Charge Q')
    a.yaxis.label.set_color('red')




    canvas = FigureCanvasTkAgg(f, graph_frame)
    canvas.get_tk_widget().pack(side = tk.TOP, expand= False,pady=0, padx=0)

    return f, a, canvas

def data_plot_resistance(title, ylabel, graph_frame, dpi, f = None, a= None, canvas=None):



    f = Figure(figsize=(10,4), dpi=dpi)


    a = f.add_subplot(121)


    a.set_title('Measurement of' + " " + title)
    a.set_xlabel('Number of aquired Data')
    a.set_ylabel(ylabel)
    a.yaxis.label.set_color('red')




    canvas = FigureCanvasTkAgg(f, graph_frame)
    canvas.get_tk_widget().pack(side = tk.TOP, expand= False,pady=0, padx=0)

    return f, a, canvas

def temp_plot(graph_frame,dpi,f=None,a=None,canvas=None):



    f = Figure(figsize=(10,4), dpi=dpi)


    a = f.add_subplot(121)


    a.set_title('Digital Output of the Arduino')
    a.set_xlabel('Number of aquired Data')
    a.set_ylabel('Voltage output (V)')
    a.yaxis.label.set_color('red')




    canvas = FigureCanvasTkAgg(f, graph_frame)
    canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand= True,pady=0, padx=0)

    return f, a, canvas

def plot(f,a,canvas,data):

    a.plot(data,'r')

    canvas.draw()

def plot_temp(f,a,canvas,data):
    a.plot(data,'r')
    canvas.draw()

def plot_temp_clear(f,a,canvas):
    f.clf()

    """a.cla()
    a.set_xlabel('Number of aquired Data')
    a.set_ylabel('Temperature')
    a.yaxis.label.set_color('red')"""
    canvas.draw()

def plot_clear(f,a,canvas,a1):

    f.clf()
    """a.clear()
    a1.clear()

    a1=a.twinx()


    a.set_xlabel('Number of aquired Data')
    a.set_ylabel('Impedance Re')
    a.yaxis.label.set_color('red')
    a1.yaxis.label.set_color('green')
    a1.set_ylabel('Impedance Im')"""


    canvas.draw()



def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False
