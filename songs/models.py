#
# Create song DB models
#

from django.db import models
import collections

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
        # print('Inds:', inds)      # [(0, 3.57), (98, 0.194), (36, 0.128), (50, 0.125), ... (46, 0.0985)]
        return inds
            
