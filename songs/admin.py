# Register your models here.

from django.contrib import admin

from .models import SongFile, SongMatcher

admin.site.register(SongFile)
admin.site.register(SongMatcher)

