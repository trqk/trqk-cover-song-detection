#
# View classes for the Django front end to the Trqk cover-song detection demo code
#
#     @author: stephenp@trqk.io - 2001
# 	Copyright (C) 2020 Stephen T. Pope & Trqk, LLC. All rights reserved.
# 	THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.
# 	The copyright notice above does not evidence any actual or intended publication
# 	of such source code.

from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from django import forms
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from .models import SongFile, SongMatcher
from .forms import FileNameForm, FileNameForm2
import ast, json, os
import urllib.parse
import requests
import boto3

# globals

gConfig = 0

#----------------------------------------------------------------------------------------
#
# Configuration class - Describes system settings; loaded from JSON at the start
#

class Configuration(object):
    "Describes a collection of features and system settings"

    def __init__(self):
        "Initialize the Configuration object"
        global gConfig                              # global config object (me)
        gConfig = self
        self.log_to_CW = False                       # log to AWS cloudwatch
        if self.log_to_CW:
            self.b3Client = boto3.client('logs')
            respD = self.b3Client.describe_log_streams(logGroupName = 'SndsLikeLogging', 
                                                logStreamNamePrefix = 'AnalysisLog', limit = 1)
            try:
                resCode = respD['ResponseMetadata']['HTTPStatusCode']
                if resCode == 200:
                    self.log_seq_tok = respD['logStreams'][0]['uploadSequenceToken']
            except Exception as inst:
                print('Error connecting to logging service - exiting')
                print(inst)
        try:                                        # Load system settings from JSON file
            jsNam = 'SL_Settings.json'
            if not os.path.isfile(jsNam):
                jsNam = '../SL_Settings.json'
            setFile = open(jsNam, 'r')
            stri = setFile.read()
            settings = json.loads(stri)
            self.dict = settings
        except Exception as inst:
            print('Error reading/parsing settings file \"SL_Settings.json\" - exiting')
            print(inst)

        self.do_debug = settings['debug_me']         # Debugging flag
        self.folder = settings['folder']    
        self.dbName = settings['db_name']            # DB conn parameters and table names
        self.tableName = settings['db_tableName']
        self.normName = settings['db_normName']
        self.host = settings['db_host']
        self.user = settings['db_user']
        self.passwd = settings['db_passwd']
        self.had_error = False                       # whether there were any processing errors
        self.error_msg = 'No analysis errors'
        self.kw_args = dict(charset='utf8', use_unicode=True)
        self.doTiming = settings['do_timing']
        self.use_s3_store = settings['use_s3_store']

    def get_err(self, key):
        "Answer an error message from the settings file"
        return self.dict[key]

#----------------

class StartView(generic.View):
    template_name = 'songs/index.html'

    def get(self, request):
        "Display the file name form"
        return render(request, 'songs/index.html')

class IndexView(generic.ListView):
    template_name = 'songs/list.html'
    context_object_name = 'song_list'

    def get_queryset(self):
        """Return the list of songs"""
        return SongFile.objects.all()

class MatchesView(generic.ListView):
    template_name = 'songs/matches.html'
    context_object_name = 'song_list'

    def get_queryset(self):
        """Return the list of songs"""
        song = self.get_song()
        print('Song:', song, '--', str(song.ind))
        mdct = self.get_matches(song)         # ANS: [(0, 3.57), (98, 0.194), (36, 0.128), ... (46, 0.0985)]
        ks = []
        vs = []
#        print(mdct)
        for a, b in mdct:
            ks.append(a)
            vs.append(b)
#        print(ks)
        qset = SongFile.objects.filter(ind__in = ks)
#        print(qset.all())
        for so in qset:
            ind = so.ind
            wt = -1
            for tp in mdct: 
                if tp[0] == ind:
                    wt = tp[1]
                    break
            so.wht = wt
            so.save()
        qset = qset.order_by('wht').reverse()
        # for so in qset:
        #     print('Mt:', so, '--', str(so.ind), '--', str(so.wht))
        return qset

    def get_matches(self, song):
        "Answer the song matches for the given song"
        return song.matches()         # ANS: [(0, 3.57), (98, 0.194), (36, 0.128), ... (46, 0.0985)]

    def get_song(self):
        "Answer the selected match song"
        which = self.kwargs['index']
        print('----IND:', which)
        song = SongFile.objects.filter(ind = which).first()
        return song


