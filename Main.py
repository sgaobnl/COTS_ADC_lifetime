# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 11:11:01 AM
Last modified: 1/9/2018 9:09:03 AM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl


import os
import numpy as np
import time
import sys 
from adc_meas import LF_MEAS

lfm = LF_MEAS()
def one_lf_cycle(savepath, t_min= 60, chn=0):
    t_sec = t_min * 60
    print "A new lifetime cycle starts... "

    lfm.adc_meas(savepath, chn=chn)

    lfm.cur_meas(savepath, Vchn1=1.8, Vchn2=6.0, Vchn3=2.5, t = 10*60, mode=lfm.MSU_NOR)
    lfm.cur_meas(savepath, Vchn1=5.5,   Vchn2=6.0, Vchn3=5.5,   t = t_sec, mode=lfm.MSU_STRESS)
    lfm.cur_meas(savepath, Vchn1=1.8, Vchn2=6.0, Vchn3=2.5, t = 10*60, mode=lfm.MSU_NOR)

    lfm.adc_meas(savepath, chn=chn)
    print "A lifetime cycle done... "

lf_hours = [1,1,2,2,2,2, 4,4,4,4, 4,4,4,4,8,8,8,8, 8,8,8,8, 8,8,8,8, 8,8,8,8,16, 16, 16, 16,  16, 16, 16, 16, 16, 16, 16, 16,  16, 16, 16, 16 ] 
lf_mins = np.array(lf_hours) * 60
chippn = sys.argv[1]  #AD7274
chipno = sys.argv[2]  #001
chipchn =  int(sys.argv[3])

savepath = "D:/COTS_ADC_LF/Rawdata/" + chippn +"_" + chipno + "/"
if os.path.exists(savepath):
    print "Folder exist, please check!"
    ow_flg = raw_input("Overwrite ? (y/n) : ")
    if (ow_flg == "y"):
        pass
    else:
        raise
else:
    try: 
        os.makedirs(savepath)
    except OSError:
        print "Cannot make the folder!"
        raise

lfm.meas_init()
for lf_min in lf_mins:
    one_lf_cycle(savepath, t_min= lf_min, chn=chipchn)

lfm.meas_close()

