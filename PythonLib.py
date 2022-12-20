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
from mpl_axes_aligner import align

import ruptures as rpt

plt.rc('font', size= 20)



#%%
def data_transfer_force():
    filename_force = filedialog.askopenfilename(initialdir='Z:/ThesesMaster/Sundaralingam Esan/050__Messdaten/Messungen/', 
                                                filetypes = (('txt files', '*.txt'), ('all files', '*.*')),
                                                title='File Open Kraftmessung; Bitte die .txt Datei auswählen')
    data_force = pd.read_csv(filename_force,
                             sep=';',
                             dtype=float)
    
    # repeats = int(filename_force.split('_')[-1].split('x')[0])
    # bkps = 4 * repeats
    
    return data_force

def data_transfer_smu():
    filename_res = filedialog.askopenfilename(initialdir='Z:/ThesesMaster/Sundaralingam Esan/050__Messdaten/Messungen/',  
                                              filetypes = (('csv files', '*.csv'), ('all files', '*.*')),
                                              title='File Open Widerstandsmessung; Bitte die .csv Datei auswählen')
    data_smu = pd.read_csv(filename_res,
                           sep=',',
                           dtype={'Widerstand [Ohm]': np.single})

    
    return data_smu

def data_transfer_ref():
    filename_ref = filedialog.askopenfilename(initialdir='Z:/ThesesMaster/Sundaralingam Esan/050__Messdaten/Messungen/', 
                                              filetypes = (('txt files', '*.txt'), ('all files', '*.*')),
                                              title='File Open Referenzmessung; Bitte die .txt Datei auswählen')  
    data_ref = pd.read_csv(filename_ref,
                           sep=';',
                           dtype=float)
    
    return data_ref

def data_transfer_bible():
    filename = filedialog.askopenfilename(initialdir='Z:/ThesesMaster/Sundaralingam Esan/050__Messdaten/Messungen/',
                                          filetypes = (('txt files', '*.txt'), ('all files', '*.*')),
                                          title= 'File Open Bible')
    
    data = pd.read_csv(filename,
                       sep=',',
                       dtype=float)
    
    return data
    
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
def compute_time_diff_res(time, data):        
    r_time_temp = time[time <= 34]
    r_time = r_time_temp
    r_time = r_time[r_time_temp >= 27.5]
    r_value = data[time <= 34]
    r_value = r_value[r_time_temp >= 27.5]
    
    r_mean_time_temp = time[time <= 29.5]
    r_mean_time = r_mean_time_temp
    r_mean_time = r_mean_time[r_mean_time_temp >= 27.5]
    r_mean_value = data[time <= 29.5]
    r_mean_value = r_mean_value[r_mean_time_temp >= 27.5]
        
    b, a = sg.butter(3, 0.1, 'lowpass')
    filtered_dr = sg.filtfilt(b, a, np.gradient(r_value, r_time))
    
    result_temp = rpt.Window(width=10 ,model='ar', jump=1).fit_predict(filtered_dr, 1)
    
    r_min = min(r_value)
    r_mean = np.mean(r_mean_value)
        
    for i in range(len(r_value)):
        if r_value[i] == r_min:
            result_temp1 = i
            
    for i in range(len(r_value)):
        if r_value[i] > r_mean + abs(r_mean)*0.05 or r_value[i] > r_mean - abs(r_mean)*0.05:
            result_temp2 = i
            break
        
    # if result_temp1 < 10:
    #     result = result_temp2
    # else:
    #     result = result_temp1
    
    result = result_temp2
    
    rpt.display(r_value, result_temp, [result])
    
    return result

def compute_time_diff_force(time, data):
    r_time_temp = time[time <= 34]
    r_time = r_time_temp
    r_time = r_time[r_time_temp >= 27.5]
    r_value = data[time <= 34]
    r_value = r_value[r_time_temp >= 27.5]
        
    b, a = sg.butter(3, 0.1, 'lowpass')
    filtered_dr = sg.filtfilt(b, a, np.gradient(r_value, r_time))
    
    result_temp = rpt.BottomUp(model='ar', jump=1).fit_predict(filtered_dr, 1)
    
    for i in range(len(r_time)):
        if r_time[i] == 30.4:
            result = i
            break
    
    rpt.display(r_value, result_temp, [result])
    
    return result

def compute_time_diff(t_F, F, t_r, r):
    result = compute_time_diff_res(t_r, r)
    result2 = compute_time_diff_force(t_F, F)

    r_time_temp = t_r[t_r <= 34]
    r_time = r_time_temp
    r_time = r_time[r_time_temp >= 27.5]
    r_value = r[t_r <= 34]
    r_value = r_value[r_time_temp >= 27.5]
    
    f_time_temp = t_F[t_F <= 34]
    f_time = f_time_temp
    f_time = f_time[f_time_temp >= 27.5]
    f_value = F[t_F <= 34]
    f_value = f_value[f_time_temp >= 27.5]    

    diff = f_time[result2] - r_time[result]
    
    return [diff, f_time[result2]]

