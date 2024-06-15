from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F, Q, Value
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from . import models, forms
from django.utils import timezone
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
import random, json, os
import requests
import re

from .musicapi import MusicPlayer
jsonDec = json.decoder.JSONDecoder()

API_KEYS = [
    {'client_id': '48770ee144fe44679cd8bb60106e26ca', 'client_secret': '3a49c3b8b2bc410ebf1cbf8f283ccc8a'},
    {'client_id': 'c9ae1e5b831c439291916ada2e0b0927', 'client_secret': '103fa5e6a35f464eb16cf5b534a719c1'},
    {'client_id': 'f50d7a603a4c40e0b2ea0af9520e49a5', 'client_secret': '820674e2a9e549d987eb2f69b1626663'},
    {'client_id': '56e2e324b381496a8cb530e78a986861', 'client_secret': 'd1ae48fe21784d2990e8b722952a11cd'}
]

# web service
def error_404(request, exception):
    return render(request, '404.html')

def error_500(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response

def error(request, exception):
    print(exception)
    logOut(request)
    
def sitemap(request):
    return render(request, 'sitemap.xml', content_type = 'text/xml')

def manifest(request):
    return render(request, 'manifest.json', content_type = 'application/json')
    
# Create your views here.
@login_required
def index(request):
    # Check if the user is logged in
    try:
        if request.user.is_authenticated:
            if request.session.get('spotify_state', 0):
                # check if user has UserProfile
                if not models.UserProfileInfo.objects.filter(user__username=request.user.username).exists():
                    models.UserProfileInfo.objects.create(user=request.user)
            if not models.UserProfileInfo.objects.get(user__username=request.user.username).hasSurvey:
                return redirect('server:survey')
            return render(request, 'index.html')
        else:
            return redirect('server:login')
    except Exception as e:
        print(e)
        logOut(request)

@login_required
def load_favorites(request):
    if request.user.is_authenticated:
        # Load saved playlist and its tracks
        savedPlaylist = models.Playlist.objects.filter(user=request.user).order_by('-created')
        playlist = []
        for i in savedPlaylist:
            tracks = models.Track.objects.filter(playlist=i)
            trackList = []
            for j in tracks:
                trackList.append({
                    'trackurl': j.trackurl,
                    'artist': j.artist,
                    'name': j.name,
                    'album': j.album,
                    'duration': j.duration,
                    'image': j.image,
                    'published_date': j.published_date,
                    'artistId': j.artistId,
                    'albumId': j.albumId,
                })
            playlist.append({
                'id': i.id,
                'playlist': i.name,
                'tracksCount': i.tracksCount,
                'created': format_created_date(i.created),
                'tracks': trackList
            })
        return JsonResponse({'savedPlaylist': playlist})

def format_created_date(created):
    if created.date() == timezone.now().date():
        
        if timezone.now().hour - created.hour == 0:
            if timezone.now().minute - created.minute == 0:
                return "Just now"
            if timezone.now().minute - created.minute == 1:
                return f"{timezone.now().minute - created.minute} min ago"
            return f"{timezone.now().minute - created.minute} mins ago"
        
        if timezone.now().hour - created.hour == 1:
            return f"{timezone.now().hour - created.hour} hour ago"
        
        if timezone.now().hour - created.hour > 1:
            return f"{timezone.now().hour - created.hour} hours ago"
        
    return created.strftime('%B %d, %Y')
        
def call_spotify_api(endpoint, **kwargs):
    temp = API_KEYS
    attemps = len(temp)
    while attemps > 0:
        try:
            client = MusicPlayer(temp[0])
            response = getattr(client, endpoint)(**kwargs)
            return response
        except Exception as e:
            temp.pop()
            print(e)
            attemps -= 1
            continue
    return []

@login_required
def generate(request):
    if request.method == "POST":
        emotion = request.POST.get("mood")
        popularType = request.POST.get("type")
        
        pop = 100 if popularType == 'most_popular' else 0
        
        userMusic = models.UserMusic.objects.get(user=request.user)
        market = userMusic.market
        artists = list(userMusic.singer.values())
        genres = jsonDec.decode(userMusic.genre)
        
        songsURL = generate_playlist(artists, emotion, genres, market, pop)
        return JsonResponse({'songsURL': songsURL})  
    return redirect('server:index')

def generate_playlist(artists, emotion, genres, market, pop, searchType=0):
    if searchType == 3:
        return []

    songsURL = []

    # Split the list of artists into chunks of 4
    artist_chunks = [artists[i:i+4] for i in range(0, len(artists), 4)]

    for chunk in artist_chunks:
        chunk_songsURL = call_spotify_api('get_recommendations', artistsIds=chunk, emotion=emotion, genres=genres, market=market, pop=pop, searchType=searchType)
        songsURL.extend(chunk_songsURL)

    if songsURL != []:
        # shuffle the dictionary of songs
        random.shuffle(songsURL)
        return songsURL[:20]
    else:
        generate_playlist(artists, emotion, genres, market, pop, searchType + 1)

@login_required
@api_view(['GET', 'POST'])
def get_lyrics(request):
    if request.user.is_authenticated and request.method == "POST":
        if request.data.get("trackId", "") != "":
            track_id = request.data["trackId"]
            lyrics = call_spotify_api('get_lyrics', track_id=track_id)
            if lyrics == {}:
                return JsonResponse({
                    'status': 'no_lyrics',
                    })
            return JsonResponse({
                'status': 'success',
                'data': lyrics
                })
        return JsonResponse({
            'status': 'error',
            })
    else:
        return redirect('server:index')    
     
@login_required
@api_view(['GET', 'POST'])
def search(request):
    if request.user.is_authenticated and request.method == "POST":
        if request.data.get("query", "") != "":
            query = request.data["query"]
            search_type = request.data["search_type"]
            market = request.data["market"]
            search_results = call_spotify_api('search_items', query=query, search_type=search_type, market=market)
            return JsonResponse({
                'status': 'success',
                'search_results': search_results
                })
        return JsonResponse({
            'status': 'error',
            'search_results': {}
            })
    else:
        return redirect('server:index')

def search_results_view(request):
    if request.user.is_authenticated and request.GET.get('query', '') != '':
        query = request.GET.get('query', '')
        search_results = call_spotify_api('search_items', query=query, search_type='artist', market=None)
        search_results = search_results["artists"]["items"]
        
        if len(search_results) > 4:
            search_results = search_results[:4]

        for i in search_results:
            if len(i['images']) > 0:
                i['image'] = i['images'][0]['url']
            else:
                i['image'] = "https://www.thermaxglobal.com/wp-content/uploads/2020/05/image-not-found.jpg"
    else:
        search_results = []
    return render(request, 'search_results.html', {'search_results': search_results})

@login_required
@api_view(['GET', 'POST'])
def get_track(request):
    if request.user.is_authenticated and request.method == "POST":
        if request.data.get("trackId", "") != "":
            track_id = request.data["trackId"]
            track_items = call_spotify_api('get_track_items', track_id=track_id)
            return JsonResponse({
                'status': 'success',
                'track_items': track_items
                })
        return JsonResponse({
            'status': 'error',
            'track_items': {}
            })
    else:
        return redirect('server:index')

@login_required
@api_view(['GET', 'POST'])
def get_album(request):
    if request.user.is_authenticated and request.method == "POST":
        if request.data.get("albumId", "") != "":
            album_id = request.data["albumId"]
            album_items = call_spotify_api('get_album_items', album_id=album_id)
            # log to json file
            # json.dump(album_items, open("album.json", "w"), indent=4)
            return JsonResponse({
                'status': 'success',
                'album_items': album_items
                })
        return JsonResponse({
            'status': 'error',
            'album_items': {}
            })
    else:
        return redirect('server:index')

def get_extra_data(artist_id):
    url = f'https://open.spotify.com/artist/{artist_id}'
    response = requests.get(url)
    html = response.text
    
    monthly_listeners_match = re.search(r'(\d{1,3}(,\d{3})*|\d+) monthly listeners</div>', html)
    about_match = re.search(r'<span class="Type__TypeElement-sc-goli3j-0 kmjYak G_f5DJd2sgHWeto5cwbi" data-encore-id="type">(.*?)</span>', html, re.DOTALL)

    if monthly_listeners_match:
        monthly_listeners = monthly_listeners_match.group(1)
        # print(f'Monthly listeners: {monthly_listeners}')
    else:
        monthly_listeners = 'Not available'
        print('Monthly listeners count not found')

    if about_match:
        about = about_match.group(1)
        # print(f'About: {about}')
    else:
        about = ''
        print('About section not found')
        
    return {
        'artistMonthlyListeners': monthly_listeners,
        'artistAbout': f"{about}",
    }

@login_required
@api_view(['GET', 'POST'])
def get_artist(request):
    if request.user.is_authenticated and request.method == "POST":
        if request.data.get("artistId", "") != "":
            artist_id = request.data["artistId"]
            artist_items = call_spotify_api('get_artist_items', artist_id=artist_id)

            extra_data = get_extra_data(artist_id)
            artist_items.update(extra_data)
            
            # json.dump(artist_items, open("artist.json", "w"), indent=4)
            return JsonResponse({
                'status': 'success',
                'artist_items': artist_items
                })
        return JsonResponse({
            'status': 'error',
            'artist_items': {}
            })
    else:
        return redirect('server:index')

@login_required
@api_view(['GET', 'POST'])
def create_playlist(request):
    if request.user.is_authenticated and request.method == "POST":
        if request.data is not None:
            try:
                playlistName = request.data["playlistName"]
                # check if the playlist name already exists
                if not models.Playlist.objects.filter(user=request.user, name = playlistName).exists():
                    newPlaylist = models.Playlist(
                        user = request.user,
                        name = playlistName
                    )
                    newPlaylist.save()
                    return JsonResponse({'status': 'success'})
                return JsonResponse({'status': 'duplicate'})
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'error'})
        return JsonResponse({'status': 'error'})
    return redirect('server:index')

            
