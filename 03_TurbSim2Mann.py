import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Local 
# import weio
from TurbSimFile import TurbSimFile
from MannBoxFile import MannBoxFile


Cases=['A1','A2','B1']
OutDir='_ForHenrik/'
for Case in Cases:
    Suffix='_161'

    ts_filename='{}{}{}.bts'.format(OutDir,Case,Suffix)
    print('Reading TurbSim')
    ts=TurbSimFile(ts_filename)

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






