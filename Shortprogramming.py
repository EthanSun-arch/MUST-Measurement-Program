# -*- coding: utf-8 -*-

import PythonLib as pl

root = pl.tk.Tk()
root.withdraw()

files = 1
newsys = False

force, res, ref = [], [], []
t_r, R, R_d, r, r_d, deltaR = [], [], [], [], [], []
t_f, f, x = [], [], []
t_ref, f_ref, x_ref = [], [], []

for i in range(files):
    force.append(pl.data_transfer_force())
    res.append(pl.data_transfer_smu())
    ref.append(pl.data_transfer_ref())

    t_f.append(pl.export_force_t(force[-1]))
    f.append(pl.export_force_F(force[-1]))
    x.append(pl.export_force_s(force[-1]))

    t_ref.append(pl.export_force_t(ref[-1]))
    f_ref.append(pl.export_force_F(ref[-1]))
    x_ref.append(pl.export_force_s(ref[-1]))

    t_r.append(pl.export_smu_t(res[-1]))
    R.append(pl.export_smu_R(res[-1]))
    R_d.append((R[-1] - R[-1][0]))
    r.append(R[-1]/max(R[-1]) * 100)
    r_d.append(R_d[-1]/max(R_d[-1]) * 100)
    deltaR.append((R[-1] - R[-1][0])/R[-1][0] * 100)

y_achse = ['Absolute Differenz zum Anfangswert [Ohm]',
           'Änderung [%] normiert auf das Maximum',
           r'$\Delta R/R_0 $ [%]']
res_label = ['Widerstandsmessung des eingeklemmten Sensors',
             'Widerstandsmessung der gedruckten Feder',
             'Widerstand der Zugprobe']
ref_label = ['Einhausung mit Doppelblechblattfeder',
             'Einhausung mit Doppel-PLA-Blattfeder']

diff = []

# pl.plot(t_r[0], R[0])

for i in range(files):
    diff.append(pl.compute_time_diff(t_f[i], f[i], t_r[i], deltaR[i]))
    t_r[i] = t_r[i] + diff[i][0]
    pl.plot_res_and_force(t_r[i], deltaR[i],
                          t_f[i], f[i], x[i],
                          t_ref[i], f_ref[i], x_ref[i],
                          y_achse[2], res_label[2], ref_label[1])
    
# l_0 = 28
l_0 = 40

strain_res = []
strain_res_100 = []
strain_res_max = []
maxi = []

t_f_temp, F, s = [],[],[]
t_r_temp, deltaR_temp = [],[]

if newsys == True:
    for i in range(files):
        t_f_temp.append(t_f[i][t_f[i]>=50])
        F.append(f[i][t_f[i]>=50])
        s.append(x[i][t_f[i]>=50])
        t_r_temp.append(t_r[i][t_r[i]>=50])
        deltaR_temp.append(deltaR[i][t_r[i]>=50])
else:
    t_f_temp = t_f
    F = f
    s = x
    t_r_temp = t_r
    deltaR_temp = deltaR

for i in range(files):
    strain_res.append(pl.compute_strain_res(l_0,
                                            t_r_temp[i], deltaR_temp[i], 
                                            t_f_temp[i], F[i], s[i]))  
    pl.plot_strain_res(strain_res[i][0], 
                        strain_res[i][1],
                        strain_res[i][2], 
                        strain_res[i][3],
                        strain_res[i][4])
index = []

for j in range(files):
    for i in range(len(strain_res[j][0])):
        if strain_res[j][0][i] == max(strain_res[j][0]):
            index.append(i)
            break
        
for i in range(files):
    pl.plot_strain_res(strain_res[i][0][0:index[0]], 
                        strain_res[i][1][0:index[0]],
                        strain_res[i][2][0:index[0]], 
                        strain_res[i][3],
                        strain_res[i][4])
    maxi.append(pl.compute_res_max_strain(strain_res[i][0][0:index[0]],
                                          strain_res[i][1][0:index[0]],
                                          strain_res[i][2][0:index[0]]))
    strain_res_max.append(pl.compute_strain_res_rmax(maxi[i][2],
                                                     maxi[i][3],
                                                     maxi[i][4]))
    strain_res_100.append(pl.compute_strain_res_100(strain_res[i][0][0:index[0]], 
                                                    strain_res[i][1][0:index[0]],
                                                    strain_res[i][2][0:index[0]]))

# for i in range(files):
#     pl.plot_strain_res(strain_res_100[i][0],
#                         strain_res_100[i][1],
#                         strain_res_100[i][2], 
#                         strain_res_100[i][3], 
#                         strain_res_100[i][4])

# for i in range(files):
#     pl.plot_strain_res(strain_res_max[i][0],
#                         strain_res_max[i][1],
#                         strain_res_max[i][2], 
#                         strain_res_max[i][3], 
#                         strain_res_max[i][4])

# bible = pl.data_transfer_bible()
# bible_mean = pl.data_transfer_bible()

# pl.plot_bible(bible, bible_mean)