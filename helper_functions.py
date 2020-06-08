import matplotlib.pyplot as plt  # matplotlib for some plotting
import numpy as np  # numeric python functions
import pandas as pd  # need this to load our data from the csv files
import pickle
import sys
import itertools
import scipy.optimize as so
import string

from curve_fitting import *

# --- General fitter
def fit_powerlaw_u_alpha(x, y, z_ref=100, p0=(10,0.1)):
    """ 
    p[0] : u_ref
    p[1] : alpha
    """
    pfit, _ = so.curve_fit(lambda x, *p : p[0] * (x / z_ref) ** p[1], x, y, p0=p0)
    y_fit = pfit[0] * (x / z_ref) ** pfit[1]
    coeffs_dict={'u_ref':pfit[0],'alpha':pfit[1]}
    formula = '{u_ref} * (z / {z_ref}) ** {alpha}'
    fitted_fun = lambda xx: pfit[0] * (xx / z_ref) ** pfit[1]
    return y_fit, pfit, {'coeffs':coeffs_dict,'formula':formula,'fitted_function':fitted_fun}

def fit_polynomial_continuous(x, y, order):
    pfit  = np.polyfit(x,y,order)
    y_fit = np.polyval(pfit,x)
    return y_fit,pfit,{'fitted_function':lambda xx : np.polyval(pfit,xx)}




def get_wsp_func(con_tc, h_hub, plot=False):
    con_stats = con_tc.get_time().describe().loc[['mean', 'std']]
    con_mean = con_stats.loc['mean']
    con_std  = con_stats.loc['std']
    con_z    = con_tc.filter(regex='u_').loc['z']
    u_mean = con_mean.filter(regex='u_')
    v_mean = con_mean.filter(regex='v_')


    # --- fit u
    y_fit, pfit, model = fit_powerlaw_u_alpha(con_z, u_mean, z_ref=h_hub, p0=(u_mean['u_p1'],0.1))

    alpha=pfit[1]
    u_ref=pfit[0]
    my_wsp_fun = lambda y,z: power_profile(y, z, u_ref= model['coeffs']['u_ref'], z_ref= h_hub, alpha=model['coeffs']['alpha'])

    # --- fit v

    zzzzz=np.concatenate((con_z,[240]))
    v_mean=np.concatenate((v_mean,[v_mean[-1]*1.0]))

    print(con_z,v_mean)
#     y_fit, pfit, model_v = fit_powerlaw_u_alpha(con_z, v_mean, z_ref=h_hub, p0=(v_mean['v_p1'],0.1))
#     y_fit, pfit, fitter_v = model_fit('eval: {A}*np.arctan({B}*x+{C})+1.0',zzzzz, v_mean)
    y_fit, pfit, fitter_v = model_fit('eval: {:.3f}*np.exp(-{:s}*x**5) +{:.3f}'.format(v_mean[0]-v_mean[-1],'{a}',+v_mean[-1]),zzzzz, v_mean)
    model_v=fitter_v.model

    my_veer_fun = lambda y,z, **kwargs: model_v['fitted_function'](z)


#     y_fit, pfit, model_v = fit_polynomial_continuous(zzzzz, v_mean, order=2)

    if plot:

        zz=np.linspace(0,240,100)
        fig,ax = plt.subplots(1, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
        fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)
        ax.plot(u_mean, con_z, 'kd', label='meas')
        ax.plot(model['fitted_function'](zz), zz, '-', label='fit')
        ax.set_xlabel('u [m/s]')
        ax.set_ylabel('z [m]')
        ax.legend()
        ax.tick_params(direction='in')

        zz=np.linspace(0,240,100)
        fig,ax = plt.subplots(1, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
        fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)
        ax.plot(v_mean, zzzzz, 'kd', label='meas')
        ax.plot(model_v['fitted_function'](zz), zz, '-', label='fit')
        ax.set_xlabel('v [m/s]')
        ax.set_ylabel('z [m]')
        ax.legend()
        ax.tick_params(direction='in')
    return alpha, u_ref, my_wsp_fun, my_veer_fun



def get_sigma_func(con_tc, plot=False):
    con_stats = con_tc.get_time().describe().loc[['mean', 'std']]
    con_std  = con_stats.loc['std']
    con_z    = con_tc.filter(regex='u_').loc['z']
    con_ustd=con_std.filter(regex='u_')
    con_vstd=con_std.filter(regex='v_')
    con_wstd=con_std.filter(regex='w_')

    zzzzz=np.concatenate((con_z,[240]))
    sig_u=np.concatenate((con_ustd,[con_ustd[-1]*0.8]))
    sig_v=np.concatenate((con_vstd,[con_vstd[-1]*0.8]))
    sig_w=np.concatenate((con_wstd,[con_wstd[-1]*0.8]))
    sig_v[0]*=0.9

    y_fit, pfit, model_su = fit_polynomial_continuous(zzzzz, sig_u, order=1)
    y_fit, pfit, model_sv = fit_polynomial_continuous(zzzzz, sig_v, order=2)
    y_fit, pfit, model_sw = fit_polynomial_continuous(zzzzz, sig_w, order=1)

    y_fit, pfit, fitter_sv = model_fit('eval: {A}*np.exp(-{k}*x)+{B}',zzzzz, sig_v, order=2)
    model_sv=fitter_sv.model
    y_fit, pfit, fitter_su = model_fit('eval: {A}*np.exp(-{k}*x)+{B}',zzzzz, sig_u, order=2)
    model_su=fitter_su.model
    z_fit, pfit, fitter_sw = model_fit('eval: {A}*np.exp(-{k}*x)+{B}',zzzzz, sig_w, order=2)
    model_sw=fitter_sw.model

    def custom_sig(k, y, z, **kwargs):
        sig = np.zeros(y.shape)
        sig[k==0] = model_su['fitted_function'](z[k==0])
        sig[k==1] = model_sv['fitted_function'](z[k==1])
        sig[k==2] = model_sw['fitted_function'](z[k==2])
        return sig

    if plot:
        zz=np.linspace(0,240,100)
        fig,ax = plt.subplots(1, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
        fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)
        ax.plot(sig_u, zzzzz, 'kd', label='meas')
        ax.plot(model_su['fitted_function'](zz), zz, '-', label='fit')
        ax.plot(sig_v, zzzzz, 'kd', label='meas')
        ax.plot(model_sv['fitted_function'](zz), zz, '-', label='fit')
        ax.plot(sig_w, zzzzz, 'kd', label='meas')
        ax.plot(model_sw['fitted_function'](zz), zz, '-', label='fit')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.legend()
        ax.tick_params(direction='in')


    return custom_sig

