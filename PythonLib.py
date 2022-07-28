# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 19:08:17 2022

@author: Esan
"""

import numpy as np
import pandas as pd

from scipy import stats as st
from scipy import signal as sg

import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
import mplcursors as mpl

import ruptures as rpt

#%%
def data_transfer_force():
    filename_force = filedialog.askopenfilename(initialdir='Z:/ThesesMaster/Sundaralingam Esan/050__Messdaten/Messungen/', 
                                                title='File Open Kraftmessung; Bitte die .txt Datei auswählen')
    data_force = pd.read_csv(filename_force,
                             sep=';',
                             dtype=float)
    
    # repeats = int(filename_force.split('_')[-1].split('x')[0])
    # bkps = 4 * repeats
    
    return data_force

def data_transfer_smu():
    filename_res = filedialog.askopenfilename(initialdir='Z:/ThesesMaster/Sundaralingam Esan/050__Messdaten/Messungen/',  
                                              title='File Open Widerstandsmessung; Bitte die .csv Datei auswählen')
    data_smu = pd.read_csv(filename_res,
                           sep=',',
                           dtype={'Widerstand [Ohm]': np.single})

    
    return data_smu

def data_transfer_ref():
    filename_ref = filedialog.askopenfilename(initialdir='Z:/ThesesMaster/Sundaralingam Esan/050__Messdaten/Messungen/', 
                                              title='File Open Referenzmessung; Bitte die .txt Datei auswählen')  
    data_ref = pd.read_csv(filename_ref,
                           sep=';',
                           dtype=float)
    
    return data_ref
    
#%%
def export_smu_t(data_smu):
    data_smu['Zeit [Datum+T+Zeit]'] = pd.to_datetime(data_smu['Zeit [Datum+T+Zeit]'])
    firstValue = data_smu['Zeit [Datum+T+Zeit]'].iloc[0]
    data_smu['Zeit [Datum+T+Zeit]'] = data_smu['Zeit [Datum+T+Zeit]'] - firstValue
    
    t_r = np.array(np.ones(len(data_smu['Zeit [Datum+T+Zeit]'])))
    for i in range(len(data_smu['Zeit [Datum+T+Zeit]'])):
        t_r[i] = data_smu['Zeit [Datum+T+Zeit]'][i].total_seconds()
    
    return t_r

def export_smu_R(data_smu):    
    R   = np.array(data_smu['Widerstand [Ohm]'], dtype= np.single)
    
    return R

def export_force_t(data_force):
    t_F = np.array(data_force['Zeit_s'], dtype= float)
    
    return t_F

def export_force_F(data_force):
    F = np.array(data_force['Kraft_N'], dtype= float)
    
    return F

def export_force_s(data_force):
    s = np.array(data_force['Weg_mm'], dtype= float)
    
    return s

#%%
def compute_time_diff_one(t_r, r, tensile):
    
    if tensile == True:
        r_time = t_r[t_r <= 50]
        r_time = r_time[100:len(r_time)]
        r_value = r[t_r <=50]
        r_value = r_value[100:len(r_value)]
    elif tensile == False:
        r_time = t_r[t_r <= 31]
        r_time = r_time[100:len(r_time)]
        r_value = r[t_r <= 31]
        r_value = r_value[100:len(r_value)]
        
    b, a = sg.butter(3, 0.05, 'lowpass')
    filtered_dr = sg.filtfilt(b, a, np.gradient(r_value, r_time))
    
    result = rpt.Pelt(model='l2').fit_predict(filtered_dr, 0.0015)
    
    rpt.display(filtered_dr, result)
    
    return result

def compute_time_diff(t_F, F, t_r, r, tensile):
    result = compute_time_diff_one(t_r, r, tensile)
    result2 = compute_time_diff_one(t_F, F, tensile)
    
    r_time = t_r[t_r <= 50]
    r_time = r_time[100:len(r_time)]
    r_value = r[t_r <=50]
    r_value = r_value[100:len(r_value)]
    
    f_time = t_F[t_F <= 50]
    f_time = f_time[100:len(f_time)]
    f_value = F[t_F <= 50]
    f_value = f_value[100:len(f_value)]
    
    diff = f_time[result2[0]] - r_time[result[0]]
    
    return diff, f_time[result2[0]]

def compute_gradient(t_F, F, t_r, r):
    
    r_max = []
    for i in range(len(r)):
        if r[i] == max(r):
            r_max.append(i)
    
    b, a = sg.butter(3, 0.05, 'lowpass')
    filtered_dr = sg.filtfilt(b, a, np.gradient(r[:r_max[0]-1], t_r[:r_max[0]-1]))
    
    b, a = sg.butter(3, 0.01, 'lowpass')
    filtered_dF = sg.filtfilt(b, a, np.gradient(F, t_F))
    
    return [[filtered_dF], [filtered_dr]]
    
def compute_force_lin_err(t_F, F, s, bkps):
    b,a = sg.butter(3, 0.01, 'lowpass')
    filtered_dF = sg.filtfilt(b, a, np.gradient(F, t_F))
    algo = rpt.BottomUp(model='l2').fit(filtered_dF)
    result = algo.predict(bkps)
    
    x_s, y_force, reg = [], [], []
    
    for i in range(0,bkps,2):
        x_s.append(s[result[i]:result[i+1]])
        y_force.append(F[result[i]:result[i+1]])
        reg.append(st.linregress(x_s[-1], y_force[-1]))
    
    lin_fit = []
    lin_err = []
    
    for i in range(len(reg)):
        lin_fit.append(reg[i].intercept + reg[i].slope * x_s[i])
        temp = (y_force[i] - (reg[i].intercept + reg[i].slope * x_s[i])) / (y_force[i][-1] - y_force[i][0]) * 100
        lin_err.append(temp)
    
    return [[x_s], [y_force], [lin_fit], [lin_err]]
    
def compute_res_lin_err(data_smu, t_r, R, t_F, F, bkps):
    b,a = sg.butter(3, 0.01, 'lowpass')
    filtered_dF = sg.filtfilt(b, a, np.gradient(F, t_F))
    algo = rpt.BottomUp(model='l2').fit(filtered_dF)
    result = algo.predict(bkps)
    
    f_time, f_value = [], []
    reg_tF, reg_rF, lin_fit = [], [], []
    r_min, r_max = [], []
    r_time, r_value = [], []
    x_t, x_f = [], []
    lin_err = []
    
    for i in range(0, bkps, 2):
        f_time.append(t_F[result[i]:result[i+1]])
        f_value.append(F[result[i]:result[i+1]])
        r_min.append(data_smu[t_r >= t_F[result[i]]].index)
        r_max.append(data_smu[t_r >= t_F[result[i+1]]].index)
    
    for i in range(len(r_min)):
        r_time.append(t_r[r_min[i][0]:r_max[i][0]])
        r_value.append(R[r_min[i][0]:r_max[i][0]])
        
    for i in range(len(f_time)):
        reg_tF.append(st.linregress(f_time[i], f_value[i]))
        x_t.append(np.linspace(f_time[i][0], f_time[i][len(f_time[i])-1],
                             num= r_max[i][0]-r_min[i][0]))
        
    for i in range(len(f_time)):
        x_f.append(reg_tF[i].intercept + reg_tF[i].slope * x_t[i])
        reg_rF.append(st.linregress(x_f[-1], r_value[i]))
    
    for i in range(len(reg_rF)):
        lin_fit.append(reg_rF[i].intercept + reg_rF[i].slope * x_f[i])
        temp = (r_value[i] - (reg_rF[i].intercept + reg_rF[i].slope * x_f[i]))/(r_value[i][-1] - r_value[i][0]) *100
        lin_err.append(temp)
    
    return [[x_f], [r_value], [lin_fit], [lin_err]]

def compute_strain_res(l_0, A_0, t_r, R, s, F, data, tensile):
    stress = F / A_0
    strain = s/l_0 * 100
    sg.resample(R, len(s))
    result = compute_time_diff_one(data, t_r, R, tensile)
    

#%%

def plot_force(t_F, F, s, t_F_ref, F_ref, s_ref):
    fig, ax = plt.subplot_mosaic([[0,2],[1,2]])
    fig.set_tight_layout(True)
    
    ax[0].set_xlabel('Zeit [s]')
    ax[0].set_ylabel('Kraft [N]', color= 'tab:red')
    ax[0].plot(t_F, F, label= 'Kraftmessung')
    ax[0].plot(t_F_ref, F_ref, color='black', label= 'Referenz')
    ax[0].legend()
    
    ax[1].set_xlabel('Zeit [s]')
    ax[1].set_ylabel('Weg [mm]')
    ax[1].plot(t_F, s, label= 'Wegmessung')
    ax[1].plot(t_F_ref, s_ref, color='black', label= 'Referenz')
    ax[1].legend()
    
    ax[2].set_xlabel('Weg [mm]')
    ax[2].set_ylabel('Kraft [N]')
    ax[2].plot(s, F, label= 'Messung')
    ax[2].plot(s_ref, F_ref, color='black', label= 'Referenz')
    ax[2].legend()
    
    plt.show()
    
def plot_res_and_force(t_r, r_d, t_F, F, s, t_F_ref, F_ref, s_ref, y_achse, res_label, ref_label, sensor): 
    
    r_max = []
    for i in range(len(r_d)):
        if r_d[i] == max(r_d):
            r_max.append(i)
    
    fig, ax = plt.subplot_mosaic([[0],[1]])
    fig.set_tight_layout(True)
    ax[0].set_xlabel('Zeit [s]')
    ax[0].set_ylabel('Kraft [N]', color = 'tab:red')
    ax[0].tick_params(axis= 'y', labelcolor= 'tab:red')
    ax[0].plot(t_F, F, color= 'tab:red', label= 'Kraft Prüfmaschine')
    ax[0].legend(bbox_to_anchor =(0,1.1), loc= 'upper left')
    
    ax2 = ax[0].twinx()
    ax2.set_ylabel(y_achse,
                   color= 'tab:blue')
    ax2.tick_params(axis= 'y', labelcolor= 'tab:blue')
    ax2.set_ylim(None, r_d[r_max[0]-1], auto= sensor)
    ax2.plot(t_r, r_d, color= 'tab:blue', label= res_label)
    ax2.legend(bbox_to_anchor =(1,1.1), loc= 'upper right')
    
    ax[1].set_xlabel('Zeit [s]')
    ax[1].set_ylabel('Weg [mm]', color = 'tab:red')
    ax[1].tick_params(axis= 'y', labelcolor= 'tab:red')
    ax[1].plot(t_F, s, color= 'tab:red', label= 'Weg Prüfmaschine')
    ax[1].legend(bbox_to_anchor =(0,1.1), loc= 'upper left')

    ax3 = ax[1].twinx()
    ax3.set_ylabel(y_achse,
                   color= 'tab:blue')
    ax3.tick_params(axis= 'y', labelcolor= 'tab:blue')
    ax3.set_ylim(None, r_d[r_max[0]-1], auto= sensor)
    ax3.plot(t_r, r_d, color= 'tab:blue', label= res_label)
    ax3.legend(bbox_to_anchor =(1,1.1), loc= 'upper right')
    
    fig, ax = plt.subplots()
    ax.set_xlabel('Weg [mm]')
    ax.set_ylabel('Kraft [N]')
    ax.plot(s, F, label= 'Messung', color= 'tab:red')
    ax.plot(s_ref, F_ref, label= 'Referenz: '+ ref_label, color= 'black')
    ax.legend()
    mpl.cursor(hover=True)
    
    # plt.savefig("res_force_plot.svg", dpi=300.0, orientation='landscape', papertype='a4')
    
    plt.show()
    
    
def plot_gradient(t_F, dF, t_r, dr):
    
    r_max = []
    for i in range(len(dr)):
        if dr[i] == max(dr):
            r_max.append(i)
    
    fig, ax = plt.subplots()
    ax.set_xlabel('Zeit [s]')
    ax.set_ylabel('Steigung der Kraft [N/s]', color = 'tab:red')
    ax.plot(t_F, dF, color= 'tab:red', label= 'Kraftmessung')
    ax.tick_params(axis='y', labelcolor= 'tab:red')
    ax.legend(loc='upper left')

    ax2 = ax.twinx()
    ax2.set_ylabel('Steigung der Widerstands [Ohm/s]', color= 'tab:blue')
    ax2.plot(t_r[:r_max[0]], dr[:r_max[0]], color= 'tab:blue', label= 'widerstandsmessung')
    ax2.tick_params(axis='y', labelcolor= 'tab:blue')
    ax2.legend(loc= 'upper right')

def plot_force_lin_err(x_s, y_force, lin_fit, lin_err):
    fig, ax = plt.subplot_mosaic([[0,1],[2,3]])
    fig.set_tight_layout(True)
    ax[0].set_xlabel('Weg [mm]')
    ax[0].set_ylabel('Kraft [N]')

    ax[1].set_xlabel('Weg [mm]')
    ax[1].set_ylabel('Kraft [N]')

    ax[2].set_xlabel('Weg [mm]')
    ax[2].set_ylabel('Linearisierungsfehler [%]')

    ax[3].set_xlabel('Weg [mm]')
    ax[3].set_ylabel('Linearisierungsfehler [%]')
    
    j, k = 1, 1
    for i in range(len(x_s)):
        if i%2 == 0:
            ax[0].plot(x_s[i], y_force[i], label= 'Steiung '+ str(j) + ' der Kraft [N]')
            ax[0].plot(x_s[i], lin_fit[i], '--', label= 'fitted Steigung ' + str(j) + ' der Kraft [N]')
            ax[2].plot(x_s[i], lin_err[i], label= 'Fehler der Steigung ' + str(j) + ' [%]')
            j += 1
        else:
            ax[1].plot(x_s[i], y_force[i], label= 'Abfall' + str(k) + ' der Kraft [N]')
            ax[1].plot(x_s[i], lin_fit[i], '--', label= 'fitted Abfall ' + str(k) + ' der Kraft [N]')
            ax[3].plot(x_s[i], lin_err[i], label= 'Fehler des Abfalls ' + str(k) + ' [%]')
            k += 1
            
    ax[0].legend()
    ax[1].legend()
    ax[2].legend()
    ax[3].legend()
    # mpl.cursor(hover=True)
    plt.show()

def plot_res_lin_err(x_f, r_value, lin_fit, lin_err):
    fig, ax = plt.subplot_mosaic([[0,1],[2,3]])
    fig.set_tight_layout(True)
    ax[0].set_xlabel('Kraft [N]')
    ax[0].set_ylabel('Widerstand [Ohm]')

    ax[1].set_xlabel('Kraft [N]')
    ax[1].set_ylabel('Widerstand [Ohm]')
    ax[1].invert_xaxis()

    ax[2].set_xlabel('Kraft [N]')
    ax[2].set_ylabel('Linearisierungsfehler [%] normiert auf den Messbereich')

    ax[3].set_xlabel('Kraft [N]')
    ax[3].set_ylabel('Linearisierungsfehler [%] normiert auf den Messbereich')
    ax[3].invert_xaxis()
    
    j, k = 1, 1
    for i in range(len(x_f)):
        if i%2 == 0:
            ax[0].plot(x_f[i], r_value[i], label= 'Steiung ' + str(j) + ' des Widerstands [N]')
            ax[0].plot(x_f[i], lin_fit[i], '--', label= 'fitted Steigung ' + str(j) + ' des Widerstands [N]')
            ax[2].plot(x_f[i], lin_err[i], label= 'Fehler der Steigung ' + str(j) + ' [%]')
            j += 1
        else:
            ax[1].plot(x_f[i], r_value[i], label= 'Abfall ' + str(k) + ' des Widerstands [Ohm]')
            ax[1].plot(x_f[i], lin_fit[i], '--', label= 'fitted Abfall ' + str(k) + ' des Widerstands [Ohm]')
            ax[3].plot(x_f[i], lin_err[i], label= 'Fehler des Abfalls ' + str(k) + ' [%]')
            k += 1
            
    ax[0].legend()
    ax[1].legend()
    ax[2].legend()
    ax[3].legend()
    mpl.cursor(hover=True)
    plt.show()

    
    
    
        