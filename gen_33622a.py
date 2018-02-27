# -*- coding: utf-8 -*-
"""
File Name: gen_33622a.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 11:11:14 AM
Last modified: 12/22/2017 11:11:16 AM
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

import visa
from visa import VisaIOError

class GEN_CTL:
    def gen_init(self):
        rm = visa.ResourceManager()
        rm_list = rm.list_resources()
        try:
            rm_list.index(self.ADDR)
            print "Keysignt 33622A generaotr (%s) is locacted"%self.ADDR
        except ValueError:
            print "Keysignt 33622A generaotr (%s) is not found, Please check!"%self.ADDR
            print "Exit anyway!"
            sys.exit()
        try:
            gen = rm.open_resource(self.ADDR)
        except VisaIOError:
            print ("Keysight Initialize--> Exact system name not found")
            print "Exit anyway!"
            sys.exit()
        self.gen = gen


    def gen_set(self, chn, wave_type, freq, amp, dc_oft, load="INF"):
        self.gen.write('Output{}:Load {}'.format(chn, load))
        cmd_str = 'Source{}:Apply:{} {},{},{}'.format(chn,wave_type, freq, amp, dc_oft)
        self.gen.write(cmd_str)
        rb_cmd_str = self.gen.query('Source{}:Apply?'.format(chn))
        print "Write: CHN{},Wave_type={}, freq={}, amp={}, dc_oft={}, load={}".format(chn, wave_type, freq, amp, dc_oft, load)
        print "Readback: " + rb_cmd_str
#        rb_wave_type= self.gen.query('Source{}:{}'.format(chn, 'Function?'))
#        rb_freq     = self.gen.query_ascii_values('Source{}:{}'.format(chn, 'Frequency?'))
#        rb_amp      = self.gen.query_ascii_values('Source{}:{}'.format(chn, 'Volt?'))
#        rb_dc_oft   = self.gen.query_ascii_values('Source{}:Volt:{}'.format(chn, 'Offset?'))
        

    def gen_chn_sw(self, chn, SW="OFF"):
        self.gen.write('Output{} {}'.format(chn, SW))
        rb_sw = self.gen.query_ascii_values("Output{}?".format(chn))
        print "CHN{}, SW_write = {}, SW_readback = {}".format(chn, SW, rb_sw)


    #__INIT__#
    def __init__(self):
        self.ADDR = u'USB0::0x0957::0x5707::MY53801762::INSTR'
        self.gen = None

#gen_ctl = GEN_CTL()
#gen_ctl.gen_init()
#gen_ctl.gen_set(chn=1, wave_type="DC", freq="DEF", amp="DEF", dc_oft="5", load="INF")
#gen_ctl.gen_set(chn=2, wave_type="TRIangle", freq="2000Hz", amp="2", dc_oft="0.9", load="50")
#time.sleep(5)
#gen_ctl.gen_chn_sw(chn=2, SW="OFF") 
#gen_ctl.gen_chn_sw(chn=1, SW="OFF") 
#time.sleep(5)
#gen_ctl.gen_chn_sw(chn=2, SW="ON") 
#gen_ctl.gen_chn_sw(chn=1, SW="ON") 
#