@login_required
@api_view(['GET', 'POST'])
def save_to_playlist(request):
    if request.user.is_authenticated and request.method == "POST":
        if request.data is not None:
            data = request.data["tracks"]
            try:
                playlistId = request.data["playlistId"]
                # check if the playlist exists
                if not models.Playlist.objects.filter(user=request.user, id = playlistId).exists():
                    return JsonResponse({'status': 'error'})
                playListInstance = models.Playlist.objects.get(user=request.user, id = playlistId)
                for track in data:
                    # check if the track already exists
                    if not models.Track.objects.filter(playlist=playListInstance, trackurl = track["trackurl"]).exists():
                        newTrack = models.Track(
                            playlist = playListInstance,
                            trackurl = track["trackurl"],
                            artist = track["artist"],
                            name = track["name"],
                            album = track["album"],
                            duration = track["duration"],
                            image = track["image"],
                            published_date = track["published_date"],
                            artistId = track["artistId"],
                            albumId = track["albumId"]
                        )
                        newTrack.save()
                return JsonResponse({'status': 'success'})
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'error'})
        return JsonResponse({'status': 'error'})
    return redirect('server:index')
    

@login_required
def delete_playlist(request):
    if request.user.is_authenticated and request.method == "POST":
        playlistId = request.POST.get("playlistId")
        models.Playlist.objects.filter(user=request.user, id=playlistId).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def rename_playlist(request):
    if request.user.is_authenticated and request.method == "POST":
        playlistId = request.POST.get("playlistId")
        newPlaylistName = request.POST.get("newPlaylistName")
        models.Playlist.objects.filter(user=request.user, id=playlistId).update(name=newPlaylistName)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})    

