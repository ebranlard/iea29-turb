#!/usr/bin/env python
from pathlib import Path
import matplotlib.pyplot as plt  # matplotlib for some plotting
import numpy as np  # numeric python functions
import pandas as pd  # need this to load our data from the csv files
from pyconturb import gen_turb, gen_spat_grid, TimeConstraint  # functions we need from PyConTurb
import pickle
# from pybra.tictoc import Timer


# ---- Parameters
Case='A1'
ymin,ymax = -198,198
zmin,zmax = 3,198
ny = 133 # 133 # TODO 133
nz = 66  # 66  # TODO 66

# --- Constants and derived params
h_hub=57;
x_refPoints=np.array(3*[293.9])
y_refPoints=np.array(3*[107.1])
z_refPoints=np.array([17,57,93])
pkl_file = '{}.pkl'.format(Case)
pkl_space = '{}_space.pkl'.format(Case)
box_file = '{}.bts'.format(Case)
con_file = '35Hz_data/{}_pyConTurb_tc.csv'.format(Case)

 ## Constraining time series
con_tc = TimeConstraint(pd.read_csv(con_file, index_col=0))  # load data from csv directly into tc
con_tc.index = con_tc.index.map(lambda x: float(x) if (x not in 'kxyz') else x)  # index cleaning
# con_tc.iloc[:7, :]  # look at the first 7 rows
# con_tc.get_spat()
# con_tc.get_time().iloc[:5, :8]
time_df = con_tc.get_time()
dt      = con_tc.get_time().index[1]
T       = con_tc.get_T()-dt          # TODO
u_ref=time_df['u_p1'].mean()
print('>>> Pkl : {}Mb'.format(0.14*ny*nz))
print('>>> T, dt:',T,dt)
print('>>> u_ref:',u_ref)


# We can plot the points to visualize the locations of the constrainting points in space.
# u_locs = con_tc.get_spat().filter(regex='u_').loc[['y', 'z']]
# [plt.scatter(u_locs.loc['y', col], u_locs.loc['z', col], label=col) for col in u_locs];
# plt.legend(); plt.ylabel('height [m]'); plt.xticks([]);


# Now let's visualize the constraining time series.
# ax = time_df.filter(regex='u_', axis=1).plot(lw=0.75)  # subselect long. wind component
# ax.set_ylabel('longitudinal wind speed [m/s]');
# [print(x) for x in time_df.filter(regex='u_', axis=1).mean()];  # print mean values
# plt.show()


## Inputs to constrained turbulence
# The first step is to define the spatial information for the desired turbulence box and the related parameters for the turbulence generation technique. In this case we will use the default IEC 61400-1 Ed. 3 simulation procedures (Kaimal Spectrum with Exponential Coherence) instead of interpolating from the data. Note that, by default, PyConTurb will not interpolate profiles from data.

y = np.linspace(ymin,ymax, ny)  # lateral components of turbulent grid
z = np.linspace(zmin,zmax, nz)  # vertical components of turbulent grid
print('y:',y)
print('z:',z)
kwargs = {'u_ref': u_ref, 'turb_class': 'B', 'z_hub': h_hub,  # necessary keyword arguments for IEC turbulence
          'T': con_tc.get_T(), 'dt': con_tc.get_time().index[1]}  # simulation length (s) and time step (s)
interp_data = 'none'  # use the default IEC 61400-1 profile instead of interpolating from contstraints

# This function below generates the actual spatial data. It assumes we want all three turbulence components at each spatial location.
spat_df = gen_spat_grid(y, z)  # create our spatial pandas dataframe. Columns are k, p_id x, y, and z.
pickle.dump(spat_df, open(pkl_space,'wb'))

# plt.scatter(spat_df.loc['y'], spat_df.loc['z'], label='sim. grid')
# plt.plot(con_tc.iloc[2, :6], con_tc.iloc[3, :6], 'rX', label='constraint')
# plt.axis('equal'); plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.);


#---  Generate constrained turbulence
# We now pass our constraint object and other arguments into `gen_turb` as follows.
sim_turb_df = gen_turb(spat_df, con_tc=con_tc, interp_data=interp_data, seed=12, verbose=True, **kwargs)
pickle.dump(sim_turb_df, open(pkl_file,'wb'))


# **Note**: The profile functions selected for the wind speed, turbulence standard deviation and power spectra affect whether you regenerate the constraining data if a simulation point is collocated. One option is to use the built-in profile functions that interpolates these profiles from your data (see related example in the documentation). Otherwise, you can define your own profile functions for custom interpolation.

# For a rotor diameter of ≈80 m, a maximum chord of ≈3 m, and a wind speed of ≈8 m/s, the rules of thumb for convergence of FAST.Farm would suggest the following discretization requirements for the ambient wind field:
# •	Spatial resolution around rotor ≤ 3 m
# •	Time step around rotor ≤ 0.1 s
# •	Spatial resolution for meandering (away from the rotor) ≤ 8 m
# •	Time step for meandering (away from the rotor) ≤ 2 s
# 
# Based on these results, it would be easiest for us if there was one Mann box with uniform spatial-temporal resolution of ≈3 m and ≈0.1 s.  But we could probably make do (with a bit of data conversion) if you provided two boxes based on the above discretization requirements.  To ensure that it is big enough to capture wake meandering, the larger box (or one large box) should probably be around 6D (480 m) wide and 3D (240 m) tall.