#%%
def compute_strain_res(l_0, t_r, R, t_f, F, s):
    strain = s/l_0 * 100
    resampled_R = np.interp(t_f, t_r, R)
    
    for i in range(len(resampled_R)):
        if resampled_R[i] > 1.0e+6:
            index = i-1
            break
        # elif resampled_R[i] == max(resampled_R):
        #     index = i
        else:
            index = i
    
    resampled_R = resampled_R[0:index]
    strain = strain[0:index]
    F = F[0:index]
    
    reg_R = 0
    reg_F = 0
    
    return [strain, F, resampled_R, reg_F, reg_R]

def compute_res_max_strain(strain, F, R):
    
    strain_temp = strain[strain <= 1.9]
    x_strain = strain_temp
    x_strain = x_strain[strain_temp >= 1]
    res = R[strain <= 1.9]
    res = res[strain_temp >= 1]
    
    for i in range(len(res)):
        if res[i] == max(res):
            x_max = x_strain[i]
            y_max = res[i]
            
    for i in range(len(strain)):
        if strain[i] == x_max:
            temp_1 = strain[0:i]
            temp_2 = F[0:i]
            temp_3 = R[0:i]
            break
    
    return [x_max, y_max, temp_1, temp_2, temp_3]

def compute_strain_res_rmax(strain, F, resampled_R):
    
    strain_05_temp = strain
    resampled_R_05 = resampled_R
    F_05 = F
    
    reg_R_05 = st.linregress(strain_05_temp, resampled_R_05)
    # for i in range(len(strain_05_temp)):
    #     reg_R_05 = st.linregress(strain_05_temp[i:len(strain_05_temp)],resampled_R_05[i:len(strain_05_temp)])
    #     if reg_R_05.rvalue**2 >= 0.995:
    #         break
    reg_F_05 = st.linregress(strain_05_temp, F_05)
    
    return [strain_05_temp, F_05, resampled_R_05, reg_F_05, reg_R_05]

def compute_strain_res_100(strain, F, resampled_R):
    
    limit = 20
    
    resampled_R_temp = resampled_R[resampled_R < limit]
    F = F[resampled_R < limit]
    strain = strain[resampled_R < limit]
    
    reg_F = 0
    reg_R = 0
    
    return [strain, F, resampled_R_temp, reg_F, reg_R]

#%%
def plot(t, R):
    fig, ax = plt.subplots()
    ax.set_xlabel('Zeit [s]')
    ax.set_ylabel('Widerstand [Ohm]')
    ax.plot(t, R, label= 'Widerstandsänderung')
    ax.legend()
    mpl.cursor(hover=True)


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
    
def plot_res_and_force(t_r, r_d, t_F, F, s, t_F_ref, F_ref, s_ref, y_achse, res_label, ref_label): 
    fig, ax = plt.subplot_mosaic([[0],[1]])
    fig.set_tight_layout(True)
    
    ax[0].set_xlabel('Zeit [s]')
    ax[0].set_ylabel('Kraft [N]', color = 'tab:red')
    ax[0].tick_params(axis= 'y', labelcolor= 'tab:red')
    ax[0].set_ylim(bottom = -max(F)*0.1 , top= max(F) + max(F)*0.01)
    ax[0].plot(t_F, F, color= 'tab:red', label= 'Kraft Prüfmaschine')
    ax[0].legend(bbox_to_anchor =(0,1.1), loc= 'upper left')
    
    ax2 = ax[0].twinx()
    ax2.set_ylabel(y_achse,
                   color= 'tab:blue')
    ax2.tick_params(axis= 'y', labelcolor= 'tab:blue')
    ax2.plot(t_r, r_d, color= 'tab:blue', label= res_label)
    ax2.legend(bbox_to_anchor =(1,1.1), loc= 'upper right')
    
    align.yaxes(ax[0], 0, ax2, min(r_d))
    
    ax[1].set_xlabel('Zeit [s]')
    ax[1].set_ylabel('Weg [mm]', color = 'tab:red')
    ax[1].tick_params(axis= 'y', labelcolor= 'tab:red')
    ax[1].plot(t_F, s, color= 'tab:red', label= 'Weg Prüfmaschine')
    ax[1].legend(bbox_to_anchor =(0,1.1), loc= 'upper left')

    ax3 = ax[1].twinx()
    ax3.set_ylabel(y_achse,
                   color= 'tab:blue')
    ax3.tick_params(axis= 'y', labelcolor= 'tab:blue')
    ax3.plot(t_r, r_d, color= 'tab:blue', label= res_label)
    ax3.legend(bbox_to_anchor =(1,1.1), loc= 'upper right')
    
    align.yaxes(ax[1], 0, ax3, min(r_d))
    
    fig, ax = plt.subplots()
    ax.set_xlabel('Weg [mm]')
    ax.set_ylabel('Kraft [N]')
    ax.plot(s, F, label= 'Messung', color= 'tab:red')
    ax.plot(s_ref, F_ref, label= 'Referenz: '+ ref_label, color= 'black')
    ax.legend()
    
    mpl.cursor(hover=True)

