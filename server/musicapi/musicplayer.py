from server.musicapi.recommender.api import *

UK = ['GB', 'VG']
US = ['US', 'UM']
EU = ['PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'AN']

class MusicPlayer:
    def __init__(self, api_key):
        self.client = Recommender(
        client_id=api_key['client_id'],
        client_secret=api_key['client_secret']
        )
        
    def get_lyrics(self, track_id):
        try:
            lyrics = self.client.get_lyrics(track_id)
            return lyrics
        except Exception as e:
            print(e)
            return {}
    
    def search_items(self, query, search_type, market):
        try:
            search_results = self.client.search_items(query=query, search_type=search_type, market=market)
            return search_results
        except Exception as e:
            print(e)
            return {}
        
    def get_track_items(self, track_id):
        try:
            track_items = self.client.get_track_info(track_id)
            return track_items
        except Exception as e:
            print(e)
            return {}
        
    def get_album_items(self, album_id):
        try:
            album_items = self.client.get_album_items(album_id)
            return album_items
        except Exception as e:
            print(e)
            return {}
        
    def get_artist_items(self, artist_id):
        try:
            artist_items = {
                'artistInfo': self.client.get_artist_info(artist_id),
                'artistTopTracks': self.client.get_artist_top_tracks(artist_id),
                'artistAlbums': self.client.get_artist_albums(artist_id),
                'artistRelatedArtists': self.client.get_artist_related_artists(artist_id)
            }
            return artist_items
        except Exception as e:
            print(e)
            return {}    
        
    def get_recommendations(self, artistsIds, emotion, genres,  market, pop, searchType):
        try:
            recommendmusic = []
            seed_artists = ','.join(artistsIds)
            
            if emotion == "sad":
                attribute = {
                    'target_acousticness':1,
                    'target_danceability':0,
                    'target_energy':0.3,
                    'target_instrumentalness':0.5,
                    'target_loudness': -15,
                    'target_popularity': pop,
                    'target_speechiness':0,
                    'target_valence':0
                    }
            elif emotion == "energetic":
                attribute = {
                    'target_acousticness':0,
                    'target_danceability':0.3,
                    'target_energy':1,
                    'target_instrumentalness':0,
                    'target_loudness': -60,
                    'target_popularity': pop,
                    'target_speechiness':0.75,
                    'target_valence':0.75
                    }
            elif emotion == "happy":
                attribute = {
                    'target_acousticness':0.3,
                    'target_danceability':0.75,
                    'target_energy':0.3,
                    'target_instrumentalness':0,
                    'target_loudness': -45,
                    'target_popularity': pop,
                    'target_speechiness':0.5,
                    'target_valence':1
                    }
            elif emotion == "depressed":
                attribute = {
                    'target_acousticness':0.5,
                    'target_danceability':1,
                    'target_energy':0,
                    'target_instrumentalness':1,
                    'target_loudness': 0,
                    'target_popularity': pop,
                    'target_speechiness':1,
                    'target_valence':0.3
                    }
            
            recommendations = self.client.find_recommendations(artist_ids=seed_artists, genres=genres, limit=100, track_attributes=attribute)

            for recommendation in recommendations['tracks']:
                if searchType == 0:        
                    #Attempt 1: Fetching from the same artist
                    if recommendation['artists'][0]['id'] in artistsIds:
                        artistname = recommendation['artists'][0]['name']
                    
                        if recommendation['id'] in [i['trackurl'] for i in recommendmusic]:
                            continue
                        recommendmusic.append({'trackurl': recommendation['id'], 
                                            'duration': recommendation['duration_ms'], 
                                            'artist': artistname, 
                                            'name': recommendation['name'], 
                                            'album': recommendation['album']['name'], 
                                            'image': recommendation['album']['images'][0]['url'], 
                                            'published_date': recommendation['album']['release_date'],
                                            'artistId': recommendation['artists'][0]['id'],
                                            'albumId': recommendation['album']['id'],
                                            })
                elif searchType == 1:
                    # Attempt 2: Fetching from other artists in the same region
                    if recommendation['id'] in [i['trackurl'] for i in recommendmusic]:
                        continue
                    i = recommendation['external_ids']['isrc'][:2]
                    i = i.upper()
                    if i == market or (market == 'UK' and i in UK) or (market == 'EU' and i in EU) or (market == 'US' and i in US):
                        recommendmusic.append({
                                'trackurl': recommendation['id'], 
                                'duration': recommendation['duration_ms'], 
                                'artist': artistname, 
                                'name': recommendation['name'], 
                                'album': recommendation['album']['name'], 
                                'image': recommendation['album']['images'][0]['url'], 
                                'published_date': recommendation['album']['release_date'],
                                'artistId': recommendation['artists'][0]['id'],
                                'albumId': recommendation['album']['id'],
                            })
                else:
                    # Attempt 3: Fetching from related artists no matter the region
                    if recommendation['id'] in [i['trackurl'] for i in recommendmusic]:
                        continue
                    recommendmusic.append({
                        'trackurl': recommendation['id'], 
                        'duration': recommendation['duration_ms'], 
                        'artist': artistname, 
                        'name': recommendation['name'], 
                        'album': recommendation['album']['name'], 
                        'image': recommendation['album']['images'][0]['url'], 
                        'published_date': recommendation['album']['release_date'],
                        'artistId': recommendation['artists'][0]['id'],
                        'albumId': recommendation['album']['id'],
                        })
            return recommendmusic
        except Exception as e:
            print(e)
            return []
        