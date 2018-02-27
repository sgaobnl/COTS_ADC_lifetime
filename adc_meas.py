# -*- coding: utf-8 -*-
"""
File Name: adc_meas.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 11:11:42 AM
Last modified: Mon Feb 26 23:38:01 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl


import struct
import sys 
import string
import time
import copy
import datetime

from gen_33622a import GEN_CTL
from smu_u2722a import SMU_CTL
from wib_ctl import WIB_CTL
from timeit import default_timer as timer
from shutil import copyfile

class LF_MEAS:
   def gen_config(self, gen_chns):
        gen_chn1 = gen_chns[0]
        gen_chn2 = gen_chns[1]
        self.gen.gen_set(chn=gen_chn1[0], wave_type=gen_chn1[1], freq=gen_chn1[2], \
                    amp=gen_chn1[3], dc_oft=gen_chn1[4], load=gen_chn1[5])
        self.gen.gen_set(chn=gen_chn2[0], wave_type=gen_chn2[1], freq=gen_chn2[2], \
                    amp=gen_chn2[3], dc_oft=gen_chn2[4], load=gen_chn2[5])

    def smu_config(self, smu_chns):
        smu_chn1 = smu_chns[0]
        smu_chn2 = smu_chns[1]
        smu_chn3 = smu_chns[2]
        self.smu.smu_chn_on( chn=smu_chn1[0], volt=smu_chn1[1], sysflt=smu_chn1[2], \
                        vrange=smu_chn1[3], crange=smu_chn1[4], clim=smu_chn1[5], nplc=smu_chn1[6])
        self.smu.smu_chn_on( chn=smu_chn2[0], volt=smu_chn2[1], sysflt=smu_chn2[2], \
                        vrange=smu_chn2[3], crange=smu_chn2[4], clim=smu_chn2[5], nplc=smu_chn2[6])
        self.smu.smu_chn_on( chn=smu_chn3[0], volt=smu_chn3[1], sysflt=smu_chn3[2], \
                        vrange=smu_chn3[3], crange=smu_chn3[4], clim=smu_chn3[5], nplc=smu_chn3[6])
        time.sleep(10)

    def gen_smu_config(self, smu_chns, gen_chns):
        gen_config( gen_chns)
        smu_config( smu_chns)
 
    def meas_init(self):
        print "Initazation start ..."
        self.wib.wib_init()
        self.smu.smu_init()
        self.gen.gen_init()

        self.wib.WIB_UDP_CTL(WIB_UDP_EN = True)
        self.wib.FEMB_INIT()
        smu_chn1 = [1, 2.5, 50, 20, 10, 10, 25]
        smu_chn2 = [2, 1.8, 50, 20, 10, 10, 25]
        smu_chn3 = [3, 2.5, 50, 20, 10, 10, 25]
        smu_chns = [smu_chn1, smu_chn2, smu_chn3]
        gen_chn1 = [1,"DC",       "DEF"  , "DEF", "0",   "INF"]
        gen_chn2 = [2,"TRIangle", "1Hz", "1",   "0.6", "50" ]
        gen_chns = [gen_chn1, gen_chn2]
        self.gen_smu_config(smu_chns, gen_chns)
        print "Initazation DONE ..."

    def smu_rec(self,savepath, mode=0):
        recchn1= self.smu.smu_meas(chn=1, mode=mode)
        recchn2= self.smu.smu_meas(chn=2, mode=mode)
        recchn3= self.smu.smu_meas(chn=3, mode=mode)

        f1 = savepath + "Protected_" + self.smuchn1_recf
        recchn1_str = "{},{},{},{},{},\n".format(recchn1[0], recchn1[1], recchn1[2], recchn1[3], recchn1[4])
        print recchn1_str
        try:
            with open(f1,"a+") as f:
                f.write(recchn1_str) 
        except IOError:
            print "%s was open by other App, please close it"%f1
            pass

        f2 = savepath + "Protected_" + self.smuchn2_recf
        recchn2_str = "{},{},{},{},{},\n".format(recchn2[0], recchn2[1], recchn2[2], recchn2[3], recchn2[4])
        print recchn2_str
        try:
            with open(f2,"a+") as f:
                f.write(recchn2_str) 
        except IOError:
            print "%s was open by other App, please close it"%f2
            pass

        f3 = savepath + "Protected_" + self.smuchn3_recf
        recchn3_str = "{},{},{},{},{},\n".format(recchn3[0], recchn3[1], recchn3[2], recchn3[3], recchn3[4])
        print recchn3_str
        try:
            with open(f3,"a+") as f:
                f.write(recchn3_str) 
        except IOError:
            print "%s was open by other App, please close it"%f3
            pass

        return f1, f2, f3

    def smu_rec_file(self, savepath, t = 60, mode=0):
        start = timer()
        while ( timer() - start < t ):
            f1, f2, f3 = self.smu_rec(savepath, mode=mode)
        try:
            copyfile(f1, savepath + self.smuchn1_recf)
        except:
            pass
        try:
            copyfile(f2, savepath + self.smuchn2_recf)
        except:
            pass
        try:
            copyfile(f3, savepath + self.smuchn3_recf)
        except:
            pass


    def adc_meas(self,savepath,chn=0, vref=1.8, mode=1):
        print "ADC DNL/INL characterization start ..."
        print "Characterize ADC with power supply from LDO"
        print "Configurate Generator ..."
        if (mode == self.LDO):
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "0",   "INF"]
        elif (mode == self.mode_smu):
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "5",   "INF"]
        else:
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "0",   "INF"]
        gen_amp = vref + 0.2
        gen_oft = (gen_amp / 2.0 ) - 0.1
        gen_chn2 = [2,"TRIangle", "0.1Hz", "{}".format(gen_amp),  "{}".format(gen_oft), "INF" ]
        gen_chns = [gen_chn1, gen_chn2]
        self.gen_config(gen_chns)
        print "Wait 30 seconds ..."
        time.sleep(30)
        print "Start collecting data, please wait for several minutes"
        self.wib.WIB_UDP_CTL(WIB_UDP_EN = True)
        self.wib.ADC_ACQ(savepath=savepath,  t_sec=22, chn=chn, mode =mode )
        time.sleep(5)
        print "ADC DNL/INL characterization DONE!"


    def cur_meas(self, savepath, t =60, mode=1):
        if (mode == self.LDO):
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "0",   "INF"]
        elif (mode == self.mode_smu):
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "5",   "INF"]
        else:
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "0",   "INF"]

            gen_chn2 = [2,"TRIangle", "1Hz", "1",   "0.6", "50" ]
        gen_chns = [gen_chn1, gen_chn2]
        self.gen_config(smu_chns, gen_chns)
        print "Configuration done, please wait for 30seconds..."
        time.sleep(30)
        print "Current Recording starts, will last %d minutes..."%(t/60)
        self.smu_rec_file(savepath, t = t, mode=mode)
        print "ADC stress test done ..."

    #__INIT__#
    def __init__(self):
        self.gen = GEN_CTL()
        self.smu = SMU_CTL() 
        self.wib = WIB_CTL()
        self.smuchn1_recf =  "SMU_CHN1_Rec.csv"
        self.smuchn2_recf =  "SMU_CHN2_Rec.csv"
        self.smuchn3_recf =  "SMU_CHN3_Rec.csv"
        self.mode_ldo = 1 
        self.mode_smu = 2 


    def meas_close(self):
        print "Close..."
        print "SCK and SCS to ground..."
        self.wib.ADC_close()
        print "SMU output off..."
        self.smu.smu_chn_off(chn=1)
        self.smu.smu_chn_off(chn=2)
        self.smu.smu_chn_off(chn=3)
        print "Generator output off..."
        self.gen.gen_chn_sw(chn=1, SW="OFF")
        self.gen.gen_chn_sw(chn=2, SW="OFF")
        print "DONE ..."


