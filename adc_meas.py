# -*- coding: utf-8 -*-
"""
File Name: adc_meas.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 11:11:42 AM
Last modified: 1/9/2018 9:53:26 AM
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
from msu_u2722a import MSU_CTL
from wib_ctl import WIB_CTL
from timeit import default_timer as timer
from shutil import copyfile

class LF_MEAS:
    def gen_msu_config(self, msu_chns, gen_chns):
        msu_chn1 = msu_chns[0]
        msu_chn2 = msu_chns[1]
        msu_chn3 = msu_chns[2]
        gen_chn1 = gen_chns[0]
        gen_chn2 = gen_chns[1]

        self.msu.msu_chn_on( chn=msu_chn1[0], volt=msu_chn1[1], sysflt=msu_chn1[2], \
                        vrange=msu_chn1[3], crange=msu_chn1[4], clim=msu_chn1[5], nplc=msu_chn1[6])
        self.msu.msu_chn_on( chn=msu_chn2[0], volt=msu_chn2[1], sysflt=msu_chn2[2], \
                        vrange=msu_chn2[3], crange=msu_chn2[4], clim=msu_chn2[5], nplc=msu_chn2[6])
        self.msu.msu_chn_on( chn=msu_chn3[0], volt=msu_chn3[1], sysflt=msu_chn3[2], \
                        vrange=msu_chn3[3], crange=msu_chn3[4], clim=msu_chn3[5], nplc=msu_chn3[6])
        self.gen.gen_set(chn=gen_chn1[0], wave_type=gen_chn1[1], freq=gen_chn1[2], \
                    amp=gen_chn1[3], dc_oft=gen_chn1[4], load=gen_chn1[5])
        self.gen.gen_set(chn=gen_chn2[0], wave_type=gen_chn2[1], freq=gen_chn2[2], \
                    amp=gen_chn2[3], dc_oft=gen_chn2[4], load=gen_chn2[5])

    def meas_init(self):
        print "Initazation start ..."
        self.wib.wib_init()
        self.msu.msu_init()
        self.gen.gen_init()

        self.wib.WIB_UDP_CTL(WIB_UDP_EN = True)
        self.wib.FEMB_INIT()
        msu_chn1 = [1, 1.8, 50, 20, 10, 10, 25]
        msu_chn2 = [2, 6.0, 50, 20, 120, 120, 25]
        msu_chn3 = [3, 2.5, 50, 20, 10, 10, 25]
        msu_chns = [msu_chn1, msu_chn2, msu_chn3]
        gen_chn1 = [1,"DC",       "DEF"  , "DEF", "5",   "INF"]
        gen_chn2 = [2,"DC",       "DEF"  , "DEF", "0.9", "50" ]
        gen_chns = [gen_chn1, gen_chn2]
        self.gen_msu_config(msu_chns, gen_chns)
        print "Initazation DONE ..."

    def msu_rec(self,savepath, mode=0):
        recchn1= self.msu.msu_meas(chn=1, mode=mode)
        recchn2= self.msu.msu_meas(chn=2, mode=mode)
        recchn3= self.msu.msu_meas(chn=3, mode=mode)

        f1 = savepath + "Protected_" + self.msuchn1_recf
        recchn1_str = "{},{},{},{},{},\n".format(recchn1[0], recchn1[1], recchn1[2], recchn1[3], recchn1[4])
        print recchn1_str
        try:
            with open(f1,"a+") as f:
                f.write(recchn1_str) 
        except IOError:
            print "%s was open by other App, please close it"%f1
            pass

        f2 = savepath + "Protected_" + self.msuchn2_recf
        recchn2_str = "{},{},{},{},{},\n".format(recchn2[0], recchn2[1], recchn2[2], recchn2[3], recchn2[4])
        print recchn2_str
        try:
            with open(f2,"a+") as f:
                f.write(recchn2_str) 
        except IOError:
            print "%s was open by other App, please close it"%f2
            pass

        f3 = savepath + "Protected_" + self.msuchn3_recf
        recchn3_str = "{},{},{},{},{},\n".format(recchn3[0], recchn3[1], recchn3[2], recchn3[3], recchn3[4])
        print recchn3_str
        try:
            with open(f3,"a+") as f:
                f.write(recchn3_str) 
        except IOError:
            print "%s was open by other App, please close it"%f3
            pass

        return f1, f2, f3

    def msu_rec_file(self, savepath, t = 60, mode=0):
        start = timer()
        while ( timer() - start < t ):
            f1, f2, f3 = self.msu_rec(savepath, mode=mode)
        try:
            copyfile(f1, savepath + self.msuchn1_recf)
        except:
            pass
        try:
            copyfile(f2, savepath + self.msuchn2_recf)
        except:
            pass
        try:
            copyfile(f3, savepath + self.msuchn3_recf)
        except:
            pass


    def adc_meas(self,savepath,chn=0):
        if (self.autoflg == True):
            print "ADC DNL/INL characterization start ..."
            msu_chn1 = [1, 1.8, 50, 20, 10, 10, 25]
            msu_chn2 = [2, 6.0, 50, 20, 120, 120, 25]
            msu_chn3 = [3, 2.5, 50, 20, 10, 10, 25]
            msu_chns = [msu_chn1, msu_chn2, msu_chn3]
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "5",   "INF"]
            gen_chn2 = [2,"DC",       "DEF"  , "DEF", "0.9", "50" ]
            gen_chns = [gen_chn1, gen_chn2]
            self.gen_msu_config(msu_chns, gen_chns)
            print "Configuration done, please wait for 30seconds..."
            self.wib.Analog_SW_SET(SW=0)
            time.sleep(30)

            print "~2 minutes to measure Current with ADC.SDO floating" 
            self.msu_rec_file(savepath, t = 2*60, mode=self.LDO_WO_SDO)

            print "Switch SDO to FPGA, please wait for 30seconds..."
            self.wib.Analog_SW_SET(SW=1)
            time.sleep(30)
            print "~5 minutes to measure Current with ADC.SDO floating" 
            self.msu_rec_file(savepath, t = 5*60, mode=self.LDO_W_SDO)

            print "Start collecting data, please wait for 30 seconds"
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "5",   "INF"]
            gen_chn2 = [2,"TRIangle", "0.1Hz", "2",   "0.9", "50" ]
            gen_chns = [gen_chn1, gen_chn2]
            self.gen_msu_config(msu_chns, gen_chns)
            time.sleep(30)
            print "Start collecting data, please wait for several minutes"
            self.wib.WIB_UDP_CTL(WIB_UDP_EN = True)
            self.wib.ADC_ACQ(savepath=savepath,  t_sec=22, chn=chn )
            print "ADC DNL/INL characterization DONE!"
        else:
            print "ADC DNL/INL characterization start ..."
            print "Please connect COTS ADC test board with LDOs boards"
            yn = "n" 
            while ( yn != "y" ):
                yn = raw_input("Hareware setting is correct? (y/n):   ")
                if (yn == "y" ):
                    break
                elif (yn == "n" ):
                    print "Please connect COTS ADC test board with LDOs boards"
                elif (yn == "q" ):
                    print "Stop and quit anyway!!!"
                    sys.exit()
                else:
                    print "Wrong input, please input: y   or  n   or q"
                    print "if you input q, the scripts will stop immediately"

            print "Please plug LDOs to SMU CHN2, unplug cables on SMU CHN1 and CHN3"
            yn = "n" 
            while ( yn != "y" ):
                yn = raw_input("Hareware setting is correct? (y/n):   ")
                if (yn == "y" ):
                    break
                elif (yn == "n" ):
                    print "Please plug LDOs to SMU CHN2, unplug cables on SMU CHN1 and CHN3"
                elif (yn == "q" ):
                    print "Stop and quit anyway!!!"
                    sys.exit()
                else:
                    print "Wrong input, please input: y   or  n   or q"
                    print "if you input q, the scripts will stop immediately"

            msu_chn1 = [1, 1.8, 50, 20, 10, 10, 25]
            msu_chn2 = [2, 6.0, 50, 20, 120, 120, 25]
            msu_chn3 = [3, 2.5, 50, 20, 10, 10, 25]
            msu_chns = [msu_chn1, msu_chn2, msu_chn3]
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "5",   "INF"]
            gen_chn2 = [2,"DC",       "DEF"  , "DEF", "0.9", "50" ]
            gen_chns = [gen_chn1, gen_chn2]
            self.gen_msu_config(msu_chns, gen_chns)
            print "Configuration done"
            print "wait for 1 minutes to measure currents" 
            self.msu_rec_file(savepath, t = 60, mode=self.LDO_WO_SDO)
            print "Start collecting data, please wait for 30 seconds"
            gen_chn1 = [1,"DC",       "DEF"  , "DEF", "5",   "INF"]
            gen_chn2 = [2,"TRIangle", "0.1Hz", "2",   "0.9", "50" ]
            gen_chns = [gen_chn1, gen_chn2]
            self.gen_msu_config(msu_chns, gen_chns)
            time.sleep(30)
            print "wait for 1 minutes to measure currents" 
            self.msu_rec_file(savepath, t = 5*60, mode=self.LDO_W_SDO)
            print "Start collecting data, please wait for several minutes"
            self.wib.WIB_UDP_CTL(WIB_UDP_EN = True)
            self.wib.ADC_ACQ(savepath=savepath,  t_sec=22, chn=chn )
            print "ADC DNL/INL characterization DONE!"

    def cur_meas(self, savepath, Vchn1=1.8, Vchn2=6.0, Vchn3=2.5, t = 20*60, mode=3):
        print "ADC stress test starts ..."
        print "Please make sure R3 has been removed if you are running stress test with voltage higher than 2.5V"
        print "Please connect COTS ADC test board to SMU directly"
        print "1.8V(Vref) <--> SMU.CHN1, 2.5V(VCC) <--> SMU.CHN3"
        yn = "n" 
        while ( yn != "y" ):
            yn = raw_input("Hareware setting is correct? (y/n):   ")
            if (yn == "y" ):
                break
            elif (yn == "n" ):
                print "Please make sure R3 has been removed if you are running stress test with voltage higher than 2.5V"
                print "Please connect COTS ADC test board to SMU directly"
                print "1.8V(Vref) <--> SMU.CHN1, 2.5V(VCC) <--> SMU.CHN3"
            elif (yn == "q" ):
                print "Stop and quit anyway!!!"
                sys.exit()
            else:
                print "Wrong input, please input: y   or  n   or q"
                print "if you input q, the scripts will stop immediately"

        msu_chn1 = [1, Vchn1, 50, 20, 10, 10, 25]
        msu_chn2 = [2, Vchn2, 50, 20, 120, 120, 25]
        msu_chn3 = [3, Vchn3, 50, 20, 10, 10, 25]
        msu_chns = [msu_chn1, msu_chn2, msu_chn3]
        gen_chn1 = [1,"DC",       "DEF"  , "DEF", "0",   "INF"]
        gen_chn2 = [2,"DC",       "DEF"  , "DEF", "0.9", "50" ]
        gen_chns = [gen_chn1, gen_chn2]
        self.gen_msu_config(msu_chns, gen_chns)
        print "Configuration done, please wait for 30seconds..."
        self.wib.Analog_SW_SET(SW=0)
        time.sleep(30)
        print "Current Recording starts, will last %d minutes..."%(t/60)
        self.msu_rec_file(savepath, t = t, mode=mode)
        print "ADC stress test done ..."

    #__INIT__#
    def __init__(self):
        self.gen = GEN_CTL()
        self.msu = MSU_CTL() 
        self.wib = WIB_CTL()
        self.msuchn1_recf =  "MSU_CHN1_Rec.csv"
        self.msuchn2_recf =  "MSU_CHN2_Rec.csv"
        self.msuchn3_recf =  "MSU_CHN3_Rec.csv"
        self.LDO_WO_SDO = 1 #6V LDO output, SDO disconnected from FPGA
        self.LDO_W_SDO = 2 #6V LDO output, SDO connected from FPGA
        self.MSU_NOR = 3 #MSU normal supply (2.5V, 1.8V)
        self.MSU_STRESS = 4 #MSU stress voltage (2.5V, 1.8V)
        self.autoflg = False

    def meas_close(self):
        print "Close..."
        print "SCK and SCS to ground..."
        self.wib.ADC_close()
        print "MSU output off..."
        self.msu.msu_chn_off(chn=1)
        self.msu.msu_chn_off(chn=2)
        self.msu.msu_chn_off(chn=3)
        print "Generator output off..."
        self.gen.gen_chn_sw(chn=1, SW="OFF")
        self.gen.gen_chn_sw(chn=2, SW="OFF")
        print "DONE ..."


#savepath = "D:/temp/"
#a = LF_MEAS()
#a.meas_init()
#a.adc_meas(savepath)
#a.cur_meas(savepath, Vchn1=1.8, Vchn2=6.0, Vchn3=2.5, t = 2*60, mode=a.MSU_NOR)
#a.cur_meas(savepath, Vchn1=5,   Vchn2=6.0, Vchn3=5,   t = 2*60, mode=a.MSU_STRESS)
#a.msu_rec(savepath, mode=a.LDO_WO_SDO)
