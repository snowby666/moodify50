from django.db import models
import datetime
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
import json
# Create your models here.


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to = "server/static/server/users/", default = "server/static/server/users/defaultuser.gif", null =True)
    hasSurvey = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
class UserMusic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    market = models.CharField(max_length=100)
    genre = models.CharField(max_length=1000)
    singer = models.JSONField(default=dict)
    
    def set_genre(self, data):
        self.genre = json.dumps(data)
        
    def load_genre(self):
        return json.loads(self.genre)
    
    # def set_singer(self, data):
    #     self.singer = json.dumps(data)
    
    # def load_singer(self):
    #     return json.loads(self.singer)
        
    def __str__(self):
        return self.user.username
    
class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created = models.DateTimeField(default=timezone.now)
    
    @property
    def tracksCount(self):
        return Track.objects.filter(playlist=self).count()
    
    def __str__(self):
        return self.name

class Track(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    trackurl = models.CharField(max_length=255, null=True)
    artist = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    album = models.CharField(max_length=255)
    duration = models.IntegerField(default=0)
    image = models.CharField(max_length=255)
    published_date = models.CharField(max_length=255)   
    artistId = models.CharField(max_length=255, default="")
    albumId = models.CharField(max_length=255, default="")
    
    def __str__(self):
        return self.name