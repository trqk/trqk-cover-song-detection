#!/usr/bin/env python2
# csd-metrics.py: - basic processing of the results of stage 1 cover-song detection
# -*- coding: utf-8 -*-

"""
    csd-metrics.py: - basic processing of the results of stage 1 cover-song detection  
        Stephen Travis Pope - stephen@FASTLabInc.com - 1911
        
    //    Copyright (C) 2019 Stephen T. Pope & Trqk. All rights reserved.
    //    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.
    //    The copyright notice above does not evidence any actual or intended publication
    //    of such source code.
"""

import sys, os
import numpy as np
import matplotlib.pyplot as plt

names = []
data = []
matches = []
res = []

def load_data(list_file, data_file):
    "Load the data file (space-sep floats) and file names"
    liFi = open(list_file, 'r')
    global names
    names = liFi.readlines()
    liFi.close()
    for i in range(len(names)):             # grab the song name from the file name
        na = names[i]
        na = na.replace('.aiff\n', '')
        pos = na.rfind('-') + 1
        if pos > 1:
            names[i] = na[pos : ]
    daFi = open(data_file, 'r')
    daStr = daFi.readlines()
    daFi.close()
    for li in daStr:                        # convert the strings into a float array
        li = li.replace('\n', '')
        toks = li.split(' ')
        data.append(map(float, toks))
    print('Names:', len(names)),
    print('- Data:', len(data), len(data[0]))

def gather_stats():
    "Calculate the diagonal matches"
    ln = len(data)
    for i in range(0, ln, 2):
        v1 = data[i]                        # get 2 rows and the off-diagonal value average
        v2 = data[i + 1]
        m1 = v1[i + 1]
        m2 = v2[i]
        mch = (m1 + m2) / 2.0
        cnt1 = cnt2 = -2
        for j in range(ln):
            if v1[j] >= mch: cnt1 = cnt1 + 1
            if v2[j] >= mch: cnt2 = cnt2 + 1
#        print names[i], str(cnt1), str(cnt2)
        res.append(cnt1)
        res.append(cnt2)

def process():
    "Print a histogram of the results and the poor performers"
    hist, edges = np.histogram(res, 16)
    print (hist, '\n', edges)
    plt.hist(res, 16,
         histtype='bar',
         facecolor='b',
         alpha=0.5)
    plt.title('Cover-song Detection Accuracy on the CSD-80 Data Set (160 songs)')
    plt.savefig(str(os.getpid()) + '_csd_hist.png')
#    tMin = edges[1]
    tMax = edges[13]
    print ('Worst performers')
    for i in range(0, len(data), 2):
        if res[i] > tMax or res[i+1] > tMax:
            print('\t', names[i])

#### Main -------------------

if __name__ == '__main__':
    if (len(sys.argv)) != 3:                # args: list-file, data-file
        print('\nTo run: python csd-metrics.py list-file data-file\n')
        sys.exit(-1)
                                            # else load data, gather stats and print histogram and list of loser songs
    load_data(sys.argv[1], sys.argv[2])
    gather_stats()
    process()
