# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 10:59:44 2022

@author: Esan
"""


import numpy as np
import pandas as pd
import datetime as date
import matplotlib.pyplot as plt
import mplcursors as mpl





#%%
"""Importing Data via Pandas"""
filename = '220602_Druck_Test2'

data_force = pd.read_csv('C:/Users/Esan/Documents/Masterarbeit/Messungen/'+ filename + '.txt',
                         sep= ';',
                         dtype= float,
                         index_col= 0)

data_smu = pd.read_csv('C:/Users/Esan/Documents/Masterarbeit/Messungen/'+ filename + '.csv',
                       dtype= {'Resistance': np.single},
                       sep= ',')

#%%
"""Adjusting the time into realtive values"""
data_smu = data_smu
data_smu['Time'] = pd.to_datetime(data_smu['Time'])
firstValue = data_smu['Time'].iloc[0]
data_smu['Time'] = data_smu['Time'] - firstValue

#%%
"""Importing the x and y data """
data_smu_t = np.array(np.ones(len(data_smu['Time'])))
for i in range(len(data_smu['Time'])):
    data_smu_t[i] = data_smu['Time'][i].total_seconds()
    
t=0.0
    
data_smu_t = data_smu_t + t
data_smu_R = np.array(data_smu['Resistance'], dtype= np.double)
max_R = max(data_smu_R)
data_smu_r = data_smu_R/max_R

data_force_t = np.array(data_force.index, dtype= float)
data_force_F = np.array(data_force['Kraft_N'], dtype= float)
data_force_s = np.array(data_force['Weg_mm'], dtype= float)

#%%
"""Plotting """
fig, ax = plt.subplots(2,2)

"""Plotting Time/Resistance/Force"""
ax[0][0].set_xlabel('time [s]')
ax[0][0].set_ylabel('Änderung [%]', color = 'tab:red')
ax[0][0].plot(data_smu_t, data_smu_r, color= 'tab:red')
ax[0][0].tick_params(axis='y', labelcolor= 'tab:red')
ax2 = ax[0][0].twinx()
ax2.set_ylabel('Kraft [N]', color= 'tab:blue')
ax2.plot(data_force_t, data_force_F, color= 'tab:blue')
ax2.tick_params(axis='y', labelcolor= 'tab:blue')

ax[0][0].legend(labels=['Widerstandsmessung'], loc='upper left')
ax2.legend(labels=['Kraftmessung'], loc= 'upper right')

"""Plotting Time/Resistance/Displacement"""
ax[1][0].set_xlabel('time [s]')
ax[1][0].set_ylabel('Änderung [%]', color = 'tab:red')
ax[1][0].plot(data_smu_t, data_smu_r, color= 'tab:red')
ax[1][0].tick_params(axis='y', labelcolor= 'tab:red')
ax3 = ax[1][0].twinx()
ax3.set_ylabel('Weg [mm]', color= 'tab:blue')
ax3.plot(data_force_t, data_force_s, color= 'tab:blue')
ax3.tick_params(axis='y', labelcolor= 'tab:blue')

ax[1][0].legend(labels=['Widerstandsmessung'], loc='upper left')
ax3.legend(labels=['Wegmessung'], loc= 'upper right')

"""Plotting Displacement/Force"""
ax[0][1].set_xlabel('Weg [mm]')
ax[0][1].set_ylabel('Kraft [N]')
ax[0][1].plot(data_force_s, data_force_F)

mpl.cursor(hover=True)

plt.show()
