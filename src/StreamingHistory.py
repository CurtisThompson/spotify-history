import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import statistics as s


class StreamingHistory:
    SPOTIPY_CLIENT_ID = None
    SPOTIPY_CLIENT_SECRET = None
    sp = None
    
    data = None
    songs = None
    
    def __init__(self):
        self.SPOTIPY_CLIENT_ID, self.SPOTIPY_CLIENT_SECRET = s.get_dev_keys()
        client_credentials_manager = SpotifyClientCredentials(client_id=self.SPOTIPY_CLIENT_ID, client_secret=self.SPOTIPY_CLIENT_SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        self.data = s.read_data()
        self.songs = s.get_all_songs(self.data)
        self.artists = None
        self.uris = None
        self.artist_search = None
        
        self.is_api_ran = False
        
        self.artist_play_time = None
        self.genre_play_time = None
    
    
    def get_top_songs(self, n=20):
        return s.get_songs_by_listens(self.data).head(n)
    
    
    def get_song_count(self):
        return s.get_total_song_count(self.data)
    
    
    def get_unique_song_count(self):
        return s.get_unique_song_count(self.data)
    
    
    def get_play_time(self):
        return s.get_play_time_string(self.data)
    
    
    def get_top_days(self, n=5):
        return s.get_days_by_play_time(self.data).head(n)
    
    
    def run_api(self):
        if not self.is_api_ran:
            self.artists, self.uris = s.get_songs_artists_frame(self.songs, sp=self.sp)
            self.artist_search = s.get_artists_from_uris(self.uris, sp=self.sp)
            self.is_api_ran = True
    
    
    def get_top_artists(self, n=20):
        # Run API if not already done
        if not self.is_api_ran:
            self.run_api()
        
        # Run artist play time calculations if not already done
        if self.artist_play_time == None:
            self.artist_play_time = s.get_artists_by_play_time(self.songs, self.artist_search, self.artists)
        
        return self.artist_play_time.sort_values('Minutes', ascending=False).head(n)
    
    
    def get_top_genres(self, n=10):
        # Run API if not already done
        if not self.is_api_ran:
            self.run_api()
        
        # Run genre play time calcuations if not already done
        if self.genre_play_time == None:
            self.genre_play_time = s.get_genres_by_play_time(self.songs, self.artist_search, self.artists)
        
        return self.genre_play_time.sort_values('Minutes', ascending=False).head(n)
        