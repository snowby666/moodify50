from django.contrib import admin
from datetime import datetime
from server.models import *
from django.db.models import F, Count
from . import models
from import_export.admin import ImportExportMixin
from django.utils import timezone

class UserPlugin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('user', 'hasSurvey')
    
class UserMusicPlugin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('user','market','genre','singer')
    
class PlaylistPlugin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('user', 'name', 'created', 'tracksCount')
    
    list_filter = ('user',)
    
    def tracksCount(self, obj):
        return obj.tracksCount
    
class TrackPlugin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('user', 'playlist', 'trackurl', 'artist', 'name', 'album', 'duration', 'image', 'published_date', 'artistId', 'albumId')
    
    list_filter = ('playlist',)
    
    def user(self, obj):
        return obj.playlist.user

admin.site.register(UserProfileInfo, UserPlugin)
admin.site.register(UserMusic, UserMusicPlugin)
admin.site.register(Playlist, PlaylistPlugin)
admin.site.register(Track, TrackPlugin)

admin.site.site_header = 'Moodify50 Admin'