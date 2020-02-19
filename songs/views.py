#
# View classes for the Django front end to the Trqk cover-song detection demo code
#
#     @author: stephenp@trqk.io - 2001
# 	Copyright (C) 2020 Stephen T. Pope & Trqk, LLC. All rights reserved.
# 	THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE.
# 	The copyright notice above does not evidence any actual or intended publication
# 	of such source code.

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from django import forms
from django.template import loader

from .models import SongFile, SongMatcher
from .forms import FileNameForm, FileNameForm2
import ast

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

    # def get(self, request, *args, **kwargs):
    #     form = self.form_class(initial=self.initial)
    #     return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        print('---', request.method, '---')
        form = self.form_class(request.POST)
        print('---', request.POST, '---')
        print('---', form.form.cleaned_data, '---')
        if form.is_valid():
            # <process form cleaned data>
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, {'form': form})
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
        ret = sm.match1(fnam)
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