class Match1View(generic.View):
    "View for the match-1-song demo"
    form_class = FileNameForm
    initial = {'key': 'value'}
    template_name = 'songs/match1song.html'

    def get(self, request):
        "Display the file name form"
#        print('---', request.method, '---')
        form = FileNameForm()                   # display the file name form
        return render(request, 'songs/match1song.html', {'form': form})
   
    def post(self, request, *args, **kwargs):
        "Post = run 1-song match and display the results"
        form = FileNameForm(request.POST, request.FILES)
        if form.is_valid():
            print('---', form.cleaned_data['file_name'].temporary_file_path(), '---')
            sndf = form.cleaned_data['file_name'].temporary_file_path()
                                        # run the match in octave
            inx = self.runMatch1(sndf)  # returns index of new file ---------------
                                        # make the response list
#            inx = SongFile.objects.all().last().ind
            song = SongFile.objects.filter(ind = inx).first()
#            print('===', inx)
#            print('===', song.tit)
#            print('===', song.mat)
            qset = SongFile.objects.all()
            ks = []
            vs = []
            mdct = ast.literal_eval(song.mat)
#            print('===', mdct)
#            print('===', type(mdct))

            for key in mdct.keys():
                ks.append(int(key))
                vs.append(float(mdct[key]))
#            print('===', ks)
#            print('===', vs)
            qset = SongFile.objects.filter(ind__in = ks)
            for so in qset:
                ind = so.ind
                so.wht = mdct[str(ind)]
                so.save()
            qset = qset.order_by('wht').reverse()
            context = {'song_list': qset }
            template = loader.get_template('songs/matches.html')
            return HttpResponse(template.render(context, request))
        return render(request, self.template_name)

    def runMatch1(self, fnam):
        "Run the match after selecting the target song"
        print('Matching', fnam)
        sm = SongMatcher()
        ret = sm.match1(fnam, False)
        return ret


class MatchResultsView(MatchesView):

    def get_song(self):
        "Answer the selected match song"
        so =  SongFile.objects.all().last()
        print('----INX:', so.ind)
        return so


class Match2View(generic.View):
    "View for the match-2-songs demo"
    form_class = FileNameForm2
    initial = {'key': 'value'}
    template_name = 'songs/match2songs.html'

    def get(self, request):
        "Display the file name form"
#        print('---', request.method, '---')
        form = FileNameForm2()                   # display the file name form
        return render(request, 'songs/match2songs.html', {'form': form})

    def post(self, request, *args, **kwargs):
        "Post = run 1-song match and display the results"
#        print('---', request.method, '---')
        form = FileNameForm2(request.POST, request.FILES)
        if form.is_valid():
            sndf1 = form.cleaned_data['file_nam1'].temporary_file_path()
            sndf2 = form.cleaned_data['file_nam2'].temporary_file_path()
                                        # run the match in octave
            res = self.runMatch2(sndf1, sndf2)  # returns match message ---------------
                                        # make the response list
            msg = 'Matching Results: \r\n' + res + '\r\n'
            return HttpResponse(msg)

            # return HttpResponse(template.render(context, request))
        return render(request, self.template_name)

    def runMatch2(self, fnam1, fnam2):
        "Run the match after selecting the 2 target songs"
#        print('Matching', fnam1, 'and', fnam2)
        sm = SongMatcher()
        rtv = sm.match2(fnam1, fnam2)
        return rtv

