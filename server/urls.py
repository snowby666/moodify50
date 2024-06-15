from django.urls import include
from django.urls import path, re_path
from . import views
app_name = 'server'
urlpatterns = [
    path('', views.index, name='index'),
    
    path('logout/', views.logOut, name='logout'),
    path('login/', views.logIn, name='login'),
    path('signup/', views.signup, name='signup'),
    
    path('search/', views.search, name='search'),
    path('loadLyrics/', views.get_lyrics, name='loadLyrics'),
    path('loadTrack/', views.get_track, name='loadTrack'),
    path('loadAlbum/', views.get_album, name='loadAlbum'),
    path('loadArtist/', views.get_artist, name='loadArtist'),
    path('results/', views.search_results_view, name='search_results_view'),    
    
    path('generate/', views.generate, name='generate'),
    path('survey/', views.survey, name='survey'),
    path('edit/', views.edit_preference, name='edit'),

    path('createPlaylist/', views.create_playlist, name='createPlaylist'),
    path('saveToPlaylist', views.save_to_playlist, name='saveToPlaylist'),
    path('loadFavorites/', views.load_favorites, name='loadFavorites'),
    path('deletePlaylist/', views.delete_playlist, name='deletePlaylist'),
    path('renamePlaylist/', views.rename_playlist, name='renamePlaylist'),
    path('removeTrack/', views.remove_track, name='removeTrack'),
]