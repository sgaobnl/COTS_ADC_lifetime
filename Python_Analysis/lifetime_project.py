# -*- coding: utf-8 -*-
"""
File Name: read_mean.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/9/2016 7:12:33 PM
Last modified: Fri Jul 13 11:55:38 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import openpyxl as px
import numpy as np
import math
import statsmodels.api as sm
import matplotlib.pyplot as plt

def lifetime():

    x = [6, 6, 5.75, 5.5, 5.5, 5.25] 
    x = 1/np.array(x)
    y = [105, 120, 130, 400, 405, 700] 
    logy = []
    for i in y:
        logy.append(math.log10(i))
    y = np.array(logy)
    cresults = sm.OLS(y,sm.add_constant(x)).fit()
    cslope = cresults.params[1]
    cconstant = cresults.params[0]
    print cslope, cconstant

    plt.figure(figsize=(8,6))
    plt.scatter(x[0:-1], y[0:-1],c='g',marker='o')
    #plt.scatter([x[-1]], [y[-1]],c='r',marker='*')
    plt.scatter([x[-1]], [y[-1]],c='g',marker='o')
    cx_plot = np.linspace(0,1/2.0, num=10)

    plt.plot(cx_plot, cx_plot*cslope + cconstant, color = 'b')

#    k = len(cx_plot)
#    m = max(delta_cacu_np)
    #plt.text(0.0,1.0*m,"Y = (%f) * X + (%f)"%(cslope,cconstant) )
#    plt.text(1/5.25+0.01, 2.5,"5.25V, estimate to 800 hours", fontsize=14 )
#    plt.text(1/5.25+0.01, 2.5,"5.25V, estimate to 800 hours", fontsize=14 )
    plt.scatter([1/3.6],[(cslope*(1/3.6)+cconstant)], c='m', marker = 's')
    plt.text(0.3,6,"3.6V, %.1E years"%(10**(cslope*(1/3.6)+cconstant)/365/24), fontsize=14  )
    plt.scatter([1/2.5],[(cslope*(1/2.5)+cconstant)], c='m', marker = 's')
    plt.text(0.27,10.7,"2.5V, %.1E years"%(10**(cslope*(1/2.5)+cconstant)/365/24), fontsize=14  )
#    plt.title("Linear fit by Caculation" )
    plt.ylabel("$\log$$_1$$_0$(lifetime) / hour", fontsize=16 )
    plt.xlabel("1/V$_d$$_s$  / V" , fontsize=16 )
    plt.title("AD7274@LN2 Lifetime Projection" , fontsize=20 )
    plt.xlim([0.1,0.5])
    plt.ylim([0,15])
    plt.tick_params(labelsize=12)
    plt.tight_layout( rect=[0, 0.05, 1, 0.95])
    plt.savefig("./lifetime.png")
    #plt.show()
    plt.close()

lifetime()