# CSD JSON Formats
#
#Input:
# { 
#   url: valid_url_string_to_S3_or_elsewhere, // if just this, then compare vs reference library
#   reference: valid_url_string_to_S3_or_elsewhere // optional for comparison of 2 tracks
# }
#
# Output:
# // if CSD matches to provided reference or reference library (i.e. score > 1), 
# // then matches contains the individual matches and scores
# //
# // if no matches (i.e. CSD scores nothing > 1), the matches array is EMPTY
# //
# {
#   matches: [              // always present, but may be EMPTY if no matches found
#     {
#       score: Float,
#       title: String,
#       artist: String,
#       url: valid_url_string_to_S3_or_elsewhere   // could be null or reference url above valid_url_string_to_S3_or_elsewhere
#     },
#     { ... }              // may contains one or more matches
#   ]
# }

class Match1JSON(generic.View):
    "View for the match-1-song app that answers JSON"
  
    @csrf_exempt 
    def post(self, request, *args, **kwargs):
        "Post = run 1-song match and display the results"
#        print('--- Match1JSON.POST ---')
#        print(request.META['QUERY_STRING'])
        di = QueryDict(request.META['QUERY_STRING'])
#        print(di)
        match2 = False
        reff = ''
        try:
            sndf = di['url'] # [0] # .decode('utf-8')
            if 'reference' in di:
                reff = di['reference'] # [0] # .decode('utf-8')
#                print('--- ref file fnd', reff,' ---')
                match2 = True
        except Exception as inst:
            print('POST arg unpacking error', inst)
#        print('--- snd files:', sndf, '---', reff, '---')

        gConfig.had_error = False
        self.fSiz = 0
        if match2:                  # 2 files
            self.fileURL = sndf
            pos = sndf.rfind('/')                # find tail of name
            if pos < 0: pos = 0
            pos2 = sndf.rfind('.')               # find name extension
            if pos2 < 0: pos2 = len(sndf)
            self.filename = sndf[(pos + 1) : pos2]
            self.localFName = '/tmp/' + sndf[(pos + 1) : ]
            self.fileExt = sndf[pos2 : ]
            
            self.fileURL2 = reff
            pos = reff.rfind('/')                # find tail of name
            if pos < 0: pos = 0
            pos2 = reff.rfind('.')               # find name extension
            if pos2 < 0: pos2 = len(reff)
            self.filename2 = reff[(pos + 1) : pos2]
            self.localFName2 = '/tmp/' + reff[(pos + 1) : ]
            self.fileExt2 = reff[pos2 : ]

            return self.match2()
        else:                       # single file
            self.fileURL = sndf
            pos = sndf.rfind('/')                # find tail of name
            if pos < 0: pos = 0
            pos2 = sndf.rfind('.')               # find name extension
            if pos2 < 0: pos2 = len(sndf)
            self.filename = sndf[(pos + 1) : pos2]
            self.localFName = '/tmp/' + sndf[(pos + 1) : ]
            self.fileExt = sndf[pos2 : ]
            
            return self.match1()

    def match1(self):
        "Perform match between a song and the default data set; answer JSON"
        if len(self.fileURL):
            print('--- match1:', self.fileURL, '---')
            self.get_snd_file(self.fileURL, self.localFName)         # Fetch snd file
            if gConfig.had_error or self.fSiz == 0:
                print('Uncaught file fetch error')
                gConfig.error_msg = gConfig.get_err('file_fetch_err')
#                self.send_nogo()
                return
            sm = SongMatcher()          # run the match in octave
            dct = sm.match1(self.localFName, True)   # returns match dict ---------------
                                        # make the response list
            js_text = '{  "matches": ['
            ks = list(dct.keys())
            for ind in range(8):            # answer top 8 matches
                mval = ks[ind]
                mstr = dct[mval]            # 'annie_lennox+Medusa+09-Waiting_In_Vain.aiff'
                toks = mstr.split('+')
                if len(toks) != 3:          # other name formats (no '+')
                    toks = ['', '', '']
                js_text += '{ "score": ' + mval + ', "title": "' + toks[2] + '", "artist": "' + toks[0] + '", "url": "' + mstr + '" }, '
            js_text = js_text[:-2]          # drop last comma
            js_text += ' ] }'
            print(js_text)
            return HttpResponse(js_text, content_type="application-json")

    def match2(self):
        "Perform match between 2 songs; answer JSON"
        if len(self.fileURL):
            print('--- match2: ', self.fileURL, '---', self.fileURL2, '---')
            self.get_snd_file(self.fileURL, self.localFName)         # Fetch snd file
            if gConfig.had_error or self.fSiz == 0:
                print('Uncaught file fetch error')
                gConfig.error_msg = gConfig.get_err('file_fetch_err')
