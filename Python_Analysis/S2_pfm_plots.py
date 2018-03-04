# -*- coding: utf-8 -*-
"""
File Name: S2_pfm_plots.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 6:39:06 PM
Last modified: Sun Mar  4 09:50:14 2018
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

from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from random import randint
import time
#from datetime import datetime
import datetime

def lf_pfm_fs (result_f, chn, msps, pfm_pers, ps_flg = "LDO", sft=1, phase=3):
    for root, dirs, files in os.walk(result_f):
        break
    fns = []
    for f in files:
        pos1 = f.find("CHN"+format(chn,"1x"))
        pos2 = f.find(format(msps,"1d")+"MSPS")
        pos3 = f.find("SFT"+format(sft,"1d"))
        pos4 = f.find("Phase"+format(phase,"1d"))
        pos5 = f.find(pfm_pers)
        pos6 = f.find(ps_flg)
        if ( pos1 >= 0 ) and ( pos2 >= 0) and (pos3 >=0 ) and (pos4 >=0 ) and (pos5 >=0 ) and (pos6 >=0 )  :
            fns.append(f)

    acq_tts = []
    for fn in fns:
        pos_Phase = fn.find("Phase")
        acq_time = fn[pos_Phase+7: pos_Phase+7+15]
        acq_tstamp = time.mktime(datetime.datetime.strptime(acq_time, "%m%d%Y_%H%M%S").timetuple())
        acq_tts.append(acq_tstamp)
    acq_tts = sorted(acq_tts,reverse=True)

    fns_tmp = []
    for tt in acq_tts:
        strtime =datetime.datetime.fromtimestamp(tt).strftime('%m%d%Y_%H%M%S') 
        for fn in fns:
            pos_Phase = fn.find("Phase")
            acq_time = fn[pos_Phase+7: pos_Phase+7+15]
            acq_tstamp = time.mktime(datetime.datetime.strptime(acq_time, "%m%d%Y_%H%M%S").timetuple())
            if (acq_tstamp == tt):
                fns_tmp.append(fn)
                break
    fns = fns_tmp
    return fns

def adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = "LDO", dis_range=(-1,1), sft=1, phase=3, dut_no = "AD7274_001"):
    fns = lf_pfm_fs (result_f, chn, msps, pfm_pers, ps_flg, sft, phase)
    #fns = sorted(fns,reverse=False)

    t_np = []
    voft_np = []
    vrange_r_np = []
    vrange_f_np = []

    for fn_i in range(len(fns)-1, -1, -1):
        pos_Phase = fns[fn_i].find("Phase")
        acq_time = fns[fn_i][pos_Phase+7: pos_Phase+7+15]
        acq_tstamp = time.mktime(datetime.datetime.strptime(acq_time, "%m%d%Y_%H%M%S").timetuple())
        vpfm = np.load(result_f + fns[fn_i])

        t_np.append(acq_tstamp)
        voft_np.append(vpfm[0])
        vrange_f_np.append(vpfm[1])
        vrange_r_np.append(vpfm[2])
    h_np = (np.array(t_np) - t_np[0])/3600.0
    voft_np = np.array(voft_np)*1000
    vrange_f_np = np.array(vrange_f_np)*1000
    vrange_r_np = np.array(vrange_r_np)*1000

    plt.figure(figsize=(16,9))
    plt.grid()
    plt.plot(h_np, voft_np, color='m', marker='o', label="ADC DC offset Error @%dMSPS"%msps)
    plt.legend(loc='best')
    strtime =datetime.datetime.fromtimestamp(t_np[0]).strftime('%Y-%m-%d %H:%M:%S') 
    plt.text( 0, np.max(voft_np), "$\leftarrow$%s"%(strtime)) 
    plt.ylim([-5,5])
    plt.ylabel("DC offset / mV ")
    plt.xlabel("Time of duration in LN2 under test / h ")
    plt.title ("%s: ADC DC offset vs. Time of duration in LN2"%dut_no)
    plt.savefig(plot_f + ps_flg + "_" + "DC_offset_%dMSPS"%(msps) + ".png")
    plt.close()

    plt.figure(figsize=(16,9))
    plt.grid()
    plt.plot(h_np, vrange_f_np, color='g', marker='*', label="Scale from 0xFFE to 0x001@%dMSPS"%msps)
    plt.legend(loc='best')
    strtime =datetime.datetime.fromtimestamp(t_np[0]).strftime('%Y-%m-%d %H:%M:%S') 
    plt.text( 0, np.max(vrange_f_np), "$\leftarrow$%s"%(strtime)) 
    plt.ylim([np.mean(vrange_f_np)-10,np.mean(vrange_f_np)+10])
    plt.ylabel("Input voltage range / mV ")
    plt.xlabel("Time of duration in LN2 under test / h ")
    plt.title ("%s: ADC scale vs. Time of duration in LN2"%dut_no)
    plt.savefig(plot_f + ps_flg + "_" + "ADC_scale_FFE_001_%dMSPS"%(msps) + ".png")
    plt.close()

    plt.figure(figsize=(16,9))
    plt.grid()
    plt.plot(h_np, vrange_f_np, color='r', marker='+', label="Scale from 0x001 to 0xFFE@%dMSPS"%msps)
    plt.legend(loc='best')
    strtime =datetime.datetime.fromtimestamp(t_np[0]).strftime('%Y-%m-%d %H:%M:%S') 
    plt.text( 0, np.max(vrange_r_np), "$\leftarrow$%s"%(strtime)) 
    plt.ylim([np.mean(vrange_r_np)-10,np.mean(vrange_r_np)+10])
    plt.ylabel("Input voltage range / mV ")
    plt.xlabel("Time of duration in LN2 under test / h ")
    plt.title ("%s: ADC scale vs. Time of duration in LN2"%dut_no)
    plt.savefig(plot_f + ps_flg + "_" + "ADC_scale_001_FFE_%dMSPS"%(msps) + ".png")
    plt.close()

def adc_error_plots (result_f, plot_f, chn, msps, pfm_pers = "_inl_r.npy", ps_flg="LDO", dis_range=(-1,1), sft=1, phase=3, label = "INL", dut_no = "AD7274_001"):
    fns = lf_pfm_fs (result_f, chn, msps, pfm_pers, ps_flg, sft, phase)

    plt.figure(figsize=(16,9))
    clor_np = ['b', 'c', 'm', 'y', 'k'] 
    t_mean_stds = []
    for fn_i in range(len(fns)):
        adc_np = np.load(result_f + fns[fn_i][0:-10]+"_adcnp_r.npy")
        pos_Phase = fns[fn_i].find("Phase")
        acq_time = fns[fn_i][pos_Phase+7: pos_Phase+7+15]
        acq_tstamp = time.mktime(datetime.datetime.strptime(acq_time, "%m%d%Y_%H%M%S").timetuple())
        pfm = np.load(result_f + fns[fn_i])
        pfm_mean = np.mean(pfm)
        pfm_std  = np.std(pfm)
        t_mean_stds.append([acq_tstamp, pfm_mean, pfm_std])
        if fn_i == 0 :
            clor = 'r'
            plt.text(2148, 0.90, "End time: %s"%acq_time,color= clor )
            plt.text(2148, 0.80, "%s"%fns[fn_i],color= clor )
            plt.text(2148, 0.70, "Mean={}, Std={}".format(pfm_mean, pfm_std ),color=clor)
            plt.plot(adc_np, pfm, color=clor)
        elif fn_i == 1 :
            clor = 'r'
        elif fn_i == len(fns)-1:
            clor = 'g'
            plt.text(100, 0.90, "Begin time: %s"%acq_time,color= clor )
            plt.text(100, 0.80, "%s"%fns[fn_i],color= clor )
            plt.text(100, 0.70, "Mean={}, Std={}".format(pfm_mean, pfm_std ),color=clor)
            plt.plot(adc_np, pfm, color=clor)
        else:
            clor = clor_np[randint(0, len(clor_np)-1)]
        plt.scatter(adc_np, pfm, color=clor)
    plt.xlim([0,4095])
    plt.ylim(dis_range)
    plt.xlabel("Codes")
    plt.ylabel("%s ERROR / LSB"%label)
    plt.title("%s: "%dut_no +label)
    plt.grid()
    plt.savefig(plot_f + ps_flg + "_" + "%s_%dMSPS_performance"%(label,msps) + ".png")
    plt.close()
    np.save(result_f + fns[0][0:(fns[0].find("Phase")+7)] + pfm_pers[0:-4] +  "%s_t_mean_std"%label, t_mean_stds)

    avg_times = []
    avg_mpfms = []
    avg_spfms = []
    t_mean_stds = sorted(t_mean_stds, reverse=False)
    for avg in t_mean_stds:
        avg_times.append(avg[0])
        avg_mpfms.append(avg[1])
        avg_spfms.append(avg[2])

    avg_hours = (np.array(avg_times) - avg_times[0] )/ 3600.0
    pct_pfmmean = np.array(avg_mpfms)*100.0 / avg_mpfms[0] 
    pct_pfmstd = np.array(avg_spfms)*100.0 / avg_spfms[0] 
    pct_msps = msps
    pct_pfmchn = chn
    pct_label = label
    return pct_pfmchn, pct_msps, avg_hours, pct_pfmmean, pct_pfmstd, pct_label, avg_mpfms, avg_spfms, avg_times

def adcdnl_histo_plots (result_f, plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = "LDO", dis_range=(-1,1), sft=1, phase=3, label = "DNL", dut_no = "AD7274_001"):
    fns = lf_pfm_fs (result_f, chn, msps, pfm_pers, ps_flg, sft, phase)
    plt.figure(figsize=(16,9))
    clor_np = ['b', 'c', 'm', 'y', 'k'] 

    for fn_i in range(len(fns)):
        dnl = np.load(result_f + fns[fn_i])
        pos_Phase = fns[fn_i].find("Phase")
        acq_time = fns[fn_i][pos_Phase+7: pos_Phase+7+15]
        dnl_mean = np.mean(dnl)
        dnl_std  = np.std(dnl)
        if fn_i == 0 :
            clor = 'r'
            plt.text(0.1, 950, "End Time: %s"%acq_time,color= clor )
            plt.text(0.1, 900, "%s"%fns[fn_i],color= clor )
            plt.text(0.1, 850, "Mean={}, Std={}".format(dnl_mean, dnl_std ),color=clor)
        elif fn_i == 1 :
            clor = 'r'
        elif fn_i == len(fns)-1:
            clor = 'g'
            plt.text(-0.9, 950, "Begin Time: %s"%acq_time,color= clor )
            plt.text(-0.9, 900, "%s"%fns[fn_i],color= clor )
            plt.text(-0.9, 850, "Mean={}, Std={}".format(dnl_mean, dnl_std ),color=clor)
        else:
            clor = clor_np[randint(0, len(clor_np)-1)]
        plt.hist(dnl, bins=100, range=dis_range, color=clor, histtype='barstacked', label=label )
    plt.xlim([-1,1])
    plt.ylim([0,1000])
    plt.xlabel("%s \ LSB"%label[0:3])
    plt.ylabel("Number of Codes (%d codes in total)"%(0xFFE))
    plt.title("%s: "%dut_no +label)
    plt.grid()
    plt.savefig(plot_f + ps_flg + "_" + "%s_%dMSPS_distribution_histogram"%(label,msps) + ".png")
    plt.close()



def sigma_dnl_plot (result_f, plot_f, dnl_pcts, dut_no = "AD7274_001", ps_flg = "LDO"):
    plt.figure(figsize=(12,8)) 
    ax1 = plt.subplot2grid((1, 1), (0, 0))
    dnl_0h = "Sigma(DNL) @ 0h = %f "%dnl_pcts[7][0]
    ax1.plot(dnl_pcts[2],  dnl_pcts[4], color = 'r', marker = 'o' , label= "sigma of %s when %d MSPS \n %s"%(dnl_pcts[5], dnl_pcts[1], dnl_0h) ) 
    ax1.legend(loc='best')
    ax1.grid()
    strtime =datetime.datetime.fromtimestamp(dnl_pcts[8][0]).strftime('%Y-%m-%d %H:%M:%S') 
    ax1.text( dnl_pcts[2][0], np.max(dnl_pcts[7])*0.95, "$\leftarrow$%s"%(strtime)) 
    ax1.set_ylabel("%s Variation compared to beginning / %% "%(dnl_pcts[5]))
    ax1.set_xlabel("Time of duration in LN2 under test / h ")
    ax1.set_ylim([dnl_pcts[7][0]*0.5*100/dnl_pcts[7][0], dnl_pcts[7][0]*2.5*100/dnl_pcts[7][0]])

    ax2 = ax1.twinx()
    ax2.set_ylabel("%s Variation / LSB "%(dnl_pcts[5]))
    ax2.set_ylim([dnl_pcts[7][0]*0.5, dnl_pcts[7][0]*2.5])

    plt.title ("%s: Sigma of %s vs. Time of duration in LN2"%(dut_no, dnl_pcts[5]))
    plt.savefig(plot_f + ps_flg + "_" + "%s_%dMSPS_vs_time_of_duration_LSB"%(dnl_pcts[5], dnl_pcts[1]) + ".png")
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.close()


def read_msu(result_f):
    curr = np.load(result_f +  "MSU_MEAS.npy")
    ivrefnor = []
    ivccnor  = []
    ivrefstr = []
    ivccstr  = []
    for icurr in curr:
        if icurr[0] == 1 and icurr[2] == 2 :
            ivrefnor.append(icurr)
        elif icurr[0] == 1 and icurr[2] == 3 :
            ivccnor.append(icurr)
        elif icurr[0] == 2 and icurr[2] == 2 :
            ivrefstr.append(icurr)
        elif icurr[0] == 2 and icurr[2] == 3 :
            ivccstr.append(icurr)
    return ivrefnor, ivccnor, ivrefstr, ivccstr 

def msu_avginfo(cinfo):
    csplit = [0]
    t0 = cinfo[0][1]
    for i in range(0, len(cinfo)-1, 1):
        if (cinfo[i+1][1] - cinfo[i][1] > 60):
            csplit.append(i)
            t0 = cinfo[i+1][1]
        elif (cinfo[i+1][1] - t0 > 3660):
            csplit.append(i)
            t0 = cinfo[i+1][1]

    csplit.append( (len(cinfo)-2) )

    avg_info = []

    for i in range(0, len(csplit)-1,1):
        slicevolt = []
        slicecurr = []
        slice_start = csplit[i]
        slice_end = csplit[i+1]
        for onec in cinfo[slice_start: slice_end]:
            slicevolt.append(onec[3] )
            slicecurr.append(onec[4] )
        clast =  cinfo[slice_end-1][1]-cinfo[slice_start+1][1] + 3 #compensate 3 second
        avgvolt = np.mean(slicevolt)
        stdvolt = np.std(slicevolt)
        avgcurr = np.mean(slicecurr)
        stdcurr = np.std(slicecurr)
        avg_info.append([clast, cinfo[slice_end-1][0], cinfo[slice_end-1][1], cinfo[slice_end-1][2], avgvolt, stdvolt, avgcurr, stdcurr])
    return avg_info

def msuavg_to_pct(cinfo):
    avg_info=msu_avginfo(cinfo)
    avg_times = []
    slice_hours = []
    avg_mvolts = []
    avg_svolts = []
    avg_mcurrs = []
    avg_scurrs = []
    for avg in avg_info:
        avgmode = avg[1]
        avgchn  = avg[3]
        avg_times.append(avg[2])
        slice_hours.append(avg[0]/3600.0)
        avg_mvolts.append(avg[4])
        avg_svolts.append(avg[5])
        avg_mcurrs.append(avg[6])
        avg_scurrs.append(avg[7])
    avg_hours  = ( (np.array(avg_times) - avg_times[0] +3 )/ 3600.0 ) + (avg[0]/3600.0)#compensate 3 seconds
    sum_hours  = np.sum(slice_hours)
    pct_vmean  = np.array(avg_mvolts)*100.0 / avg_mvolts[0] 
    pct_vstd   = np.array(avg_svolts)*100.0 / avg_mvolts 
    pct_imean  = np.array(avg_mcurrs)*100.0 / avg_mcurrs[0] 
    pct_istd   = np.array(avg_scurrs)*100.0 / avg_mcurrs 
    pct_mode   = avgmode
    pct_msuchn = avgchn
    return [pct_mode, pct_msuchn, avg_hours, sum_hours, pct_vmean, pct_vstd, pct_imean, pct_istd, avg_times,avg_mvolts, avg_svolts, avg_mcurrs, avg_scurrs, slice_hours]

def cur_plot (result_f, plot_f, cur_pcts, fn="Current_of_Stress_Vcc", dut_no = "AD7274_001", ylim=[98,102]):
    plt.figure(figsize=(12,8)) 
    ax1 = plt.subplot2grid((1, 1), (0, 0))
    str_imark = "V(0) = %.3fV, I(0) = %.3fmA"% (cur_pcts[9][0], cur_pcts[11][0]*1000)
    if (cur_pcts[0] == 1 ):
        str_curmode = "Vcc=2.5V, Vref=1.8V\n %s "%( str_imark ) 
    elif (cur_pcts[0] == 2 ):
        str_hmark = "%.1f Hours under Stress"% (cur_pcts[3])
        str_curmode = "Stress Voltage \n %s \n %s"%( str_imark, str_hmark )

    ax1.errorbar(cur_pcts[2], cur_pcts[6],  cur_pcts[7], color = 'r', marker = 'o', label= "%s"%(str_curmode)) 
    ax1.legend(loc='best')
    ax1.grid()
    strtime =datetime.datetime.fromtimestamp(cur_pcts[8][0]).strftime('%Y-%m-%d %H:%M:%S') 
    ax1.text( cur_pcts[2][0], 90, "$\leftarrow$%s"%(strtime)) 
    ax1.set_ylim(ylim)
    ax1.set_ylabel("Current Variation compared to beginning / % ")
    ax1.set_xlabel("Time of duration in LN2 under test / h ")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Current / mA ")
    ax2.set_ylim([ylim[0]*cur_pcts[11][0]*10, ylim[1]*cur_pcts[11][0]*10])

    plt.title ("%s: Current vs. Time of duration in LN2"%dut_no)
    plt.savefig(plot_f + fn + ".png")
    plt.close()

def volt_plot (result_f, plot_f, volt_pcts, fn="Volt_of_Stress_Vcc", dut_no = "AD7274_001"):
    plt.figure(figsize=(16,9)) 
    str_imark = "V(0) = %.3fV, I(0) = %.3fmA"% (volt_pcts[9][0], volt_pcts[11][0]*1000)
    if (volt_pcts[0] == 1 ):
        str_curmode = "Vcc=2.5V, Vref=1.8V\n %s "%( str_imark ) 
    elif (volt_pcts[0] == 2 ):
        str_hmark = "%.1f Hours under Stress"% (volt_pcts[3])
        str_curmode = "Stress Voltage \n %s \n %s"%( str_imark, str_hmark )

    plt.errorbar(volt_pcts[2], volt_pcts[4],  volt_pcts[5], color = 'r', marker = 'o', label= "%s"%(str_curmode)) 
    plt.legend(loc='best')
    plt.grid()
    strtime =datetime.datetime.fromtimestamp(volt_pcts[8][0]).strftime('%Y-%m-%d %H:%M:%S') 
    plt.text( volt_pcts[2][0], 90, "$\leftarrow$%s"%(strtime)) 
    plt.ylim([99.9,100.1])
    plt.ylabel("Voltage Variation compared to beginning / % ")
    plt.xlabel("Time of duration in LN2 under test / h ")
    plt.title ("%s: Current vs. Time of duration in LN2"%dut_no)
    plt.savefig(plot_f + fn + ".png")
    plt.close()

def strcur_plot (result_f, plot_f, cur_pcts, fn="Stress_Vcc", dut_no = "AD7274_001"):
    str_imark = "V(0) = %.3fV, I(0) = %.3fmA"% (cur_pcts[9][0], cur_pcts[11][0]*1000)
    if (cur_pcts[0] == 4 ):
        cur_sum_hs = [] 
        for ih in range(len(cur_pcts[13])):
            cur_sum_hs.append(np.sum(cur_pcts[13][0:ih+1]))

        str_hmark = "%.1f Hours under Stress"% (cur_pcts[3])
        str_curmode = "Stress Voltage \n %s \n %s"%( str_imark, str_hmark )
        plt.figure(figsize=(16,9)) 
        plt.errorbar(cur_sum_hs, cur_pcts[6],  cur_pcts[7], color = 'r', marker = 'o', label= "%s"%(str_curmode)) 
        plt.legend(loc='best')
        plt.grid()
        strtime =datetime.datetime.fromtimestamp(cur_pcts[8][0]).strftime('%Y-%m-%d %H:%M:%S') 
        plt.text( cur_sum_hs[0], 90, "$\leftarrow$%s"%(strtime)) 
        plt.ylim([98,102])
        plt.ylabel("Current Variation compared to beginning / % ")
        plt.xlabel("Time of duration in LN2 under test / h ")
        plt.title ("%s: Current vs. Time of duration in LN2"%dut_no)
        plt.savefig(plot_f + fn + ".png")
        plt.close()

dut_no = "AD7274_009"
rawpath = "D:/COTS_ADC_LF/Rawdata/" + dut_no + "/"
pfm_f = "pfm_results/"
result_f = rawpath + pfm_f
plot_f = rawpath + "plot_results/"
chn = 0
sft = 1
phase = 3

if os.path.exists(plot_f):
    pass
else:
    try: 
        os.makedirs(plot_f)
    except OSError:
        print "Cannot make the folder!"
        raise

ps_flg="LDO"
msps = 2
adcdnl_histo_plots (result_f, plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
dnl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, label = "DNL", dut_no = dut_no)
inl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_inl_r.npy", ps_flg = ps_flg, dis_range=(-2,1), sft=1, phase=3, label = "INL", dut_no = dut_no)
adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
sigma_dnl_plot (result_f, plot_f, dnl_pcts, dut_no = dut_no, ps_flg = ps_flg)
msps = 1
adcdnl_histo_plots (result_f, plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
dnl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, label = "DNL", dut_no = dut_no)
inl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_inl_r.npy", ps_flg = ps_flg, dis_range=(-2,1), sft=1, phase=3, label = "INL", dut_no = dut_no)
adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
sigma_dnl_plot (result_f, plot_f, dnl_pcts, dut_no = dut_no, ps_flg = ps_flg)

ps_flg="SMU"
msps = 2
adcdnl_histo_plots (result_f, plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
dnl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, label = "DNL", dut_no = dut_no)
#inl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_inl_r.npy", ps_flg = ps_flg, dis_range=(-2,1), sft=1, phase=3, label = "INL", dut_no = dut_no)
#adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
#adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
sigma_dnl_plot (result_f, plot_f, dnl_pcts, dut_no = dut_no, ps_flg = ps_flg)
msps = 1
adcdnl_histo_plots (result_f, plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
dnl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_dnl_r.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, label = "DNL", dut_no = dut_no)
#inl_pcts = adc_error_plots (result_f,plot_f, chn, msps, pfm_pers = "_inl_r.npy", ps_flg = ps_flg, dis_range=(-2,1), sft=1, phase=3, label = "INL", dut_no = dut_no)
#adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
#adc_v_plots (result_f, plot_f, chn, msps, pfm_pers = "_Vinfo.npy", ps_flg = ps_flg, dis_range=(-1,1), sft=1, phase=3, dut_no = dut_no)
sigma_dnl_plot (result_f, plot_f, dnl_pcts, dut_no = dut_no, ps_flg = ps_flg)
#

#
ivrefnor, ivccnor, ivrefstr, ivccstr=read_msu(result_f)
irefnor_pct  = msuavg_to_pct(cinfo=ivrefnor)
iccnor_pct   = msuavg_to_pct(cinfo=ivccnor)
ivrefstr_pct = msuavg_to_pct(cinfo=ivrefstr)
ivccstr_pct  = msuavg_to_pct(cinfo=ivccstr)

cur_plot (result_f, plot_f, cur_pcts=irefnor_pct , fn="Current_of_Normal_Vref", dut_no = dut_no, ylim=[20,120])
cur_plot (result_f, plot_f, cur_pcts=iccnor_pct  , fn="Current_of_Normal_Vcc", dut_no = dut_no , ylim=[20,120])
cur_plot (result_f, plot_f, cur_pcts=ivrefstr_pct, fn="Current_of_Stress_Vref", dut_no = dut_no, ylim=[20,120])
cur_plot (result_f, plot_f, cur_pcts=ivccstr_pct , fn="Current_of_Stress_VCC", dut_no = dut_no , ylim=[20,120])

#volt_plot (result_f, plot_f, volt_pcts=ivccstr_pct , fn="Volt_of_Stress_VCC", dut_no = dut_no)
#strcur_plot (result_f, plot_f, cur_pcts=ivccstr_pct, dut_no = dut_no)
