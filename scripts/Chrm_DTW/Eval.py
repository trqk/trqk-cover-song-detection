#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Cover-song detection data analysis tools
        Stephen Travis Pope - stephenp@trqk.io - 2001
        
    //    Copyright (C) 2020 Stephen T. Pope & Trqk. All rights reserved.
    //    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.
    //    The copyright notice above does not evidence any actual or intended publication
    //    of such source code.

This program loads a csv file generated by the MATLAB Chromagram_DTW app and massages it 
to deliver better stats and plot accuracy histograms.  
"""

# Imports

import os
import numpy as np
import csv
import matplotlib.pyplot as plt

#----------------------------------------------------------------------------------------
#
# Tester class does it all
#

class Tester(object):
    "Test data clean-up for Chromagram_DTW app"

    def __init__(self, csv_file, clr):
        "Load the csv file and run the minimal data massaging; plot result histograms"
        folder = '/Content/Code/SndsLike/CoSoDe/ChrmDTW_CSD/'
        csv_f = folder + csv_file
        self.data = []
        with open(csv_f, 'rt') as csvfile:
            csvreader = csv.reader(csvfile, delimiter = '	')
            for row in csvreader:
                self.data.append(list(map(float, row)))
        ln = len(self.data[0])
        print('\n--', csv_file, '--', ln, 'rows')
        # print(self.data[0])
        for i in range(ln):
            self.data[i][i] = 0         # zero out diagonal
        self.avgs = np.empty(ln, np.float32)                  # avgs of rows
        self.mats = np.empty(ln, np.float32)                  # avgs of matches
        self.rats = np.empty(ln, np.float32)                  # ratios of matches
        for i in range(ln - 1):         # compute avg of row and avg of matches
            self.avgs[i] = np.average(self.data[i])
            self.mats[i] = (self.data[i][i+1] + self.data[i+1][i-1]) / 2
            self.rats[i] = self.mats[i] / self.avgs[i]
            
                                        # print raw results
        np.set_printoptions(precision = 4, suppress = True)
        # print('\nAVGS', self.avgs)
        # print('\nMATS', self.mats)
        # print('\nRATS', self.rats)
        
        avgr = np.average(self.rats)    # calc avg and std-dev of ratios
        stdd = np.std(self.rats)
        # ra2 = np.subtract(self.rats, avgr)  # scale rats to std-devs
        # ra2 = np.divide(ra2, stdd)
        # ra2 = np.absolute(ra2)
        ra2 = self.rats
        print('\nAvg', avgr, 'Stdd', stdd)
        print('\n', ra2)
        plt.style.use('ggplot')
        plt.hist(ra2, alpha = 0.6, bins = 60, color = clr)

    def play_matches(self, ind):
        print('\nInd:', ind)


#------- MAIN function --------------------------

if __name__ == '__main__':
    os.system('clear')
    # te = Tester('Results_20_01_22_16_41.csv', 'r')
    # te = Tester('Results_20_01_29_17_47.csv', 'g')
    # te = Tester('Results_20_01_29_22_43.csv', 'b')
    # te = Tester('Results_20_01_31_06_36b.csv', 'y')
    te = Tester('Results_20_01_31_14_12.csv', 'r')
    
    # if (len(sys.argv)) < 2:                    # if called with no arg, run std test
    #     print 'Unknown command selector; choose [pdksmocneg1]'
    # else:                                       # else switch on arg
    #     ch = sys.argv[1][0]
    #     if   ch == 'p':     te.do_rank()        # 
    #     elif ch == 'd':     te.do_spread        # 

    #     else: print 'Unknown command selector; choose [pdksmocneg1]'
        
# END