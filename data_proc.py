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
from statistics import mean 
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
                wrtr.writerow(newda[ix]);
            out.close



# Now create a song list and run the normalize method

cs = SongList()

cs.normalize('Results_20_02_10_21_00.csv')
