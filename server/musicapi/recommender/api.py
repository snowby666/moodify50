import requests
import logging
import base64
import six


class _ClientCredentialsFlow(object):
    OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id=None, client_secret=None):

        if not client_id or not client_secret:
            raise Exception('A client ID and client secret is required.')

        self.client_id = client_id
        self.client_secret = client_secret

        self.token_info = None

    def _make_authorization_header(self):
        auth_header = base64.b64encode(six.text_type(self.client_id + ':' + self.client_secret).encode('ascii'))
        return {'Authorization': 'Basic %s' % auth_header.decode('ascii')}

    def get_access_token(self):
        payload = {'grant_type': 'client_credentials'}
        headers = self._make_authorization_header()
        response = requests.post(self.OAUTH_TOKEN_URL, data=payload, headers=headers, verify=True)
        if response.status_code != 200:
            raise Exception(response.reason)
        token_info = response.json()
        return token_info['access_token']

class Recommender(object):
    def __init__(self, client_id=None, client_secret=None):
        auth = _ClientCredentialsFlow(client_id, client_secret)
        self.token = auth.get_access_token()

        self.url = 'https://api.spotify.com/v1/'

        self.headers = {
            'Authorization': 'Bearer ' + self.token
        }

        self._available_genre_seeds = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("music-recommender")
    
    def get_lyrics(self, track_id: str):
        lyrics_url = f"https://lyrix.vercel.app/getLyrics/{track_id}"
        response = requests.get(lyrics_url)
        if response.status_code != 200:
            return {}
        json = response.json()
        return json

    def available_genre_seeds(self):
        if self._available_genre_seeds is None:
            self._available_genre_seeds = self._make_request('recommendations/available-genre-seeds', params=None)
        return self._available_genre_seeds

    def _is_genre_seed_available(self, genre):
        if self._available_genre_seeds is None:
            self._available_genre_seeds = self.available_genre_seeds()
        return genre in self._available_genre_seeds['genres']

    def find_recommendations(self, artist_ids=None, genres=None, tracks=None, limit=100, track_attributes=None):
        params = {
            'seed_artists': artist_ids,
            'seed_genres': genres,
            'seed_tracks': tracks,
            'limit': limit
        }
        params.update(track_attributes)
        recs = self._make_request(endpoint='recommendations', params=params)
        return recs
    
    def search_items(self, query, search_type: str=None, market: str=None, limit=50):
        if not search_type:
            search_type = 'album,artist,playlist,track'
        params = {
            'q': query,
            'type': search_type,
            'limit': limit,  
            'market': market 
        }
        return self._make_request(endpoint='search', params=params)
    
    def get_track_info(self, track_id):
        return self._make_request(endpoint='tracks/' + track_id, params=None)
    
    def get_album_items(self, album_id):
        return self._make_request(endpoint='albums/' + album_id, params=None)
    
    def get_artist_info(self, artist_id):
        return self._make_request(endpoint='artists/' + artist_id, params=None)
    
    def get_artist_albums(self, artist_id):
        params = {
            'include_groups': 'album,single,compilation,appears_on',
            'limit': 50
        }
        return self._make_request(endpoint='artists/' + artist_id + '/albums', params=params)
    
    def get_artist_top_tracks(self, artist_id, market: str=None):
        params = {
            'market': market
        }
        return self._make_request(endpoint='artists/' + artist_id + '/top-tracks', params=params)

    def get_artist_related_artists(self, artist_id):
        return self._make_request(endpoint='artists/' + artist_id + '/related-artists', params=None)
    
    def _lookup(self, term, lookup_type):
        params = {
            'q': term,
            'type': lookup_type
        }
        return self._make_request(endpoint='search', params=params)

    def _lookup_track_id(self, track):
        tracks = self._lookup(term=track, lookup_type='track')

        if len(tracks['tracks']['items']):
            return tracks['tracks']['items'][0]['id']

        self.logger.warning("No results found for: %s" % track)

    def _lookup_artist_id(self, artist_name):
        artists = self._lookup(term=artist_name, lookup_type='artist')

        if len(artists['artists']['items']):
            return artists['artists']['items'][0]['id']

        self.logger.warning("No results found for: %s" % artist_name)

    def _make_request(self, endpoint, params):
        response = requests.get(self.url + endpoint, params=params, headers=self.headers)
        if response.status_code != 200:
            self.logger.error(response.content)
            return {
                'error': response.content
            }
        json = response.json()
        return json
