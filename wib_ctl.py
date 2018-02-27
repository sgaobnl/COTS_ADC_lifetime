# -*- coding: utf-8 -*-
"""
File Name: wib_ctl.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 11:11:28 AM
Last modified: Mon Feb 26 23:39:52 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl


import os
import sys
import copy
from datetime import datetime
from raw_convertor_m import raw_convertor
import numpy as np
import math
import time
import struct

from femb_udp_cmdline import FEMB_UDP

class WIB_CTL:
    def wib_init(self):
        #check WIB emulator
        wib_ip = self.wib_ip_info[0]
        ip_address = self.wib_ip_info[1] 

        self.udp.write_reg_wib (0x101, self.wib_ver_id)
        self.udp.write_reg_wib (0x101, self.wib_ver_id)
        time.sleep(0.1)
        ver_value = self.udp.read_reg_wib (0x101)
        time.sleep(0.1)
        ver_value = self.udp.read_reg_wib (0x101)

        if ( (ver_value) == (self.wib_ver_id) ):
            print "WIB%d(%s) passed self check!"%(wib_ip, ip_address)
            pass
        else:
            print "WIB%d fails, exit!!!"%self.wib_ip_info[0]
            sys.exit()
        if (self.jumbo_flag):
            jumbo_size = 0xEFB
        else:
            jumbo_size = 0x1FB
        self.udp.write_reg_wib_checked (0x1F, jumbo_size)

    def FEMB_STREAM_CTL(self,  one_femb_stream_en=False, switch=True,):
        if (one_femb_stream_en):
            reg_9_value = self.udp.read_reg_femb(self.fembno, 9)
            reg_9_value = self.udp.read_reg_femb(self.fembno, 9)
            if (switch):
                reg_9_value = reg_9_value | 0x00000001
            else:
                reg_9_value = reg_9_value & 0xFFFFFFFE
            self.udp.write_reg_femb_checked (self.fembno, 9, reg_9_value)
        else:
            pass

    def WIB_UDP_CTL(self, WIB_UDP_EN = False):
        wib_reg_7_value = self.udp.read_reg_wib (7)
        time.sleep(0.001)
        wib_reg_7_value = self.udp.read_reg_wib (7)
        if (WIB_UDP_EN):
        #enable UDP output
            wib_reg_7_value = wib_reg_7_value & 0x00000000 #bit31 of reg 7 for disable wib udp control
        else:
        #disable WIB UDP output
            wib_reg_7_value = wib_reg_7_value | 0x80000000 #bit31 of reg 7 for disable wib udp control
        self.udp.write_reg_wib_checked (7, wib_reg_7_value)
        time.sleep(0.01)    

    def FEMB_INIT(self ):
        ver_value = self.udp.read_reg_femb (self.fembno, 0x101)
        time.sleep(0.1)
        ver_value = self.udp.read_reg_femb (self.fembno, 0x101)
        if ( (ver_value &0xff0) == (self.femb_ver_id&0xff0) ):
            print "FEMB#%d detected!"%self.fembno
            pass
        else:
            print "FEMB#%d NOT detected!"%self.fembno
            print "Please check connection! Exit anyway"
            sys.exit()
        self.udp.write_reg_femb_checked (self.fembno, 9, 0)
        self.udp.write_reg_femb_checked (self.fembno, 9, 9)

    def Analog_SW_SET(self, SW = 0 ):
        if (SW == 0):
            self.udp.write_reg_femb_checked (self.fembno, 0x11, 0)
        else:
            self.udp.write_reg_femb_checked (self.fembno, 0x11, 1)
        time.sleep(1)

    def ADC_SET(self, chn=0x0 ):
#        #set sample rate
        adc_str = ""
        if (self.MSPS == 2) :
            adc_str = adc_str + "1MSPS"
            self.udp.write_reg_femb_checked (self.fembno, 1, self.MSPS)
        elif (self.MSPS == 1) :
            adc_str = adc_str + "2MSPS"
            self.udp.write_reg_femb_checked (self.fembno, 1, self.MSPS)
        #ad7274
        ad7274_sft = ((self.adc_sft_np[0]&0x03) <<0 ) + \
                     ((self.adc_sft_np[1]&0x03) <<4 ) + \
                     ((self.adc_sft_np[2]&0x03) <<8 ) + \
                     ((self.adc_sft_np[3]&0x03) <<12) + \
                     ((self.adc_sft_np[4]&0x03) <<16)
        ad7274_phase = ((self.adc_phase_np[0]&0x03) <<0  ) + \
                       ((self.adc_phase_np[1]&0x03) <<4  ) + \
                       ((self.adc_phase_np[2]&0x03) <<8  ) + \
                       ((self.adc_phase_np[3]&0x03) <<12 ) + \
                       ((self.adc_phase_np[4]&0x03) <<16 )
        #ads7883
        ads7883_sft = ((self.adc_sft_np[5]&0x03) <<0  ) + \
                      ((self.adc_sft_np[6]&0x03) <<4  ) + \
                      ((self.adc_sft_np[7]&0x03) <<8  ) + \
                      ((self.adc_sft_np[8]&0x03) <<12 ) + \
                      ((self.adc_sft_np[9]&0x03) <<16 )
        ads7883_phase = ((self.adc_phase_np[5]&0x03) <<0  ) + \
                        ((self.adc_phase_np[6]&0x03) <<4  ) + \
                        ((self.adc_phase_np[7]&0x03) <<8  ) + \
                        ((self.adc_phase_np[8]&0x03) <<12 ) + \
                        ((self.adc_phase_np[9]&0x03) <<16 )
        #ads7049
        ads7049_sft = ((self.adc_sft_np[10]&0x03) <<0  ) + \
                      ((self.adc_sft_np[11]&0x03) <<4  ) + \
                      ((self.adc_sft_np[12]&0x03) <<8  ) + \
                      ((self.adc_sft_np[13]&0x03) <<12 ) + \
                      ((self.adc_sft_np[14]&0x03) <<16 ) + \
                      ((self.adc_sft_np[15]&0x03) <<20 )
        ads7049_phase = ((self.adc_phase_np[10]&0x03) <<0  ) + \
                        ((self.adc_phase_np[11]&0x03) <<4  ) + \
                        ((self.adc_phase_np[12]&0x03) <<8  ) + \
                        ((self.adc_phase_np[13]&0x03) <<12 ) + \
                        ((self.adc_phase_np[14]&0x03) <<16 ) + \
                        ((self.adc_phase_np[15]&0x03) <<20 )

        self.udp.write_reg_femb_checked (self.fembno, 3, ad7274_sft)
        self.udp.write_reg_femb_checked (self.fembno, 6, ad7274_phase)
        self.udp.write_reg_femb_checked (self.fembno, 4, ads7883_sft)
        self.udp.write_reg_femb_checked (self.fembno, 7, ads7883_phase)
        self.udp.write_reg_femb_checked (self.fembno, 5, ads7049_sft)
        self.udp.write_reg_femb_checked (self.fembno, 8, ads7049_phase)
        self.udp.write_reg_femb_checked (self.fembno, 10, 0x100000)

        chn_cs = (1 << chn)
        chn_csn = ((chn_cs ^ 0xFFFF) & 0xFFFF)
        self.udp.write_reg_femb_checked (self.fembno, 13, chn_csn)

        adc_str = "CHN" + format(chn, '1X') + "_" + adc_str + "_SFT" + \
                  format(self.adc_sft_np[chn], '1d') + "_Phase" + format(self.adc_phase_np[chn], '1d')
        return adc_str

    def ADC_close(self ):
        chn_csn = 0xFFFF
        self.udp.write_reg_femb_checked (self.fembno, 13, chn_csn)
        self.udp.write_reg_femb_checked (self.fembno, 0x11, 0)

    def selectasic_femb(self):
        self.udp.write_reg_wib (7, 0x80000000)
        self.udp.write_reg_wib (7, 0x80000000)
        self.udp.write_reg_wib (7, 0x80000000)
        femb_asic = self.asicno & 0x0F
        self.udp.write_reg_femb_checked ( self.fembno, 7, femb_asic)
        self.udp.write_reg_femb_checked ( self.fembno, 17, 1)
        wib_asic =  ( ((self.fembno << 16)&0x000F0000) + ((femb_asic << 8) &0xFF00) )
        self.udp.write_reg_wib (7, wib_asic | 0x80000000)
        self.udp.write_reg_wib (7, wib_asic | 0x80000000)
        self.udp.write_reg_wib (7, wib_asic | 0x80000000)
        self.udp.write_reg_wib (7, wib_asic)
        self.udp.write_reg_wib (7, wib_asic)
        self.udp.write_reg_wib (7, wib_asic)
        self.udp.write_reg_wib (7, wib_asic)
        time.sleep(0.001)

    def ADC_ACQ(self, savepath, t_sec=22, chn = 0, mode=1 ):
        self.MSPS = 2 #1MSPS
        adc_str = self.ADC_SET(chn=chn)
        self.selectasic_femb()
        smps = int(adc_str[adc_str.find("MSPS")-1]) * 1000000
        if (self.jumbo_flag == True):
            val = long( (t_sec*smps)/(295) )
        else:
            val = long( (t_sec*smps)/(39) )
        timestampe =  datetime.now().strftime('%m%d%Y_%H%M%S')
        rawfilep = savepath + "/" + adc_str + "_" + timestampe + ".bin"
        print rawfilep
        rawdata = None
        rawdata = self.udp.get_rawdata_packets(val, self.jumbo_flag)
        if rawdata != None:
            with open(rawfilep,"wb") as f:
                f.write(rawdata) 
        else:
            print "No data has been collected!, please check!!"
            print "Exit anyway!!!"
            sys.exit()

        self.MSPS = 1 #2MSPS
        adc_str = self.ADC_SET(chn=chn)
        self.selectasic_femb()
        smps = int(adc_str[adc_str.find("MSPS")-1]) * 1000000
        if (self.jumbo_flag == True):
            val = long( (t_sec*smps)/(295) )
        else:
            val = long( (t_sec*smps)/(39) )
        timestampe =  datetime.now().strftime('%m%d%Y_%H%M%S')
        if (mode == 1):
            rawfilep = savepath + "/" + "LDO_" + adc_str + "_" + timestampe + ".bin"
        else
            rawfilep = savepath + "/" + "SMU_" + adc_str + "_" + timestampe + ".bin"
        print rawfilep
        rawdata = None
        rawdata = self.udp.get_rawdata_packets(val, self.jumbo_flag)
        if rawdata != None:
            with open(rawfilep,"wb") as f:
                f.write(rawdata) 
        else:
            print "No data has been collected!, please check!!"
            print "Exit anyway!!!"
            sys.exit()

    #__INIT__#
    def __init__(self):
        self.wib_ip_info = [1, "192.168.121.1"]
        self.jumbo_flag =True
        self.udp = FEMB_UDP()
        self.udp.UDP_IP = self.wib_ip_info[1]
        self.wib_ver_id = 0x001
        self.fembno = 0
        self.asicno = 0
        self.femb_ver_id = 0x204
        self.MSPS = 1 #1 --> 2M, 2 --> 1 M
        self.adc_sft_np = [1, 2, 2, 2,   2, 2, 2, 2,   2, 2, 2, 2,   2, 2, 2, 2]
        self.adc_phase_np = [3, 1, 1, 1,   1, 1, 1, 1,   1, 1, 1, 1,   1, 1, 1, 1]

###wib = WIB_CTL()
###wib.wib_init()
#####wib.WIB_UDP_CTL(WIB_UDP_EN = False)
###wib.WIB_UDP_CTL(WIB_UDP_EN = True)
#######wib.FEMB_STREAM_CTL()
###wib.FEMB_INIT()
###wib.ADC_ACQ(savepath="d:/",  t_sec=22 )
####wib.WIB_UDP_CTL(WIB_UDP_EN = False)
