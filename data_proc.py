#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Song list class with table of songs for CSD test web app

#     @author: stephenp@trqk.io - 2001
# 	Copyright (C) 2020 Stephen T. Pope & Trqk, LLC. All rights reserved.
# 	THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.
# 	The copyright notice above does not evidence any actual or intended publication
# 	of such source code.

For testing: python data_proc.py 

"""

import numpy as np
from statistics import mean, stdev
import csv

# Song list class with table of songs

class SongList:
    "List of song objects; loads files into the DB"
#    folder = '/Users/stp/Code/CoSoDe/trqk-csd/scripts/Chrm_DTW/'        # location of data folder
    folder = './scripts/Chrm_DTW/'        # location of data folder

    def normalize(self, csv_file):
        "Normalize the data so the max off-axis value is 100"
                            # read the match table (TSV)
#        print(' -- read the match table')
        csv_f = self.folder + csv_file
        tsvFi = open(csv_f, 'r')
        data = tsvFi.readlines()
        tsvFi.close()
        ln = len(data)
        print(' --', csv_file, '--', ln, 'rows')
        # print(data[0])
        # print(type(data[0]))
        newda = []
        for ix in range(ln):
            lst = list(map(float, data[ix].split('\t')))
            ind = np.argmax(lst)
            lst[ind] = 0
            av = mean(lst)
            mx = max(lst)
            print(ix, 'AV:', f'{av:.3f}', '  MX:', f'{mx:.3f}')
            sca = 100.0 / mx        # scale line by 100 / max
            newli = []
            for i2 in range(len(lst)):
                newli.append(lst[i2] * sca)
            newda.append(newli)
        csv_f = self.folder + csv_file+ '2'
        with open(csv_f, 'w', newline='') as out:
            wrtr = csv.writer(out, delimiter='\t');
            for ix in range(ln - 1):
                wrtr.writerow(['{:.4}'.format(x) for x in newda[ix]])
            out.close

    def stats(self, csv_file):
        "Gather the stats of the match-results table"
                            # read the match table (TSV)
#        print(' -- read the match table')
        csv_f = self.folder + csv_file
        tsvFi = open(csv_f, 'r')
        data = tsvFi.readlines()
        tsvFi.close()
        ln = len(data)
        print(' --', csv_file, '--', ln, 'rows')
        newda = []
        for ix in range(ln):
            lst = list(map(float, data[ix].split('\t')))
            ind = np.argmax(lst)
            lst[ind] = 0
#            av = mean(lst)
            mx = max(lst)
            sca = 1.0 # 100.0 / mx        # scale line by 100 / max
            newli = []
            for i2 in range(len(lst)):
                newli.append(lst[i2] * sca)
            newda.append(newli)
        res = []
        for ix in range(ln):
            arr = newda[ix]
            if ix % 2 == 0:
                i2 = ix + 1
            else:
                i2 = ix - 1
            va = arr[i2]
            arr[i2] = 0
            mn = va / mean(arr)
#            print(ix, i2, f'{va:.3f}', f'{mn:.3f}')
#            print(ix, f'{mn:.3f}')
            res.append(mn)
        print('Min, avg, max, std-dev:  ', f'{min(res):.3f}', f'{mean(res):.3f}', f'{max(res):.3f}', f'{stdev(res):.3f}')


# Now create a song list and run the normalize method

cs = SongList()

#cs.normalize('Results_20_02_10_21_00.csv')

#Song match results: min/avg/max weight of "right" answer to the rest

# Full song
cs.stats('Results_20_02_10_21_00.csv')         # 0.000 4.430 49.585

#Middle minute
cs.stats('Results_20_02_19_23_39.csv')         # 0.000 1.023 3.190

