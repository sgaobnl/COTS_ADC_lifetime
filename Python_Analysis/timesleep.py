# -*- coding: utf-8 -*-
"""
File Name: timesleep.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 12/22/2017 11:10:55 AM
Last modified: 12/25/2017 9:05:43 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl


import sys 
import time
from datetime import datetime

timestampe =  datetime.now().strftime('%m/%d/%Y %H:%M:%S')
print "Sleep begin at %s"%timestampe
sleepsecond = int(sys.argv[1])
sleephours = sleepsecond/3600.0
print "Sleep will last %f hours"%sleephours
time.sleep(sleepsecond)
print "Wake up at  %s"%timestampe
