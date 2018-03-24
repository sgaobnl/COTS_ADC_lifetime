# -*- coding: utf-8 -*-
"""
File Name: S1_data_parser.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 6:39:06 PM
Last modified: 3/21/2018 1:13:26 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
import numpy as np
import os
import sys
from raw_convertor_m import raw_convertor
import time
import datetime 

def read_raw(rawpath, fn, spsfp, t= 20, adc_smps = 2000000):
    chn = int(fn[fn.find("CHN")+3], 16)
    fp = rawpath + fn
    fileinfo  = os.stat(fp)
    f_len = fileinfo.st_size
    smps_len = 26 * adc_smps * t + (int((adc_smps * t)/295)+1)*16
    if os.path.isfile(spsfp) :
        print "%s has been analyzed, delete it"%fp
        if os.path.isfile(fp) :
            os.remove(fp)
    else:
        print "Wait for several minutes"
        with open(fp, 'rb') as f:
            data = f.read(f_len-1024)
            chipdata = raw_convertor(data, (smps_len/2)) 
            np.save(spsfp[0:-4], chipdata[chn])


def read_chn_npy(spsfp, t= 20, adc_smps = 2000000, amp = 2.0, adcbits = 12, pfm_f ="pfm_results/"):
    ADCzero = 0
    ADChalf = 2**(adcbits-1) -1
    ADCfull = 2**adcbits -1
    chndata = np.load(spsfp)
    pos7ffs = np.where(chndata == ADChalf)[0]
    pos7fes = np.where(chndata == (ADChalf-1))[0]
    posfffs = np.where(chndata == ADCfull)[0]
    pos000s = np.where(chndata == ADCzero)[0]

    qtr_len1 = abs(posfffs[0]-pos7ffs[0])
    qtr_len2 = abs(pos000s[1]-pos7ffs[0])
    if (qtr_len1 < qtr_len2):
        qtr_len = qtr_len1
    else:
        qtr_len = qtr_len2

    pos7ff_mk = []
    pos7ff_mk.append(pos7ffs[0])
    for pos7ff in pos7ffs:
        if (pos7ff > (pos7ff_mk[-1] + qtr_len) ):
            pos7ff_mk.append(pos7ff)

    pos7fe_mk = []
    pos7fe_mk.append(pos7fes[0])
    for pos7fe in pos7fes:
        if (pos7fe > (pos7fe_mk[-1] + qtr_len) ):
            pos7fe_mk.append(pos7fe)

    if (len(pos7ff_mk) >=4):
        pos_m_mk = pos7ff_mk
    elif  (len(pos7fe_mk) >=4):
        pos_m_mk = pos7fe_mk
    else:
        print pos7fe_mk, pos7ff_mk
        print "Middle ADC (0x2047 and 0x2046) are missing"
        print "Please check, exit anyway"
        sys.exit()

    posfff_m0_m2 = []
    posfff_m1_m3 = []
    for posfff in posfffs:
        if ( (posfff > pos_m_mk[0]) and (posfff < pos_m_mk[2]) ):
            posfff_m0_m2.append(posfff)
        if ( (posfff > pos_m_mk[1]) and (posfff < pos_m_mk[3]) ):
            posfff_m1_m3.append(posfff)

    if ( posfff_m0_m2[0] == posfff_m1_m3[0] ):
        posfff_mk = [posfff_m0_m2[0], posfff_m0_m2[-1]]
        v_shape = 0  #inverted V shape
        m_fff = (posfff_mk[0] + posfff_mk[1])/2
    else:
        posfff_mk = [posfff_m0_m2[0], posfff_m0_m2[-1], posfff_m1_m3[0], posfff_m1_m3[-1]]
        v_shape = 1 # V shape
        m1_fff = (posfff_mk[0] + posfff_mk[1])/2
        m2_fff = (posfff_mk[2] + posfff_mk[3])/2
                
    pos000_m0_m2 = []
    pos000_m1_m3 = []
    for pos000 in pos000s:
        if ( (pos000 > pos_m_mk[0]) and (pos000 < pos_m_mk[2]) ):
            pos000_m0_m2.append(pos000)
        if ( (pos000 > pos_m_mk[1]) and (pos000 < pos_m_mk[3]) ):
            pos000_m1_m3.append(pos000)

    if ( pos000_m0_m2[0] == pos000_m1_m3[0] ):
        pos000_mk = [pos000_m0_m2[0], pos000_m0_m2[-1]]
        m_000 = (pos000_mk[0] + pos000_mk[1])/2
    else:
        pos000_mk = [pos000_m0_m2[0], pos000_m0_m2[-1], pos000_m1_m3[0], pos000_m1_m3[-1]]
        m1_000 = (pos000_mk[0] + pos000_mk[1])/2
        m2_000 = (pos000_mk[2] + pos000_mk[3])/2
    spsoft = pos000_mk[1] - pos000_mk[0]

    if (v_shape == 1):
        f_range = [m1_fff, m_000]
        r_range = [m_000, m2_fff]
    else:
        f_range = [m1_000, m_fff]
        r_range = [m_fff, m2_000]

    chndata_f = []

    for addr in range(f_range[0],f_range[1],1):
        if (chndata[addr] != 0 ) and (chndata[addr] != 0xFFF ) :
            chndata_f.append(chndata[addr])
    chndata_f = np.array(chndata_f) 
    Vrange_f = (len(chndata_f)*1.0 / (f_range[1] - f_range[0]) ) * amp
    Voffset = ( spsoft*0.5 / (f_range[1] - f_range[0]) ) * amp - 0.1
    print "Range 0x001 to 0xFFE = %fV (Falling Triangle) "%(Vrange_f)

    chndata_r = []
    for addr in range(r_range[0],r_range[1],1):
        if (chndata[addr] != 0 ) and (chndata[addr] != 0xFFF ) :
            chndata_r.append(chndata[addr])
    chndata_r = np.array(chndata_r) 
    Vrange_r = (len(chndata_r) *1.0/ (r_range[1] - r_range[0]) ) * amp
    print "Range 0x001 to 0xFFE = %fV (Rising Triangle) "%(Vrange_r)

    adc_range = [0x001, 0xFFE]
    adc_np = np.arange(adc_range[0], adc_range[1],1)

    Vinfo = [Voffset, Vrange_f, Vrange_r]
    vinfofp = spsfp[0:-4] + "_Vinfo" 
    np.save(vinfofp, Vinfo)

    chninfo_f = [chndata_f, adc_np, adcbits ]
    chninfo_r = [chndata_r, adc_np, adcbits ]
    adc_pfm(spsfp, chninfo_f, direct = "_f")
    adc_pfm(spsfp, chninfo_r, direct = "_r")

def adc_pfm(spsfp, chninfo, direct = "_f"):
    adc_histo_np = np.zeros(2**chninfo[2])
    for onevalue in chninfo[0]:  
        adc_histo_np[onevalue] = adc_histo_np[onevalue] + 1
    dnl, inl, dnl_abs = dnl_inl(adc_histo_np, chninfo[1])

    adcnpfn = spsfp[0:-4] + "_adcnp" + direct 
    histofn = spsfp[0:-4] + "_histo" + direct
    dnlfn = spsfp[0:-4] + "_dnl" + direct
    inlfn = spsfp[0:-4] + "_inl" + direct
    dnl_abs_fn = spsfp[0:-4] + "_dnl_abs" + direct

    np.save(adcnpfn, chninfo[1])
    np.save(histofn, adc_histo_np)
    np.save(dnlfn, dnl)
    np.save(inlfn, inl)
    np.save(dnl_abs_fn, dnl_abs)

def dnl_inl(adc_histo_np, adc_np):
    allsps = np.sum(adc_histo_np)
    spsperbit = allsps * 1.0 / ( adc_np[-1] - adc_np[0] + 1)
    norperbit = adc_histo_np / spsperbit 
    dnl = [ ]
    dnl_abs = [ ]
    inl = [ ]				
    for adccnt in adc_np:
        if adccnt == adc_np[0] :
            dnl.append(0)
            inl.append(0)
        else:
            dnl.append(norperbit[adccnt] -1 )
            dnl_abs.append(abs(norperbit[adccnt] -1) )
            inl.append( np.sum(dnl[0:adccnt+1]) )
    return dnl, inl, dnl_abs

def cur_to_npy(rawpath, pfm_f):
    cinfo = []
    cfns = ["SMU_CHN1_Rec.csv", "SMU_CHN2_Rec.csv", "SMU_CHN3_Rec.csv", ]
    for cfn in cfns:
        with open(rawpath+cfn, 'rb') as f:
            for line in f:
                #print line
                cparas = line.split(',')
                cmode = int(cparas[0])
                ctime = time.mktime(datetime.datetime.strptime(cparas[1], "%m%d%Y_%H%M%S").timetuple()) 
                cchn = int(cparas[2])
                cvolt =  cparas[3] 
                ccurr = cparas[4]
                cinfo.append([np.float64(cmode), ctime, np.float64(cchn), np.float64(cvolt), np.float64(ccurr)])
    np.save(rawpath+pfm_f+"MSU_MEAS", cinfo)


rawpath = "D:/COTS_ADC_LF/Rawdata/AD7274_012/"
pfm_f = "pfm_results/"

for root, dirs, files in os.walk(rawpath):
    break
fns = []
for f in files:
    pos1 = f.find("CHN")
    pos2 = f.find("MSPS")
    pos3 = f.find("SFT")
    pos4 = f.find("Phase")
    pos5 = f.find(".bin")
    if ( pos1 >= 0 ) and ( pos2 >= 0) and (pos3 >=0 ) and (pos4 >=0 ) and (pos5 >=0 ) :
        fns.append(f)
for fn in fns:
    print fn
    adc_smps = int(fn[fn.find("MSPS")-1])*1000000
    result_fp = rawpath + pfm_f
    if os.path.exists(result_fp):
        pass
    else:
        try: 
            os.makedirs(result_fp)
        except OSError:
            print "Cannot make the folder!"
            raise
    spsfn = fn[0:-4] + ".npy"
    spsfp = result_fp + spsfn
    histofp = spsfp[0:-4] + "_histo_r" +".npy"
    
    read_raw(rawpath, fn, spsfp, t= 20, adc_smps = adc_smps)
    if os.path.isfile(histofp) :
        print "%s has got!"%histofp
        pass
    else:
        read_chn_npy(spsfp, t= 20, adc_smps = adc_smps, amp=2.0, pfm_f = pfm_f)

cur_to_npy(rawpath, pfm_f)


#
