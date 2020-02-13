# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import SongFile
from django.views import generic
from django.shortcuts import render

#----------------

class IndexView(generic.ListView):
    template_name = 'songs/index.html'
    context_object_name = 'song_list'

    def get_queryset(self):
        """Return the list of songs"""
        return SongFile.objects.all()

class MatchesView(generic.ListView):
    template_name = 'songs/matches.html'
    context_object_name = 'song_list'

    def get_queryset(self):
        """Return the list of songs"""
        self.which = self.kwargs['index']
#        print('IND:', self.which)
        song = SongFile.objects.filter(ind = self.which).first()
#        print('Song:', song, '--', str(song.ind))
        mdct = song.matches()         # ANS: [(0, 3.57), (98, 0.194), (36, 0.128), ... (46, 0.0985)]
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


class Match1View(generic.ListView):
    template_name = 'songs/match1song.html'
    context_object_name = 'song_list'

    def get_queryset(self):
        """Return the list of songs"""
        self.which = self.kwargs['index']
#        print('IND:', self.which)
        song = SongFile.objects.filter(ind = self.which).first()
#        print('Song:', song, '--', str(song.ind))
        mdct = song.matches()         # ANS: [(0, 3.57), (98, 0.194), (36, 0.128), ... (46, 0.0985)]
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


#------------------------------

# def index(request):
#     song_list = SongFile.objects.order_by('id')
#     context = {'song_list': song_list }
#     return render(request, 'songs/index.html', context)

#

# def matches(request, song_id):
#     song = get_object_or_404(SongFile, pk = song_id)
#     match_list = song.matches()
#     context = { 'song': song, 'matches' : match_list[:8] }
#     return render(request, 'songs/matches.html', context)

#
        
# def home(request):
#     song_list = SongFile.objects.order_by('id')
#     context = { 'song_list': song_list }
#     return render(request, 'base.html', context)

