## Set up the list of URL paterns/paths for the server#from django.urls import pathfrom django.views.decorators.csrf import csrf_exemptfrom . import viewsapp_name = 'songs'urlpatterns = [        # http://127.0.0.1:8000/songs/    path('', views.StartView.as_view(), name='start'),        # http://127.0.0.1:8000/songs/list    path('list/', views.IndexView.as_view(), name='list'),        # http://127.0.0.1:8000/songs/list/matches/4    path('list/matches/<index>/', views.MatchesView.as_view(), name='matches'),        # http://127.0.0.1:8000/songs/match1/    path('match1/', views.Match1View.as_view(), name='match1'),        # http://127.0.0.1:8000/songs/match2/    path('match2/', views.Match2View.as_view(), name='match2'),        # http://127.0.0.1:8000/songs/matchResults/    path('matchResults/', views.MatchResultsView.as_view(), name='matchResults'),        # http://127.0.0.1:8000/songs/csd/    path('csd/', csrf_exempt(views.Match1JSON.as_view()), name='matchJSON'),]