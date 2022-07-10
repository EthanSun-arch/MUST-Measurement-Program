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

t_f     = pl.export_force_t(force)
f       = pl.export_force_F(force)
x       = pl.export_force_s(force)

t_ref   = pl.export_force_t(ref)
f_ref   = pl.export_force_F(ref)
x_ref   = pl.export_force_s(ref)

# pl.plot_force(t_f, f, x, t_ref, f_ref, x_ref)

pl.plot_res_and_force(t_r+0.561, R_d, t_f, f, x, t_ref, f_ref, x_ref)

grad = pl.compute_gradient(t_f, f, t_r, R)

pl.plot_gradient(t_f, grad[0][0], t_r, grad[1][0])

bkps = 20

# lin_err_f = pl.compute_force_lin_err(t_f, f, x, bkps)

# pl.plot_force_lin_err(lin_err_f[0][0], lin_err_f[1][0], 
#                       lin_err_f[2][0], lin_err_f[3][0])

lin_err_r = pl.compute_res_lin_err(res, t_r, R_d, t_f, f, bkps)

pl.plot_res_lin_err(lin_err_r[0][0], lin_err_r[1][0], 
                     lin_err_r[2][0], lin_err_r[3][0])


