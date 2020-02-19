#
# CSD song DB models
#

from django.db import models
import sys, subprocess, platform

# Song class has name, title, file...

class SongFile(models.Model):
    "SongFile: file_name, artist, album, title, matches, weight, index"
    fnam = models.CharField(max_length=200, default="")
    art = models.CharField(max_length=100, default="")
    alb = models.CharField(max_length=100, default="")
    tit = models.CharField(max_length=100, default="")
    mat = models.CharField(max_length=2000, default="")
    wht = models.FloatField(default=0)
    ind = models.IntegerField(default=-1)

    def __str__(self):
        "Required string name"
        return(self.fnam)
#        return (self.art + ' - ' + self.tit)

    def matches(self):
        "Return a sorted list of the song's match IDs & weights."
        lst = list(map(float, self.mat.split('\t')))
        # print('Matches:', lst)
        dct = { }
        for ind in range(len(lst)):
            dct[ind] = lst[ind]
        # print('Matches:', dct)
        inds = sorted(dct.items(), key = lambda kv: (kv[1], kv[0]), reverse=True)
        inds = inds[:16]
        return inds

#-----------------------------------------

class SongMatcher(models.Model):
    "Matcher for song objects"
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    
    def __init__(self):
#        print(' -- create the SongMatcher')
        if platform.system() == 'Linux':
            self.octave = '/usr/bin/octave'
            self.sdir = '/home/stp/Code/trqk-cover-song-detection/scripts/Chrm_DTW/'
        else:
            self.octave = '/opt/local/bin/octave'
            self.sdir = '/Users/stp/Code/CoSoDe/trqk-csd/scripts/Chrm_DTW/'
        # shell args: octave script, list file, chgrm folder

    def __str__(self):
        "Required string name"
        return('SongMatcher')

    def match1(self, son_nam):
        "Given a song file, analyze it and match against the stored DB; return the db index of the new song."
#        print(' -- running SongMatcher match1')

        # /opt/local/bin/octave -p /Users/stp/Code/CoSoDe/trqk-csd/scripts/Chrm_DTW/ /Users/stp/Code/CoSoDe/trqk-csd/scripts/Chrm_DTW/RunOneSong.m 
        #     /Users/stp/Code/CoSoDe/trqk-csd/scripts/Chrm_DTW/list_stp.txt /Users/stp/Code/CoSoDe/trqk-csd/scripts/Chrm_DTW/ChrmGrms0/ 
        #     /var/folders/74/xv0vn6s92ml1dt5dnjg8czdw0000gn/T/tmpskhumyk9.upload.mp3

        args = ' ' + self.sdir + 'RunOneSong.m ' + self.sdir + 'list_stp.txt ' + self.sdir + 'ChrmGrms0/ '
        cmd = self.octave + ' -p ' + self.sdir + args + son_nam        # create octave command with file name
#        print(cmd)
        sys.stdout.flush()
        try:
            proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)      # fork octave process and wait
            ret_code = proc.wait()
            if ret_code != 0:
                print('Error running octave command')
                return 0
            res = proc.stdout.readlines()
            sys.stdout.flush()
            cnt = 1
            for line in res:                            # loop to process result list
                lstr = str(line, 'utf-8').rstrip()      # 99 | 48.3721 | elliott_smith+Either_Or+04-Between_The_Bars.aiff
#                print(": " + lstr)
                if lstr == '--Results--':
                    ind0 = cnt
                if lstr == '--End--':
                    ind1 = cnt
                cnt = cnt + 1
 #           print('--', ind0, ':', ind1)
            dct = { }
            for i in range(ind0, ind1 - 1):             # now create a dict of the weights
                lstr = str(res[i], 'utf-8').rstrip()
                toks = lstr.split(' | ')                # ['139', '29.394', 'simon_and_garfunkel+Bookends+03-America.aiff']
                dct[toks[0]] = toks[1]
#            print(dct)
            cnt = len(SongFile.objects.all()) + 1       # now create the SongFile object and save it
            sf = SongFile(fnam = son_nam, art = son_nam, tit = son_nam, alb = son_nam, ind = cnt, mat = dct)
            sf.save()
            return cnt
        except Exception as inst:
            print('Error running octave for file \"' + son_nam + '\"')
            print(str(inst))
            return 0

    def match2(self, son1_nam, son2_nam):
        "Given 2 song files, analyze and match them against one another."

        args = ' ' + self.sdir + 'RunSongPair.m ' + self.sdir + 'list_stp.txt ' + self.sdir + 'ChrmGrms0/ '
        cmd = self.octave + ' -p ' + self.sdir + args + son1_nam + ' ' + son2_nam    # create octave command with file names
        print(cmd)
        sys.stdout.flush()
        try:
            proc = subprocess.Popen(cmd.split(), stdout = subprocess.PIPE)      # fork octave process and wait
            ret_code = proc.wait()
            if ret_code != 0:
                print('Error running octave command')
                return 0
            res = proc.stdout.readlines()
            sys.stdout.flush()
            cnt = 1
            for line in res:                            # loop to process result list
                lstr = str(line, 'utf-8').rstrip()      # 99 | 48.3721 | elliott_smith+Either_Or+04-Between_The_Bars.aiff
                if lstr == '--Results--':
                    ind0 = cnt
                cnt = cnt + 1
            lstr = str(res[ind0], 'utf-8').rstrip()
            print('---', lstr, '---')
            return lstr
        except Exception as inst:
            print('Error running octave for file \"' + son1_nam + '\"')
            print(str(inst))
            return 0

        
        
