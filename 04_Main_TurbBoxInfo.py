import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from TurbSimFile import TurbSimFile
from curve_fitting import *

Cases=['A1','A2','B1']
OutDir='_ForHenrik/'

zProbe=[17,57,93]
yProbe=[0,-107.1]

for Case in Cases:
    box_file  = '{}{}{}.bts'.format(OutDir,Case,Suffix)
    print(box_file)
    ts = TurbSimFile(box_file)

    # writing an info file
    infofile = '{}{}_info.txt'.format(Case,Suffix)
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
    probefile = '{}{}_probes.csv'.format(Case,Suffix)
    np.savetxt(probefile, Data, header=','.join(Columns), delimiter=',')


