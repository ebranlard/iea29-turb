import matplotlib.pyplot as plt  # matplotlib for some plotting
import numpy as np  # numeric python functions
import pandas as pd  # need this to load our data from the csv files
import pickle
import sys
import itertools
import scipy.optimize as so
import os
from pyconturb import gen_turb, gen_spat_grid, TimeConstraint  # functions we need from PyConTurb
from pyconturb.tictoc import Timer
from pyconturb.wind_profiles import power_profile
from helper_functions import *

# --- Parameters
dtype=np.float32 # TODO
bBackWard=False
Suffix=''

# --- Parameters from command line
if len(sys.argv)>1:
    Case    = sys.argv[1].strip()
    combine_freq_data = sys.argv[3].lower()=='t'
    write_freq_data = True
else:
    write_freq_data = False
    Case='A1'
    Suffix+='_nochunks'
    combine_freq_data = True

# --- Constants and derived params
# ymin,ymax = -240,240
# zmin,zmax = 3,240
# ny = 161 
# nz = 80 
ymin,ymax = -320,320  # -4D, 4D
zmin,zmax = 3,480  # 0->6D
ny = 214
nz = 160

Suffix=Suffix+'_'+str(ny)'_'+str(nz)

print('>>> Case:   {}'.format(Case))
print('>>> Suffix: {}'.format(Suffix))
print('>>> Write:  {} {}'.format(write_freq_data,combine_freq_data))
print('>>> y:      {} {} {}'.format(ymin,ymax,ny))
print('>>> z:      {} {} {}'.format(zmin,zmax,nz))
h_hub=57;
pkl_file = '{}{}.pkl'.format(Case,Suffix)
pkl_space = '{}{}_space.pkl'.format(Case,Suffix)
con_file = '35Hz_data/{}_pyConTurb_tc.csv'.format(Case)

# --- Constraint time series
con_tc = TimeConstraint(pd.read_csv(con_file, index_col=0))  # load data from csv directly into tc
con_tc.index = con_tc.index.map(lambda x: float(x) if (x not in 'kxyz') else x)  # index cleaning
time_df = con_tc.get_time()
dt      = con_tc.get_time().index[1]
T       = con_tc.get_T()-dt          # TODO
print('>>> Pkl : {}Mb'.format(0.07*ny*nz))
print('>>> T, dt:',T,dt)

# --- Fitting power law and sigma
# alpha,u_ref, my_wsp_func,veer_func = get_wsp_func(con_tc, h_hub, plot   = False)
# my_sig_func                        = get_sigma_func(con_tc, plot = False)
if Case=='A1':
    def my_sig_func(k, y, z, **kwargs):
        sig = np.zeros(y.shape)
        sig[k==0] =  0.46577620264919134*np.exp(-0.009459702869284256*z[k==0])+0.5242096170226613
        sig[k==1] =  0.32501065767141885*np.exp(-0.009059732365499604*z[k==1])+0.4664357892808409
        sig[k==2] =  0.25265083664918636*np.exp(-0.00816719396912162 *z[k==2])+0.27864558900332614
        return sig
    alpha=0.09501
    u_ref=8.86407 
elif Case=='A2':
    def my_sig_func(k, y, z, **kwargs):
        sig = np.zeros(y.shape)
        sig[k==0] = 0.8099028667369905 *np.exp(-0.021555344194775908  *z[k==0])+0.4071960755269242
        sig[k==1] = 135.7599449425806  *np.exp(-3.5109472359675726e-06*z[k==1])+-135.1080431878093
        sig[k==2] = 0.22495339546333412*np.exp(-0.011140930815265206  *z[k==2])+0.31941416670478984
        return sig
    alpha=0.10748
    u_ref=9.51186
