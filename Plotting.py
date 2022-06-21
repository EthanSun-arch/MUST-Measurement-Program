# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 10:59:44 2022

@author: Esan
"""


import numpy as np
import pandas as pd
from scipy import stats as st
from scipy import signal as sg
import matplotlib.pyplot as plt
import mplcursors as mpl
import ruptures as rpt





#%%
"""Importing Data via Pandas"""
foldername = '220621/'
directory = foldername + '220621_4Nmax_'
repeats = 4
zusatz = ''

bkps = 4* repeats 

data_force = pd.read_csv('C:/Users/Esan/Documents/Masterarbeit/Messungen/'+ directory + str(repeats) + 'x' 
                         + zusatz + '.txt',
                         sep= ';',
                         dtype= float)

data_smu = pd.read_csv('C:/Users/Esan/Documents/Masterarbeit/Messungen/'+ directory + str(repeats) + 'x' 
                       + zusatz + '.csv',
                       dtype= {'Widerstand [Ohm]': np.single},
                       sep= ',')

#%%
"""Adjusting the time into realtive values"""
data_smu = data_smu
data_smu['Zeit [Datum+T+Zeit]'] = pd.to_datetime(data_smu['Zeit [Datum+T+Zeit]'])
firstValue = data_smu['Zeit [Datum+T+Zeit]'].iloc[0]
data_smu['Zeit [Datum+T+Zeit]'] = data_smu['Zeit [Datum+T+Zeit]'] - firstValue

#%%
"""Importing the x and y data """
data_smu_t = np.array(np.ones(len(data_smu['Zeit [Datum+T+Zeit]'])))
for i in range(len(data_smu['Zeit [Datum+T+Zeit]'])):
    data_smu_t[i] = data_smu['Zeit [Datum+T+Zeit]'][i].total_seconds()
    
t=0.78 + 0.172
    
data_smu_t = data_smu_t + t
data_smu_R = np.array(data_smu['Widerstand [Ohm]'], dtype= np.double)
data_smu_R_d = data_smu_R - np.mean(data_smu_R[0])
data_smu_r = data_smu_R/max(data_smu_R) * 100

data_force_t = np.array(data_force['Zeit_s'], dtype= float)
data_force_F = np.array(data_force['Kraft_N'], dtype= float)
data_force_s = np.array(data_force['Weg_mm'], dtype= float)

#%%
"""Plotting """
fig, ax = plt.subplots(2,2)
fig.set_tight_layout(True)
"""Plotting Time/Resistance/Force"""
ax[0][0].set_xlabel('Zeit [s]')
ax[0][0].set_ylabel('Änderung [%] normiert auf das Maximum', color = 'tab:red')
ax[0][0].plot(data_smu_t, data_smu_R_d, color= 'tab:red')
ax[0][0].tick_params(axis='y', labelcolor= 'tab:red')
ax[0][0].legend(labels=['Widerstandsmessung'], loc='upper left')

ax2 = ax[0][0].twinx()
ax2.set_ylabel('Kraft [N]', color= 'tab:blue')
ax2.plot(data_force_t, data_force_F, color= 'tab:blue')
ax2.tick_params(axis='y', labelcolor= 'tab:blue')
ax2.legend(labels=['Kraftmessung'], loc= 'upper right')

"""Plotting Time/Resistance/Displacement"""
ax[1][0].set_xlabel('Zeit [s]')
ax[1][0].set_ylabel('Änderung [%] normiert auf das Maximum', color = 'tab:red')
ax[1][0].plot(data_smu_t, data_smu_R_d, color= 'tab:red')
ax[1][0].tick_params(axis='y', labelcolor= 'tab:red')
ax[1][0].legend(labels=['Widerstandsmessung'], loc='upper left')

ax3 = ax[1][0].twinx()
ax3.set_ylabel('Weg [mm]', color= 'tab:blue')
ax3.plot(data_force_t, data_force_s, color= 'tab:blue')
ax3.tick_params(axis='y', labelcolor= 'tab:blue')
ax3.legend(labels=['Wegmessung'], loc= 'upper right')

plt.show()

#%%
b, a = sg.butter(3, 0.1, 'lowpass')
filtered_r = sg.filtfilt(b, a, np.gradient(data_smu_r, data_smu_t))

b, a = sg.butter(3, 0.01, 'lowpass')
filtered_F = sg.filtfilt(b, a, np.gradient(data_force_F, data_force_t))

"""Plotting Slope"""
ax[0][1].set_xlabel('Zeit [s]')
ax[0][1].set_ylabel('Steigung der Widerstandsänderung [%/s]', color = 'tab:red')
ax[0][1].plot(data_smu_t, filtered_r, color= 'tab:red')
ax[0][1].tick_params(axis='y', labelcolor= 'tab:red')
ax[0][1].legend(labels=['Widerstandsmessung'], loc='upper left')

ax2 = ax[0][1].twinx()
ax2.set_ylabel('Steigung der Kraft [N/s]', color= 'tab:blue')
ax2.plot(data_force_t, filtered_F, color= 'tab:blue')
ax2.tick_params(axis='y', labelcolor= 'tab:blue')
ax2.legend(labels=['Kraftmessung'], loc= 'upper right')

plt.show()

algo = rpt.BottomUp(model='l2').fit(filtered_F)
result = algo.predict(bkps)

rpt.display(data_force_F, result)
#%%
"""Computing the linear error"""
f_time, f_value = [], []
reg = []
res0_index, res5_index = [], []
res_time, res_value, res_value2, res_value3 = [], [], [], []
x, x_f = [], []
lin_f, lin_err = [], []

for i in range(0,bkps,2):
    f_time.append(data_force[result[i]:result[i+1]]['Zeit_s'].reset_index())
    f_value.append(data_force[result[i]:result[i+1]]['Kraft_N'])
    
for i in range(0, len(f_time)):    
    reg.append(st.linregress(f_time[i]['Zeit_s'], f_value[i]))

for i in range(0,bkps,2):
    res0_index.append(data_smu[data_smu_t >= data_force['Zeit_s'][result[i]]].index)
    res5_index.append(data_smu[data_smu_t >= data_force['Zeit_s'][result[i+1]]].index)
    
for i in range(len(res0_index)):
    res_time.append(data_smu_t[res0_index[i][0]:res5_index[i][0]])
    res_value.append(data_smu_R[res0_index[i][0]:res5_index[i][0]])
    res_value2.append(data_smu_r[res0_index[i][0]:res5_index[i][0]])
    res_value3.append(data_smu_R_d[res0_index[i][0]:res5_index[i][0]])

# temp = np.mean(data_smu_R[:result[0]])
    
for i in range(len(f_time)):   
    x.append(np.linspace(f_time[i]['Zeit_s'][0], 
                         f_time[i]['Zeit_s'][len(f_time[i])-1], 
                         num= res5_index[i][0]-res0_index[i][0]))  
    x_f.append(reg[i].intercept + reg[i].slope*x[i])
    lin_f.append(st.linregress(x_f[i], res_value3[i]))
    lin_err.append((res_value3[i] - (lin_f[i].intercept + lin_f[i].slope * x_f[i]))/(res_value3[i][-1]-res_value3[i][0]) * 100)

#%%
"""Plotting Fit"""
fig2, ax4 = plt.subplots(2,2)
fig2.set_tight_layout(True)
# ax4[0].set_xlabel('Zeit [s]')
# ax4[0].set_ylabel('Kraft [N]', color= 'tab:blue' )
# ax4[0].tick_params(axis= 'y', labelcolor= 'tab:blue')
# ax4[0].plot(f_time, f_value, 'tab:blue', label= 'real data')
# ax4[0].plot(f_time, reg.intercept+reg.slope*f_time, '--g', label= 'fitted line')
# ax4[0].legend(loc = 'upper right')

# ax5 = ax4[0].twinx()
# ax5.set_ylabel('Änderung [%]', color= 'tab:red')
# ax5.tick_params(axis= 'y', labelcolor= 'tab:red')
# ax5.plot(res_time, res_value2,
#          'tab:red', label= 'Widerstandsänderung')
# ax5.legend(loc= 'upper left')

for i in range(len(x_f)):    
    if i % 2 == 0:
        ax4[0][0].plot(x_f[i], res_value3[i], label= 'Steigung ' + str(i))
        ax4[0][0].plot(x_f[i], lin_f[i].intercept + lin_f[i].slope * x_f[i], '--r', label= 'fitted Steigung'+ str(i))
        ax4[0][0].set_xlabel('Kraft [N]')
        ax4[0][0].set_ylabel('Widerstand [kOhm]')
        ax4[0][0].legend()
        
        ax4[1][0].scatter(x_f[i], lin_err[i], s= 0.3)
        ax4[1][0].set_xlabel('Kraft [N]')
        ax4[1][0].set_ylabel('Linearisierungsfehler [%] normiert auf den Messbereich')
    else:
        ax4[0][1].plot(x_f[i], res_value3[i], label='Abfall ' + str(i))
        ax4[0][1].plot(x_f[i], lin_f[i].intercept + lin_f[i].slope * x_f[i], '--r', label= 'fitted Abfall ' + str(i))
        ax4[0][1].invert_xaxis()
        ax4[0][1].set_xlabel('Kraft [N]')
        ax4[0][1].set_ylabel('Widerstand [kOhm]')
        ax4[0][1].legend()
        
        ax4[1][1].scatter(x_f[i], lin_err[i], s= 0.3)
        ax4[1][1].invert_xaxis()
        ax4[1][1].set_xlabel('Kraft [N]')
        ax4[1][1].set_ylabel('Linearisierungsfehler [%] normiert auf den Messbereich')


"""Plotting Displacement/Force"""
fig3, ax6 = plt.subplots()
fig3.set_tight_layout(True)
ax6.set_xlabel('Weg [mm]')
ax6.set_ylabel('Kraft [N]')
ax6.plot(data_force_s, data_force_F)

mpl.cursor(hover=True)

plt.show()
