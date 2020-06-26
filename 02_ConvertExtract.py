import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Local 
# import weio
from TurbSimFile import TurbSimFile
from MannBoxFile import MannBoxFile
from pyconturb import gen_turb, gen_spat_grid, TimeConstraint  # functions we need from PyConTurb

import pickle
from helper_functions import *


# --- Parameters
OUT_Folder='_ForHenrik/'

Cases=['A1','A2','B1']
for Case in Cases:
#     Case='A1'
    # Case='B1'
    # Case='B1'
    # Suffix='_nochunks_37'
    # Suffix='_37'
    # Suffix='_nochunks_1'
    Suffix='_161'
    Plot=False
    # Plot=False
    GenerateBox=True
    # GenerateBox=False


    # --- Constants and derived params
    pkl_file  = '{}{}.pkl'.format(Case,Suffix)
    pkl_space = '{}{}_space.pkl'.format(Case,Suffix)
    box_file  = '{}{}{}.bts'.format(OUT_Folder,Case,Suffix)
    con_file  = '35Hz_data/{}_pyConTurb_tc.csv'.format(Case)
    # --- Loading files
    print('Loading files...')
    sim_ts  = pickle.load(open(pkl_file,'rb'))
    sim_sp = pickle.load(open(pkl_space,'rb'))
    con_tc = TimeConstraint(pd.read_csv(con_file, index_col=0))  # load data from csv directly into tc
    con_tc.index = con_tc.index.map(lambda x: float(x) if (x not in 'kxyz') else x)  # index cleaning
    con_ts = con_tc.get_time()
    con_sp = con_tc.loc[['k','x','y','z']]

    RefPoints = con_sp.filter(regex='u_', axis=1).loc[['x','y','z']]
    print(RefPoints)
    print(sim_ts.columns)
    print(sim_sp.columns)

    if GenerateBox:
        print('Generating turbulence file:',box_file)
        ts = TurbSimFile()
        ts['y'] = np.unique(np.around(sim_sp.loc['y'].values,7))
        ts['z'] = np.unique(np.around(sim_sp.loc['z'].values,7))
        ts['t'] = np.around(sim_ts.index,10)
        ts['zHub']= (ts['z'][0]+ts['z'][-1])/2 # Not the real hub height
        nt      =  len(ts['t'])
        ts['u'] = np.zeros((3, nt, len(ts['y']), len(ts['z'])), dtype = np.float32)
        ts['ID']=8 # Periodic
        print('y',ts['y'])
        print('z',ts['z'])
        for iy in np.arange(len(ts['y'])):
            for iz in np.arange(len(ts['z'])):
                P,Iu,Iv,Iw =  get_indices(sim_sp, [ts['y'][iy]], [ts['z'][iz]], atol=1e-6)
                ts['u'][0,:,iy,iz] = sim_ts['u_p'+str(P[0])]
                ts['u'][1,:,iy,iz] = sim_ts['v_p'+str(P[0])]
                ts['u'][2,:,iy,iz] = sim_ts['w_p'+str(P[0])]
        u_mean= np.mean(ts['u'][0,:,:,:],axis=0)
        v_mean= np.mean(ts['u'][1,:,:,:],axis=0)
        w_mean= np.mean(ts['u'][2,:,:,:],axis=0)
        ts['u'][1,:,:,:] -= v_mean
        ts['u'][2,:,:,:] -= w_mean

        # Write TurbSim file
        ts.write(box_file)


    # --- Convert to Hawc2 format
    ts_filename='{}{}.bts'.format(Case,Suffix)
    print('Reading TurbSim')
    ts=TurbSimFile(box_file)
    mn = MannBoxFile()
    print('Writting u')
    mn.fromTurbSim(ts['u'],0)
    mn.write(ts_filename.replace('.bts','.u'))
    print('Writting v')
    mn.fromTurbSim(ts['u'],1)
    mn.write(ts_filename.replace('.bts','.v'))
    print('Writting w')
    mn.fromTurbSim(ts['u'],2)
    mn.write(ts_filename.replace('.bts','.w'))

    # --- Probe and info files
    print('Probe and info files')
    zProbe=[17,57,93]
    yProbe=[0,-107.1]
    # writing an info file
    infofile = '{}{}{}_info.txt'.format(OUT_Folder,Case,Suffix)
    with open(infofile,'w') as f:
        f.write(str(ts))
        zMid =(ts['z'][0]+ts['z'][-1])/2
        f.write('Middle height of box: {:.3f}\n'.format(zMid))
        iy,_ = ts._iMid()
        u = np.mean(ts['u'][0,:,iy,:], axis=0)
        z=ts['z']
        f.write('\n')
        y_fit, pfit, model =  fit_powerlaw_u_alpha(z, u, z_ref=zMid, p0=(10,0.1))
        f.write('Power law: alpha={:.5f}  -  u={:.5f}  at z={:.5f}\n'.format(pfit[1],pfit[0],zMid))
        f.write('Periodic: {}\n'.format(ts.checkPeriodic(sigmaTol=1.5, aTol=0.5))

    # Creating csv file with data at some probe locations
    Columns=['Time_[s]']
    Data   = ts['t']
    for y in yProbe:
        for z in zProbe:
            iy = np.argmin(np.abs(ts['y']-y))
            iz = np.argmin(np.abs(ts['z']-z))
            lbl = '_y{:.0f}_z{:.0f}'.format(ts['y'][iy], ts['z'][iz])
            Columns+=['{}{}_[m/s]'.format(c,lbl) for c in['u','v','w']]
            DataSub = np.column_stack((ts['u'][0,:,iy,iz],ts['u'][1,:,iy,iz],ts['u'][2,:,iy,iz]))
            Data    = np.column_stack((Data, DataSub))
    probefile = '{}{}{}_probes.csv'.format(OUT_Folder,Case,Suffix)
    np.savetxt(probefile, Data, header=','.join(Columns), delimiter=',')


    # As a sanity check, let's compare a simulated point that is close to a constraint point. If we did this right, they should look similar to each other.
    # find the points close to where we want to look
    if Plot:
        fig,axes = plt.subplots( 3*len(RefPoints), 1, sharex=True, figsize=(8.4,7.8)) # (6.4,4.8)
        fig.subplots_adjust(left=0.12, right=0.99, top=0.95, bottom=0.07, hspace=0.06, wspace=0.20)

        for iref in np.arange(RefPoints.shape[1]):
            xref, yref, zref = RefPoints['u_p{:d}'.format(iref)]
            yloc, zloc = yref, zref  # location we want to compare
            isim = np.argmin((sim_sp.loc['y'].values - yloc)**2+(sim_sp.loc['z'].values - zloc)**2)
            icon = np.argmin((con_sp.loc['y'].values - yloc)**2+(con_sp.loc['z'].values - zloc)**2)
            ysim,zsim = sim_sp.loc['y'].values[isim],sim_sp.loc['z'].values[isim]
            print('Con. Point ({:.1f} , {:.1f}) - Sim. Point ({:.1f} , {:.1f})'.format(yref,zref,ysim,zsim))
            sPointSim = sim_sp.columns[isim][1:]
            sPointCon = con_sp.columns[icon][1:]
            t = sim_ts.index

            for ic, c in enumerate(['u','v','w']):
                usim, ucon  = sim_ts.loc[:, c+sPointSim], con_ts.loc[:, c+sPointCon]
                # plot the time series
                axes[3*iref+ic].plot(t, usim,      label='simulated  (z={:.1f})'.format(zsim))
                axes[3*iref+ic].plot(t, ucon, 'r', label='constraint (z={:.1f})'.format(zref))
                print(c,usim.values[0],usim.values[-1])
                axes[3*iref+ic].set_ylabel(c+' [m/s]'.format(zref));
                axes[3*iref+ic].tick_params(direction='in')
                axes[3*iref+ic].autoscale(enable=True, tight=True)
            axes[3*iref].legend();
        axes[-1].set_xlabel('Time [s]');

        # Let's also check out statistics with height:
        # plot
        fig,axes = plt.subplots(3, 2, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
        fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)

        for ic, c in enumerate(['u','v','w']):
            stats     = sim_ts.filter(regex=c+'_', axis=1).describe().loc[['mean', 'std']]
            con_stats = con_ts.filter(regex=c+'_', axis=1).describe().loc[['mean', 'std']]
            axes[ic,0].scatter(    stats.loc['mean'], sim_sp.filter(regex=c+'_').loc['z'], label='Mean profile')
            axes[ic,0].scatter(con_stats.loc['mean'], con_sp.filter(regex=c+'_').loc['z'], color='k',marker='d')

            axes[ic,1].scatter(    stats.loc['std'], sim_sp.filter(regex=c+'_').loc['z'], label='Std dev')
            axes[ic,1].scatter(con_stats.loc['std'], con_sp.filter(regex=c+'_').loc['z'],color='k',marker='d')
        axes[0,0].legend()
        axes[0,1].legend();
    plt.show()
