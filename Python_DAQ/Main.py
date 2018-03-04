# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 11:11:01 AM
Last modified: Sat Mar  3 20:43:45 2018
"""
#IO1717
import os
import numpy as np
import time
import sys 
from adc_meas import LF_MEAS

lfm = LF_MEAS()
lfm.gen.ADDR = u'USB0::0x0957::0x5707::MY53801762::INSTR' #need change
lfm.msu.ADDR = u'USB0::0x0957::0x4118::MY57070006::INSTR' #need change

#set shift and phase for AD7274
chn0sft = 1 # normally don't need change
lfm.wib.adc_sft_np = [chn0sft, 2, 2, 2,   2, 2, 2, 2,   2, 2, 2, 2,   2, 2, 2, 2]
chn0pha = 3  # normally don't need change
lfm.wib.adc_phase_np = [chn0pha, 2, 2, 2,   2, 2, 2, 2,   2, 2, 2, 2,   2, 2, 2, 2]

def one_lf_cycle(savepath, t_hr= 1, chn=0, Vstress = 5.5):
    t_sec = t_hr * 3600
    print "A new lifetime cycle starts... "
    #####################################################################
    print "Characterize ADC with power supply from LDO"
    smu_chn1 = [1, 2.5, 50, 20, 120, 120, 25]
    smu_chn2 = [2, 1.8, 50, 20, 10, 10, 25]
    smu_chn3 = [3, 2.5, 50, 20, 10, 10, 25]
    smu_chns = [smu_chn1, smu_chn2, smu_chn3]
    lfm.smu_config(smu_chns)
    lfm.adc_meas(savepath,chn=0, vref=1.8, mode=lfm.mode_ldo)
    lfm.cur_meas(savepath, t = 300, mode=lfm.mode_smu)
    #####################################################################
    print "Characterize ADC with power supply from MSU"
    smu_chn1 = [1, Vstress, 50, 20, 120, 120, 25]
    smu_chn2 = [2, Vstress, 50, 20, 10, 10, 25]
    smu_chn3 = [3, Vstress, 50, 20, 10, 10, 25]
    smu_chns = [smu_chn1, smu_chn2, smu_chn3]
    lfm.smu_config(smu_chns)
    for stress_1hr in range (1, int(t_hr) + 1, 1):
        lfm.cur_meas(savepath, t = stress_1hr*3600, mode=lfm.mode_smu)
        lfm.adc_meas(savepath,chn=0, vref=Vstress, mode=lfm.mode_smu)
    print "Present lifetime cycle done... "

lf_hours = [1,1,2,2,2,2, 4,4,4,4, 4,4,4,4,8,8,8,8, 8,8,8,8, 8,8,8,8, 8,8,8,8,\
            16, 16, 16, 16,  16, 16, 16, 16, 16, 16, 16, 16,  16, 16, 16, 16,\
            16, 16, 16, 16,  16, 16, 16, 16, 16, 16, 16, 16,  16, 16, 16, 16,\
            16, 16, 16, 16,  16, 16, 16, 16, 16, 16, 16, 16,  16, 16, 16, 16,\
            16, 16, 16, 16,  16, 16, 16, 16, 16, 16, 16, 16,  16, 16, 16, 16,\
            16, 16, 16, 16,  16, 16, 16, 16, 16, 16, 16, 16,  16, 16, 16, 16]

chippn = sys.argv[1]  #AD7274
chipno = sys.argv[2]  #001
chipchn =  int(sys.argv[3])
stress_hours =  int(sys.argv[4]) # duration request for stress test  
Vstress =  float(sys.argv[5])

if Vstress > 6 :
    print "Error: Stress Voltage should be no more than 6V. Exit anyway!"
    sys.exit()

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

Tpassed = 0
for lf_hr in lf_hours:
    one_lf_cycle(savepath, t_hr= lf_hr, chn=chipchn, Vstress = Vstress)
    Tpassed = Tpassed + lf_hr
    if (Tpassed >= stress_hours):
        print "Entire stress has done"
        break
    else:
        print "Have been stressed %d hours"%stress_hours

lfm.meas_close()

