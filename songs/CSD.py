#!/usr/bin/env python3# -*- coding: utf-8 -*-"""Song list class with table of songs for CSD test web app        @author: stephenp@trqk.io - 2001    //	Copyright (C) 2020 Stephen T. Pope & Trqk, LLC. All rights reserved.    //	THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.    //	The copyright notice above does not evidence any actual or intended publication    //	of such source code.For testing: http://127.0.0.1:8000/songs/"""from .models import SongFilefrom django.db import connection# Song list class with table of songsclass SongList:    "List of song objects; loads files into the DB"#    folder = '/Users/stp/Code/CoSoDe/trqk-csd/scripts/Chrm_DTW/'        # location of data folder    folder = './scripts/Chrm_DTW/'        # location of data folder    def __init__(self, list_file, csv_file):        "CSD.SongList('list_stp.txt', 'Results_20_02_10_21_00.csv')"        if len(list_file) > 0:            self.read_data(list_file, csv_file)            def read_data(self, list_file, csv_file):        if SongFile.objects.count() == 162:            return                    # flush the DB table        print(' -- flush the DB table')        with connection.cursor() as cursor:            cursor.execute("DELETE from songs_songfile")                            # read the file list        print(' -- read the file list')        lis_f = self.folder + list_file        liFi = open(lis_f, 'r')        self.files = liFi.readlines()        liFi.close()                            # read the match table (TSV)        print(' -- read the match table')        csv_f = self.folder + csv_file        tsvFi = open(csv_f, 'r')        self.data = tsvFi.readlines()        tsvFi.close()        ln = len(self.data)        print(' --', csv_file, '--', ln, 'rows')                            # create the SongFile object list        print(' -- create the SongFile object list')        sfo = 'MP3/'        sf = 0        cnt = 0        for so in self.files:           # parse the file name and create the SongFile objects in the DB            so = so.replace('\n', '')            so = so.replace('.aiff', '.mp3')            lst = so.split('+')         # name like 'annie_lennox+Medusa+03-A_Whiter_Shade_Of_Pale.aiff'            ar = lst[0]                 # = artist + album + title            al = lst[1]            sn = lst[2]            sn = sn[3:]                 # clean up title: prefix #, quotes, etc.            sn = sn.replace('.mp3', '')            sn = sn.replace('_t_', '\'t ')            sn = sn.replace('_s_', '\'s ')            sn = sn.replace('_m_', '\'m ')            sn = sn.replace('_', ' ')            ar = ar.replace('_', ' ')            ar = ar.title()                                        # now create the SongFile object and save it            if cnt == ln:                return            sf = SongFile(fnam = sfo + so, art = ar, tit = sn, alb = al, ind = cnt, mat = self.data[cnt])            # print(sfo + so)            sf.save()            cnt = cnt + 1#            if cnt > 5: break        # print('------------', sf, '---', sf.mat)        # print 1 for debugging    def normalize(self, list_file, csv_file):        "Normalize the data so the max off-axis value is 100"                            # read the match table (TSV)        print(' -- read the match table')        csv_f = self.folder + csv_file        tsvFi = open(csv_f, 'r')        data = tsvFi.readlines()        tsvFi.close()        ln = len(self.data[0])        print(' --', csv_file, '--', ln, 'rows')        print(data[0])#        for ix in range(ln):#            print(data[in])