elif Case=='B1':
    def my_sig_func(k, y, z, **kwargs):
        sig = np.zeros(y.shape)
        sig[k==0] = 0.5115673365356883*np.exp(-0.013331621241907558 *z[k==0])+0.47484654611672855
        sig[k==1] = 0.3991956202078298*np.exp(-0.011923833640356686 *z[k==1])+0.4190659656311234
        sig[k==2] = 0.39194178694509046*np.exp(-0.004711856260504405*z[k==2])+0.26768397422947954
        return sig

    alpha=0.09482
    u_ref=7.61636




sig_func=None
sig_func=my_sig_func
wsp_func=None
# wsp_func=my_sig_func
veer_func=None

print('Using fitted wind profile:')
print('>>> alpha:',alpha)
print('>>> u_ref:',u_ref)
print('Using fitted sigma profile:')
# plt.show()

# ---
y = np.linspace(ymin,ymax, ny)  # lateral components of turbulent grid
z = np.linspace(zmin,zmax, nz)  # vertical components of turbulent grid
# print('y:',y)
# print('z:',z)
kwargs = {'u_ref': u_ref, 'turb_class': 'B', 'z_hub': h_hub,  # necessary keyword arguments for IEC turbulence
        'u_ref': u_ref, 'z_ref': h_hub, 'alpha':alpha, # keywords for power_profile
        'T': con_tc.get_T(), 'dt': con_tc.get_time().index[1], 'backward_comp':bBackWard}  # simulation length (s) and time step (s)
interp_data = ['wsp','sig']  # use the default IEC 61400-1 profile instead of interpolating from contstraints
interp_data = "none"  # use the default IEC 61400-1 profile instead of interpolating from contstraints

# --- Save box spatial data
spat_df = gen_spat_grid(y, z)
pickle.dump(spat_df, open(pkl_space,'wb'))

# --- Generate constrained turbulence
# We now pass our constraint object and other arguments into `gen_turb` as follows.
if os.path.exists(pkl_file):
    print('>>> NOT GENERATING TURBULENCE, PKL FILE EXIST',pkl_file)
else:
    with Timer('all:'):
        sim_turb_df = gen_turb(spat_df, con_tc=con_tc, interp_data=interp_data, wsp_func=wsp_func, veer_func=veer_func, sig_func=sig_func, seed=12, verbose=False,
                write_freq_data=write_freq_data, combine_freq_data=combine_freq_data, preffix='data/'+Case+Suffix+'_', dtype=dtype, **kwargs)

    if sim_turb_df is not None: 
        with Timer('Export:'):
            print('>>> Exporting to pkl_file')
            pickle.dump(sim_turb_df, open(pkl_file,'wb'))
# 
# **Note**: The profile functions selected for the wind speed, turbulence standard deviation and power spectra affect whether you regenerate the constraining data if a simulation point is collocated. One option is to use the built-in profile functions that interpolates these profiles from your data (see related example in the documentation). Otherwise, you can define your own profile functions for custom interpolation.

# ## Inputs to constrained turbulence
# The first step is to define the spatial information for the desired turbulence box and the related parameters for the turbulence generation technique. In this case we will use the default IEC 61400-1 Ed. 3 simulation procedures (Kaimal Spectrum with Exponential Coherence) instead of interpolating from the data. Note that, by default, PyConTurb will not interpolate profiles from data.

# For a rotor diameter of ≈80 m, a maximum chord of ≈3 m, and a wind speed of ≈8 m/s, the rules of thumb for convergence of FAST.Farm would suggest the following discretization requirements for the ambient wind field:
# •	Spatial resolution around rotor ≤ 3 m
# •	Time step around rotor ≤ 0.1 s
# •	Spatial resolution for meandering (away from the rotor) ≤ 8 m
# •	Time step for meandering (away from the rotor) ≤ 2 s
# 
# Based on these results, it would be easiest for us if there was one Mann box with uniform spatial-temporal resolution of ≈3 m and ≈0.1 s.  But we could probably make do (with a bit of data conversion) if you provided two boxes based on the above discretization requirements.  To ensure that it is big enough to capture wake meandering, the larger box (or one large box) should probably be around 6D (480 m) wide and 3D (240 m) tall.