def plot_strain_res(strain, F, resampled_r, reg_F, reg_R):
    fig, ax = plt.subplots()
    fig.set_tight_layout(True)
    
    ax.set_xlabel(r'$ \varepsilon (Strain) $ [%]')
    ax.set_ylabel('Kraft [N]')
    ax.plot(strain, F, label= 'Dehnung - Kraft', color= 'tab:red')
    if isinstance(reg_F, st._stats_mstats_common.LinregressResult):
       ax.plot(strain, reg_F.intercept + reg_F.slope * strain, 
               '--r', label= 'Lin-fit-F R^2= ' + str(round(reg_F.rvalue**2,6)))
    ax.legend(bbox_to_anchor =(0,1.1), loc= 'upper left')
    
    ax2 = ax.twinx()
    ax2.set_ylabel(r'$\Delta R/R_0 $ [%]', color= 'tab:blue')
    ax2.tick_params(axis= 'y', labelcolor= 'tab:blue')
    # ax2.set_ylim(bottom = -max(resampled_r)*0.1, top = max(resampled_r) + max(resampled_r)*0.1)
    ax2.plot(strain, resampled_r, label= 'Dehnung - Widerstand', color= 'tab:blue')
    if isinstance(reg_R, st._stats_mstats_common.LinregressResult):
       ax2.plot(strain, reg_R.intercept + reg_R.slope * strain, 
               '--b', label= 'Lin-fit-R R^2= ' + str(round(reg_R.rvalue**2,6)))
    ax2.legend(bbox_to_anchor =(1,1.1), loc= 'upper right')
    
    align.yaxes(ax, 0.0, ax2, min(resampled_r))
    mpl.cursor(hover=True)

def plot_bible(data, data_mean):
    fig, ax = plt.subplots()
    fig.set_tight_layout(True)
    
    ax.set_xlabel('Dicke [mm]')
    ax.set_ylabel(r'$ \varepsilon (Strain) $ [%]', color= 'tab:red')
    ax.scatter(data['Dicke'], data['Dehnung'], label= 'Dehnung-Dicke', color='tab:red')
    ax.errorbar(data_mean['Dicke'], 
                data_mean['MeanDehnung'], 
                yerr=data_mean['STDDehnung'], label= 'Mean Dehnung-Dicke', ls='--', color='r')
    ax.legend(bbox_to_anchor =(0,1.1), loc= 'upper left')
    
    ax2 = ax.twinx()
    ax2.set_ylabel(r'$\Delta R/R_0 $ [%]', color= 'tab:blue')
    ax2.scatter(data['Dicke'], data['Widerstandsänderung'], label= 'Widerstandsänderung-Dicke', color='tab:blue')
    ax2.errorbar(data_mean['Dicke'], 
                 data_mean['MeanWiderstand'], 
                 yerr=data_mean['STDWiderstand'], label= 'Mean Widerstandsänderung-Dicke', ls='--', color='b')
    ax2.legend(bbox_to_anchor =(1,1.1), loc= 'upper right')
    
    align.yaxes(ax, min(data['Dehnung']), ax2, min(data['Widerstandsänderung']))
    # mpl.cursor(hover=True)
    
    fig2, ax = plt.subplots()
    fig2.set_tight_layout(True)
    
    ax.set_xlabel('Dicke [mm]')
    ax.set_ylabel(r'$ \varepsilon (Strain) $ [%]', color= 'tab:red')
    ax.set_xlim(left=0.29, right=1.1)
    ax.scatter(data['Dicke'], data['Dehnung'], label= 'Dehnung-Dicke', color='tab:red')
    ax.errorbar(data_mean['Dicke'], 
                data_mean['MeanDehnung'], 
                yerr=data_mean['STDDehnung'], label= 'Mean Dehnung-Dicke', ls='--', color='r')
    ax.legend(bbox_to_anchor =(0,1.1), loc= 'upper left')
    
    fig3, ax2 = plt.subplots()
    fig3.set_tight_layout(True)
    ax2.set_xlabel('Dicke [mm]')
    ax2.set_ylabel(r'$\Delta R/R_0 $ [%]', color= 'tab:blue')
    ax2.set_xlim(left=0.29, right=1.1)
    ax2.scatter(data['Dicke'], data['Widerstandsänderung'], label= 'Widerstandsänderung-Dicke', color='tab:blue')
    ax2.errorbar(data_mean['Dicke'], 
                  data_mean['MeanWiderstand'], 
                  yerr=data_mean['STDWiderstand'], label= 'Mean Widerstandsänderung-Dicke', ls='--', color='b')
    ax2.legend(bbox_to_anchor =(1,1.1), loc= 'upper right')
    
    align.yaxes(ax, min(data['Dehnung']), ax2, min(data['Widerstandsänderung']))
    # mpl.cursor(hover=True)
#%%
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