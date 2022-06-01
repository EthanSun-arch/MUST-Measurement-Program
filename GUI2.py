import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import ttkbootstrap
from tkinter import *
from design_functions import *

import serial as sr
import serial.tools.list_ports
import threading
from datetime import datetime

import pyvisa as visa
from pyvisa.highlevel import ResourceManager
import numpy as np
import time
from time import sleep

global cond, cond_all , cond_res, cond_lad

class Main_page(tk.Tk):
    """This class is responsible for the main settings of the software"""

    def __init__(self, *args, **kwargs):
        global sensor
        super().__init__()

        """Settings of the GUI-basics: geometry, title"""
        self.title('Sourcemeter und Elektrometer Messung')
        self.style = Style('darkly')
        self.geometry('1300x700') 


        """Set a frame that contains the different classes of the software (Pages)"""
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage,PlotPage):
            """
            PlotPage: Sourcemeter + demnächst Electrometer
            """

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        """responsible for the navigation between the different pages of the GUI
        Args:
            cont: the class that has to be shown
        """
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    """Represents the first page (Start page) of the GUI"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text= "Sourcemeter and Electrometer Controller")
        label.pack(pady=10,padx=10)

        # """Set the Hcp-Sensor logo"""
        # #set_image(self,"tu.jpg",300,150,600,200)
        # set_image(self,"part1.jpg",600,150,300,300)
        # set_image(self,"arduino.jpeg",240,150,250,250)

        """Implementation of buttonn"""
        start_button = ttk.Button(self, text= "Messung",
                                  style= "Outline.TButton", 
                                  command=lambda: controller.show_frame(PlotPage))
        start_button.place(x = 610, y = 350)

class PlotPage(tk.Frame):
    """Represents the first page (Start page) of the GUI"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        global cond, cond_all, cond_lad, cond_res
        cond = False
        cond_all = False
        cond_lad = False
        cond_res = False


        """Connect Frame Keiythely 6517A & 2450 """
        connect_Frame = ttk.LabelFrame(self, text= "Connecting Devices" , padding=(4,4,5,5))
        connect_Frame.pack(expand=True)
        connect_Frame.place(x=20,y=30)
        
        "Connect Frame Keithley 6517A"
        connect_lad_button = ttk.Button(connect_Frame, text= "Keithley 6517A", 
                                        style='Outline.TButton', 
                                        command=lambda: connect_to_lad())
        connect_lad_button.grid(row=0, column=0, padx=4, pady=2)
        
        # setting_labelframe = ttk.Labelframe(self, text='Keiythely 6517A', padding=(4, 4, 5, 5))
        # setting_labelframe.pack(expand = True)
        # setting_labelframe.place(x=20,y=30)

        
        # connect_button = ttk.Button(setting_labelframe, text="Connect", 
        #                             style='Outline.TButton',command=lambda: connect_to_lad())
        # connect_button.grid(row=0, column=1, sticky='ew', padx=4, pady=2)
        
        """Connect Frame Sourcemeter 2450"""
        connect_res_button = ttk.Button(connect_Frame, text= "SMU 2450", 
                                        style='Outline.TButton', 
                                        command=lambda: connect_to_res())
        connect_res_button.grid(row=0, column=1, padx=4, pady=2)
        
        
        # setting_labelframe = ttk.Labelframe(self, text='SMU2450', padding=(4, 4, 5, 5))
        # setting_labelframe.pack(expand = True)
        # setting_labelframe.place(x=120,y=30)

        
        # connect_button = ttk.Button(setting_labelframe, text="Connect", 
        #                             style='Outline.TButton',command=lambda: connect_to_res())
        # connect_button.grid(row=0, column=1, sticky='ew', padx=4, pady=2)
        
        """Connect Frame SMU and Electrometer"""
        connect_all_button = ttk.Button(connect_Frame, text= "Keithley 6517A and SMU 2450", 
                                        #bootstyle = DARK,
                                        style='Outline.TButton', 
                                        command=lambda: connect_to_all())
        connect_all_button.grid(row=0, column=2, padx=4, pady=2)
             


        """Measurement Frame with Timespan and Stop condition"""
        Start_Stop_Frame = ttk.Labelframe(self, text='Measurement', padding=(4, 4, 5, 5))
        Start_Stop_Frame.pack(expand = True)
        Start_Stop_Frame.place(x=20,y=100)

        timespan_label = ttk.Label(Start_Stop_Frame, text= "Timespan in seconds", style="BW.TLabel")
        timespan_label.grid(row=0, column=0, sticky='ew', padx=4, pady=2)

        timespan_entry = ttk.Entry(Start_Stop_Frame)
        timespan_entry.grid(row=1, column=0, sticky='ew', padx=4, pady=2)

        start_button = ttk.Button(Start_Stop_Frame, text="Start", 
                                  style='Outline.TButton', command=lambda: plot_start())
        start_button.grid(row=2, column=0, sticky='ew', padx=4, pady=2)

        stop_button = ttk.Button(Start_Stop_Frame, text="Stop(without Timespan)", 
                                 style='Outline.TButton', command=lambda: plot_stop())
        stop_button.grid(row=3, column=0, sticky='ew', padx=4, pady=2)

        """Save Frame"""
        save_frame =  ttk.Labelframe(self, text='Save Settings', padding=(4, 4, 5, 5))
        save_frame.pack(expand=True)
        save_frame.place(x=20,y=250)

        setting_file_label = ttk.Label(save_frame, text= "Filename", style="BW.TLabel")
        setting_file_label.grid(row=0, column=0, sticky='ew', padx=4, pady=2)

        setting_file_entry = ttk.Entry(save_frame)
        setting_file_entry.grid(row=1, column=0, sticky='ew', padx=4, pady=2)

        save_button = ttk.Button(save_frame, text= "Save everything in one", 
                                 style='Outline.TButton',command=lambda: save_data_all())
        save_button.grid(row=2, column=0, sticky='ew', padx=4, pady=2)
        
        save_button_res = ttk.Button(save_frame, text= "Save only Resistance", 
                                 style='Outline.TButton',command=lambda: save_data_res())
        save_button_res.grid(row=3, column=0, sticky='ew', padx=4, pady=2)
        
        save_button_lad = ttk.Button(save_frame, text= "Save only Charge", 
                                 style='Outline.TButton',command=lambda: save_data_lad())
        save_button_lad.grid(row=4, column=0, sticky='ew', padx=4, pady=2)
        
        
        """Settings for the Electrometer"""
        setting_labelframe_electrometer = ttk.Labelframe(self, text= "Keiythely 6517A", 
                                                         padding=(4, 4, 5, 5))
        setting_labelframe_electrometer.pack(expand = True)
        setting_labelframe_electrometer.place(x=1130,y=550)

        zero_check_button = ttk.Button(setting_labelframe_electrometer, text= "Zero-check", 
                                       style='Outline.TButton',command=lambda: Zero_check())
        zero_check_button.grid(row=0, column=0, sticky='ew', padx=4, pady=2)


        reset_electrometer_button = ttk.Button(setting_labelframe_electrometer, text= "Reset", 
                                               style='Outline.TButton', 
                                               command=lambda: reset_electrometer())
        reset_electrometer_button.grid(row=1, column=0, sticky='ew', padx=4, pady=2)
        
        """Settings for the Sourcemeter"""
        setting_labelframe_sourcemeter = ttk.Labelframe(self, text= "Keiythely 2450", 
                                                        padding=(4, 4, 5, 5))
        setting_labelframe_sourcemeter.pack(expand = True)
        setting_labelframe_sourcemeter.place(x=825,y=550)

        on_button = ttk.Button(setting_labelframe_sourcemeter, text= "Output ON", 
                               style='Outline.TButton',command=lambda: output_on())
        on_button.grid(row=0, column=0, sticky='ew', padx=4, pady=2)
        
        off_button = ttk.Button(setting_labelframe_sourcemeter, text= "Output OFF", 
                                style='Outline.TButton',command=lambda: output_off())
        off_button.grid(row=1, column=0, sticky='ew', padx=4, pady=2)

        reset_sourcemeter_button = ttk.Button(setting_labelframe_sourcemeter, text= "Reset", 
                                              style='Outline.TButton',
                                              command=lambda: reset_sourcemeter())
        reset_sourcemeter_button.grid(row=2, column=0, sticky='ew', padx=4, pady=2)
        
        voltage_mode_button = ttk.Button(setting_labelframe_sourcemeter, text= "Measure Voltage",
                                         style='Outline.TButton',command=lambda: voltage_mode())
        voltage_mode_button.grid(row=0, column =1, sticky='ew',padx=4,pady=2)    
    
        current_mode_button = ttk.Button(setting_labelframe_sourcemeter, text= "Measure Current",
                                         style='Outline.TButton',command=lambda: current_mode())
        current_mode_button.grid(row=1, column =1, sticky='ew',padx=4,pady=2)
        
        resistance_2wire_mode_button = ttk.Button(setting_labelframe_sourcemeter, 
                                                  text= "Measure Resistance 2-Wire", 
                                                  style='Outline.TButton', 
                                                  command=lambda: resistance_2wire_mode())
        resistance_2wire_mode_button.grid(row=2, column = 1,sticky='ew',padx=4,pady=2)
        
        resistance_4wire_mode_button = ttk.Button(setting_labelframe_sourcemeter, 
                                                  text= "Measure Resistance 4-Wire", 
                                                  style='Outline.TButton', 
                                                  command=lambda: resistance_4wire_mode())
        resistance_4wire_mode_button.grid(row=3, column = 1,sticky='ew',padx=4,pady=2)
        
        """Global settings """
        zero_check_button = ttk.Button(self, text= "Clear Plot", 
                                       style="Outline.TButton", 
                                       command=lambda: clear_plot())
        zero_check_button.place(x=1140, y=50)

        global status_label
        status_label = ttk.Label(self,text="Status: ", 
                                 style="BW.TLabel",font=("Arial", 15))
        status_label.place(x= 800,y =10)



        global rm, inst, rmu_smu, inst_smu, state, title, ylabel
        
        state = 4
        title = "Resistance"
        ylabel = "Resistance R"


        def connect_to_electrometer():
            global rm, inst
            """Connect to arduino and Electrometer"""
            rm = ResourceManager()
            print (rm.list_resources())  #List the resources visible to pyVISA
            inst = rm.open_resource("USB0::0x0957::0xD618::MY54320227::INSTR")  #Enter Serial port here
            inst.timeout = 9600  #increased timeout from default of 2000
            sleep(1)
            inf = inst.query("*IDN?")

            """Set Electrometer Settings"""

            inst.write(':sense:function "char"')
            inst.write(':conf:char')
            inst.write(':SYSTem:ZCHeck off')

            info_label = ttk.Label(self,text=f"Electrometer: {inf}", 
                                   style="BW.TLabel",font=("Arial", 10))
            info_label.place(x = 10, y = 630)
        
        def connect_to_smu():
            global rm_smu, inst_smu
            rmu_smu = ResourceManager()
            #print (rmu_smu.list_resources())
            inst_smu = rmu_smu.open_resource("USB0::0x05E6::0x2450::04079798::INSTR")  #Enter Serial port here
            inst_smu.timeout = 9600  #increased timeout from default of 2000
            sleep(1)
            inf = inst_smu.query("*IDN?")
            print(inf)


            info_label = ttk.Label(self,text=f"Soucemeter: {inf}", 
                                   style="BW.TLabel",font=("Arial", 10))
            info_label.place(x = 10, y = 660)

        def connect_to_lad():
            global cond_lad
            cond_lad = True
            connect_to_electrometer()
            #connect_to_smu()

            global status_label
            status_label = ttk.Label(self,text="Status: Connected to 6517A", 
                                     style="BW.TLabel", font=("Arial", 15))
            status_label.place(x= 800,y =10)
            
        def connect_to_res():
            global cond_res
            cond_res = True
            #connect_to_electrometer()
            connect_to_smu()

            global status_label
            status_label = ttk.Label(self,text="Status: Connected to SMU2450", 
                                     style="BW.TLabel", font=("Arial", 15))
            status_label.place(x= 800,y =10)
            
        def connect_to_all():
            global cond_all
            cond_all = True
            connect_to_electrometer()
            connect_to_smu()

            global status_label
            status_label = ttk.Label(self,text="Status: Connected to SMU2450 & 6517A", 
                                     style="BW.TLabel", font=("Arial", 15))
            status_label.place(x= 800,y =10)
            
            
        """ Electrometer Settings """
        def Zero_check():
            """Activate the Zero-check command"""
            inst.write(':SYSTem:ZCHeck on')
            global status_label
            status_label = ttk.Label(self,text="Status: Zero-checked", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            inst.write(':SYSTem:ZCHeck off')
        
        def reset_electrometer():
            """Reset the Electrometer settings"""
            inst.write(':sense:function "char"')
            inst.write(':conf:char')
            inst.write(':SYSTem:ZCHeck off')
            global status_label
            status_label = ttk.Label(self,text="Status: Reset", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)

        """Sourcemeter Settings """
        def output_on():
            "Set the output of the Sourcemeter to ON"
            inst_smu.write(':OUTP ON')
            global status_label
            status_label = ttk.Label(self,text="Status: Output set",
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
        
        def output_off():
            "Set the output of the Sourcemeter to ON"
            inst_smu.write(':OUTP OFF')
            global status_label
            status_label = ttk.Label(self,text="Status: Output set  ON",
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            
        def reset_sourcemeter():
            "Reset the Sourcemeter"
            inst_smu.write('*RST')
            global status_label
            status_label = ttk.Label(self,text="Status: Sourcemeter resetted",
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            
        def voltage_mode():
            global state, title, ylabel
            "Set to voltage-measurment"
            inst_smu.write('MEAS:VOLT?')
            self.after(1, output_on)
            global status_label
            status_label = ttk.Label(self,text="Status: Set to Voltage Measurement", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            state = 0
            title = 'Voltage'
            ylabel = 'Voltage V'
            self.after(1,clear_plot)
            
        def current_mode():
            global state, title, ylabel
            "Set to current-measurement"
            inst_smu.write('MEAS:CURR?')
            self.after(1, output_on)
            global status_label
            status_label = ttk.Label(self,text="Status: Set to Current Measurement", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            state = 1
            title = 'Current'
            ylabel = 'Current A'
            self.after(1,clear_plot)
            
        def resistance_2wire_mode():
            global state, title, ylabel
            "Set to 2 Wire resistance mesurement"
            inst_smu.write('MEAS:RES?')
            inst_smu.write(':SENS:RES:RSEN OFF')
            self.after(1, output_on)
            global status_label
            status_label = ttk.Label(self,text="Status: Set to 2 Wire Resistance Measurement", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            state = 2
            title = 'Resistance'
            ylabel = 'Resistance R'
            self.after(1,clear_plot)
            
            
        def resistance_4wire_mode():
            global state, title, ylabel
            "Set to 4 Wire resistance mesurement"
            inst_smu.write('MEAS:RES?')
            inst_smu.write(':SENS:RES:RSEN ON')
            self.after(1, output_on)
            global status_label
            status_label = ttk.Label(self,text="Status: Set to 4 Wire Resistance Measurement", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            state = 3
            title = 'Resistance'
            ylabel = 'Resistance R'
            self.after(1,clear_plot)
        
        global timespan, start_timespan
        
        timespan = 0
        start_timespan = 0
        
        def plot_start():
            """Start of live measurement"""
            global cond, timespan, start_timespan
            print("start")
            cond = True
            if len(timespan_entry.get())>0:
                cond = False
                timespan = int(timespan_entry.get())
            else:
                timespan = 0
            start_timespan = time.time()

            global status_label
            status_label = ttk.Label(self,text="Status: Live measurement started", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
            self.after(1,plotting)

        def plot_stop():
            """Ends the live measurement"""
            global cond, start
            start = False
            cond = False

            global status_label
            status_label = ttk.Label(self,text= "Status: End of live measurement", 
                                     style= "BW.TLabel", font= ("Arial", 15))
            status_label.place(x= 800,y =10)
        
        
        """Saving Data Together and individually """
        global plot_lad, plot_res, plot_smu, plot_elec, plot_time
        
        plot_time = list()
        plot_lad = list()
        plot_res = list()

        def save_data_lad():
            """Save measured Data"""
            global plot_lad
            np.savetxt(setting_file_entry.get()+str(".csv"), 
                       np.transpose(np.array([plot_time,plot_lad])), 
                       delimiter= ",", fmt="%s")

            global status_label
            status_label = ttk.Label(self,text= "Status: Data Saved", 
                                     style="BW.TLabel", font=("Arial", 15))
            status_label.place(x= 800,y =10)
        
        def save_data_res():
            "Save measured Data from the SMU"
            global plot_res, state
            
            if state == 0:
                text = 'Spannung in Volt'
            elif state == 1:
                text = 'Strom in Ampere'
            elif state == 2 or state == 3:
                text = 'Widerstand in Ohm'
                
            np.savetxt(setting_file_entry.get()+str(".csv"), 
                       np.transpose(np.array([plot_time,plot_res])), 
                       delimiter= ",", fmt="%s",header= text)
            global status_label
            status_label = ttk.Label(self,text= "Status: Data Saved", 
                                     style="BW.TLabel", font=("Arial", 15))
            status_label.place(x= 800,y =10)
        
        def save_data_all():
            """Save the data"""
            global plot_lad, plot_res
            np.savetxt(setting_file_entry.get()+str(".csv"), 
                       np.transpose(np.array([plot_time, plot_lad, plot_res])), 
                       delimiter= ",", fmt="%s")

            global status_label
            status_label = ttk.Label(self,text="Status: Data Saved", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)

        def clear_plot():

            """Clear the electrometer plot"""
            global plot_elec, plot_lad
            global plot_smu, plot_res
            global title, ylabel, state
            global plot_time
            
            plot_frame_lad = ttk.Frame(self)
            plot_frame_lad.place(x=250,y=150)

            f_lad = None
            a_lad = None
            canvas_lad = None

            
            plot_elec = data_plot(plot_frame_lad, 90, f_lad, a_lad, canvas_lad)
            plot_lad = list()

            plot_frame_res = ttk.Frame(self)
            plot_frame_res.place(x=700,y=150)

            f_res = None
            a_res = None
            canvas_res = None
            
            if state == 0:
                plot_smu = data_plot_resistance(title, ylabel, plot_frame_res, 90, f_res, a_res, canvas_res)
            elif state == 1:
                plot_smu = data_plot_resistance(title, ylabel, plot_frame_res, 90, f_res, a_res, canvas_res)
            elif state == 2 or state == 3:
                plot_smu = data_plot_resistance(title, ylabel, plot_frame_res, 90, f_res, a_res, canvas_res)
            
            plot_res = list()
            
            plot_time = list()


            global status_label
            status_label = ttk.Label(self,text="Status: Plot cleared", 
                                     style="BW.TLabel",font=("Arial", 15))
            status_label.place(x= 800,y =10)
        
        
        def plotting():
            global cond, cond_all, cond_lad, cond_res
            global plot_smu, plot_elec, plot_lad, plot_res
            global start, timespan, start_timespan, data
            global plot_time
            
            """Plot the measured data"""

            if (cond == True or (time.time()-start_timespan)<timespan):
                if cond_lad == True:
                    
                    data_lad = inst.query(':READ?')
                    data_to_float_lad = split_data(data_lad)
                    plot_lad.append(data_to_float_lad)
                    plot_time.append(datetime.now().isoformat(timespec='microseconds'))
                    plot(plot_elec[0], plot_elec[1], plot_elec[2], plot_lad)
                    
                    self.after(1,plotting)
                    
                if cond_res == True:
                    data_res = inst_smu.query(':READ?')
                    data_to_float_res = split_data(data_res)
                    plot_res.append(data_to_float_res)
                    plot_time.append(datetime.now().isoformat(timespec='microseconds'))
                    plot(plot_smu[0], plot_smu[1], plot_smu[2], plot_res)
                    
                    self.after(1,plotting)
                    
                if cond_all == True:
                    data_res = inst.query(':READ?')
                    data_lad = inst_smu.query(':READ?')

                    data_to_float_res = split_data(data_res)
                    data_to_float_lad = split_data(data_lad)
                    plot_lad.append(data_to_float_lad)
                    plot_res.append(data_to_float_res)
                    plot_time.append(datetime.now().isoformat(timespec='microseconds'))

                    if len(plot_lad)%20 ==0:
                        plot(plot_smu[0], plot_smu[1], plot_smu[2], plot_res)
                        plot(plot_elec[0], plot_elec[1], plot_elec[2], plot_lad)

                    self.after(1,plotting)
                    
        
        
        plot_frame_lad = ttk.Frame(self)
        plot_frame_lad.place(x=250,y=150)

        f_lad=None
        a_lad=None
        canvas_lad=None

        plot_elec = data_plot(plot_frame_lad, 90, f_lad, a_lad, canvas_lad)

        plot_frame_res = ttk.Frame(self)
        plot_frame_res.place(x=700,y=150)

        f_res=None
        a_res=None
        canvas_res=None

        if state == 0:
            plot_smu = data_plot_resistance(title, ylabel, plot_frame_res, 90, f_res, a_res, canvas_res)
        elif state == 1:
            plot_smu = data_plot_resistance(title, ylabel, plot_frame_res, 90, f_res, a_res, canvas_res)
        elif state == 2 or state == 3:
            plot_smu = data_plot_resistance(title, ylabel, plot_frame_res, 90, f_res, a_res, canvas_res)
        else:
            plot_smu = data_plot_resistance(title, ylabel, plot_frame_res, 90, f_res, a_res, canvas_res)
        
    
        def split_data(data):
            x = data.split(',')
            i=1
            while i  <len(x[0]):
                if isfloat(x[0][i])==False and x[0][i] != '-' and x[0][i] != '.' and x[0][i] != 'E':
                    index = i
                    break
                i=i+1
            if data[0] == "+":
                return float(data[1:index+3])
            else:

                return float(data[0:index+3])


app = Main_page()
app.mainloop()