@login_required
def remove_track(request):
    if request.user.is_authenticated and request.method == "POST":
        trackUrl = request.POST.get("trackUrl")
        playlistId = request.POST.get("playlistId")
        models.Track.objects.filter(playlist__user=request.user, playlist__id=playlistId, trackurl=trackUrl).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})           

@login_required
def edit_preference(request):
    if request.user.is_authenticated:
        if not models.UserProfileInfo.objects.filter(user__username=request.user.username).exists():
            models.UserProfileInfo.objects.create(user=request.user)
        userMusic = models.UserMusic.objects.get(user=request.user)
        if request.method == "POST" and request.POST.get("singer", "{}") != "{}":
            market = request.POST.get("market")
            genre = request.POST.getlist("genre")
            singer_dict = json.loads(request.POST.get("singer", "{}"))

            userMusic.market = market
            userMusic.set_genre(genre)
            userMusic.singer = singer_dict
            userMusic.save()

        singer_names = list(userMusic.singer.keys())
        return render(request, 'preference.html', {
           'userMusic': userMusic,
            'singer_names': singer_names
        })
    return redirect('server:index')

@login_required
def survey(request):
    if request.method == "POST":
        if not models.UserProfileInfo.objects.filter(user__username=request.user.username).exists():
            models.UserProfileInfo.objects.create(user=request.user)
        market = request.POST.get("market")
        genre = request.POST.getlist("genre")
        singer_dict = json.loads(request.POST.get('singer', '{}'))
        # Update the user's genres, market, artists, and hasSurvey
        
        data = models.UserMusic.objects.create(user=request.user)
        data.market = market
        data.set_genre(genre)
        data.singer = singer_dict
        data.save()
        
        models.UserProfileInfo.objects.filter(user__username=request.user.username).update(hasSurvey=True)
        return redirect('server:index')
    
    return render(request, 'survey.html')
    
def logIn(request):
    if request.user.is_authenticated:
        return redirect('server:index')
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['username'] = username
            username = request.session.get('username', 0)
            return redirect('server:index')
    return render(request, 'login.html')
        
def signup(request):
    if request.method == "POST":
        form_user = forms.UserForm(data=request.POST)       
        form_por = forms.UserProfileInfoForm(data=request.POST) 
        if (form_user.is_valid() and form_user.cleaned_data['password'] == form_user.cleaned_data['confirm']):
            user = form_user.save()   
            user.set_password(user.password)         
            user.save()     
             
            profile = form_por.save(commit=False)
            profile.user = user
            profile.save()
        
            return redirect('server:login')
        
        return render(request, 'register.html', {'form_user': form_user, 'form_por': form_por})
    
    return render(request, 'register.html', {'form_user': forms.UserForm(), 'form_por': forms.UserProfileInfoForm()})
 
def logOut(request):
    logout(request)
    return redirect('server:login')