#                self.send_nogo()
                return
            self.get_snd_file(self.fileURL2, self.localFName2)         # Fetch snd file
            if gConfig.had_error or self.fSiz == 0:
                print('Uncaught file fetch error')
                gConfig.error_msg = gConfig.get_err('file_fetch_err')
#                self.send_nogo()
                return
            
            sm = SongMatcher()          # run the match in octave
            ret = sm.match2(self.localFName, self.localFName2)   # returns match string "WaitingInVain,  -- 08-Electricity,  = 8.83"
                                        # make the response list
            pos = ret.rfind(' ')                # find tail of name
            if pos < 0: pos = -1
            mat = ret[pos + 1:]
            toks = self.fileURL.split('+')
            if len(toks) != 3:          # other name formats (no '+')
                toks = ['', '', '']
            js_text = '{  "matches": [ { "score": ' + mat + ', "title": "' + toks[2] + '", "artist": "' + toks[0] + '", "url": "' + self.fileURL + '" } ] }'
            print(js_text)
            return HttpResponse(js_text, content_type="application-json")

    def get_snd_file(self, sndF, tmpF):
        "Fetch snd file"                     # using URL fetch
        global gConfig
        pos = sndF.find('.s3.')              # is this an S3 URL?
        if gConfig.use_s3_store and pos > 0: # fetch from S3 bucket
            try:                             # the request gets the data
                bucket, filename = self.get_bucket_and_key_from_url(sndF)
                print('S3: ', bucket, 'f', filename)
                self.download_file_from_s3(bucket, filename)
                fSiz = os.path.getsize(tmpF)
                log_msg('\tCopied ' + str(fSiz) + ' bytes from S3 to ' + tmpF)
                self.fSiz = fSiz
                return
            except Exception as inst:
                log_msg('Fetch S3 snd file error 0')
                log_msg(str(inst))
                self.fSiz = 0
                gConfig.had_error = True
        elif sndF.startswith('http://') or sndF.startswith('https://'):
            self.fSiz = 0
            try:                             # the request gets the data
                log_msg('Loading ' + sndF + ' to ' + tmpF + '...')
                req = requests.get(sndF, allow_redirects = True)
                if req.status_code != 200:  # or not...
                    log_msg('Error getting file; response:' + str(req.status_code))
                    raise Exception('Error getting data file ' + sndF)
                ckSz = 128 * 1024           # read in 128 kB chunks
                with open(tmpF, 'wb') as outF:
                    for chunk in req.iter_content(chunk_size = ckSz):    # read/write loop
                        if chunk:
                            outF.write(chunk)
                outF.close()
                fSiz = os.path.getsize(tmpF)
                log_msg('\tCopied ' + str(fSiz) + ' bytes to ' + tmpF)
                self.fSiz = fSiz
            except Exception as inst:
                log_msg('Fetch snd file error 1')
                log_msg(str(inst))
                self.fSiz = 0
                gConfig.had_error = True
        else:
            log_msg('Using local file')


    def download_file_from_s3(self, bucketname, filename):
        "From JT; fetch a file from an S3 bucket"
#        global gConfig
        s3c = boto3.client('s3')
        with open(self.localFName, 'wb') as f:
            s3c.download_fileobj(bucketname, filename, f)

    def get_bucket_and_key_from_url(self, url):
        "From JT; parse a URL into a bucket and key"
        parsed_url = urllib.parse(url)
        bucket = parsed_url.netloc.split('.')[0]
        key = parsed_url.path[1:]
        key = key.replace('%3A', ":")
        return (bucket, key)


def log_msg(msg):
    print(msg)

