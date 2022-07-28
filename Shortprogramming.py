# -*- coding: utf-8 -*-

import PythonLib as pl

root = pl.tk.Tk()
root.withdraw()

force, res, ref = [], [], []


force   = pl.data_transfer_force() 
res     = pl.data_transfer_smu()
ref     = pl.data_transfer_ref()

t_r     = pl.export_smu_t(res) 
R       = pl.export_smu_R(res)
R_d     = (R - R[0])
r       = R/max(R) * 100
r_d     = R_d/max(R_d) * 100 
deltaR = (R - R[0])/R[0] * 100

t_f     = pl.export_force_t(force)
f       = pl.export_force_F(force)
x       = pl.export_force_s(force)

t_ref   = pl.export_force_t(ref)
f_ref   = pl.export_force_F(ref)
x_ref   = pl.export_force_s(ref)



y_achse = ['Absolute Differenz zum Anfangswert [Ohm]', 'Änderung [%] normiert auf das Maximum', 'deltaR/R_0 [%]' ]
res_label = ['Widerstandsmessung des eingeklemmten Sensors', 'Widerstandsmessung der gedruckten Feder', 'Widerstand der Zugprobe']
ref_label = ['Einhausung mit Doppelblechblattfeder', 'Einhausung mit Doppel-PLA-Blattfeder']

diff, f_diff = pl.compute_time_diff(t_f, f, t_r, r, tensile= False)

if diff < 0:
    t_r = t_r - abs(diff)    
elif diff > 0:
    t_r = t_r + abs(diff)

pl.plot_res_and_force(t_r, deltaR, 
                      t_f, f, x, 
                      t_ref, f_ref, x_ref, 
                      y_achse[2], res_label[2], ref_label[1], sensor= False)

# grad = pl.compute_gradient(t_f, f, t_r, r)

# pl.plot_gradient(t_f, grad[0][0], t_r, grad[1][0])