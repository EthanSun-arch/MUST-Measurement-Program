# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 10:59:44 2022

@author: Esan
"""


import numpy as np
import pandas as pd
from scipy import stats as st
import matplotlib.pyplot as plt
import mplcursors as mpl






#%%
"""Importing Data via Pandas"""
foldername = '220614_Druck/'
directory = foldername + '220614_Druck_5Nmax_10x3'

data_force = pd.read_csv('C:/Users/Esan/Documents/Masterarbeit/Messungen/'+ directory + '.txt',
                         sep= ';',
                         dtype= float)

data_smu = pd.read_csv('C:/Users/Esan/Documents/Masterarbeit/Messungen/'+ directory + '.csv',
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
max_R = max(data_smu_R)
data_smu_r = data_smu_R/max_R * 100

data_force_t = np.array(data_force['Zeit_s'], dtype= float)
data_force_F = np.array(data_force['Kraft_N'], dtype= float)
data_force_s = np.array(data_force['Weg_mm'], dtype= float)

#%%
"""Computing the linear error"""
force0_index = data_force[data_force['Kraft_N'] >= min(data_force_F)+ 0.02].index
force5_index = data_force[data_force['Kraft_N'] >= max(data_force_F)- 0.1].index

f_time = data_force[force0_index[0]:force5_index[0]]['Zeit_s']
f_value = data_force[force0_index[0]:force5_index[0]]['Kraft_N']

reg = st.linregress(f_time, f_value)

res0_index = data_smu[data_smu_t >= data_force['Zeit_s'][force0_index[0]]].index
res5_index = data_smu[data_smu_t >= data_force['Zeit_s'][force5_index[0]]].index

res_time = data_smu_t[res0_index[0]:res5_index[0]]
res_value = data_smu_R[res0_index[0]:res5_index[0]]
res_value2 = data_smu_r[res0_index[0]:res5_index[0]]


x = np.linspace(data_force['Zeit_s'][force0_index[0]], 
                data_force['Zeit_s'][force5_index[0]], 
                num= res5_index[0]-res0_index[0])
x_f = reg.intercept + reg.slope*x



#%%
"""Plotting """
fig, ax = plt.subplots(2)
fig.set_tight_layout(True)
"""Plotting Time/Resistance/Force"""
ax[0].set_xlabel('Zeit [s]')
ax[0].set_ylabel('Änderung [%]', color = 'tab:red')
ax[0].plot(data_smu_t, data_smu_r, color= 'tab:red')
ax[0].tick_params(axis='y', labelcolor= 'tab:red')
ax[0].legend(labels=['Widerstandsmessung'], loc='upper left')

ax2 = ax[0].twinx()
ax2.set_ylabel('Kraft [N]', color= 'tab:blue')
ax2.plot(data_force_t, data_force_F, color= 'tab:blue')
ax2.tick_params(axis='y', labelcolor= 'tab:blue')
ax2.legend(labels=['Kraftmessung'], loc= 'upper right')

"""Plotting Time/Resistance/Displacement"""
ax[1].set_xlabel('Zeit [s]')
ax[1].set_ylabel('Änderung [%]', color = 'tab:red')
ax[1].plot(data_smu_t, data_smu_r, color= 'tab:red')
ax[1].tick_params(axis='y', labelcolor= 'tab:red')
ax[1].legend(labels=['Widerstandsmessung'], loc='upper left')

ax3 = ax[1].twinx()
ax3.set_ylabel('Weg [mm]', color= 'tab:blue')
ax3.plot(data_force_t, data_force_s, color= 'tab:blue')
ax3.tick_params(axis='y', labelcolor= 'tab:blue')
ax3.legend(labels=['Wegmessung'], loc= 'upper right')

"""Plotting Fit"""
fig2, ax4 = plt.subplots(2)
fig2.set_tight_layout(True)
ax4[0].set_xlabel('Zeit [s]')
ax4[0].set_ylabel('Kraft [N]', color= 'tab:blue' )
ax4[0].tick_params(axis= 'y', labelcolor= 'tab:blue')
ax4[0].plot(f_time, f_value, 'tab:blue', label= 'real data')
ax4[0].plot(f_time, reg.intercept+reg.slope*f_time, '--g', label= 'fitted line')
ax4[0].legend(loc = 'upper right')

ax5 = ax4[0].twinx()
ax5.set_ylabel('Änderung [%]', color= 'tab:red')
ax5.tick_params(axis= 'y', labelcolor= 'tab:red')
ax5.plot(res_time, res_value2,
         'tab:red', label= 'Widerstandsänderung')
ax5.legend(loc= 'upper left')

ax4[1].plot(x_f, res_value2)
ax4[1].set_xlabel('Kraft [N]')
ax4[1].set_ylabel('Änderung [%]')
# ax4[1].plot(y_f, np.gradient(data_smu_r[res0_index[0]:res5_index[0]], y_f))

"""Plotting Displacement/Force"""
fig3, ax6 = plt.subplots()
fig3.set_tight_layout(True)
ax6.set_xlabel('Weg [mm]')
ax6.set_ylabel('Kraft [N]')
ax6.plot(data_force_s, data_force_F)

mpl.cursor(hover=True)

plt.show()
