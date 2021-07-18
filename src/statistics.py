import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def read_data(path='../data/ExampleData/StreamingHistory0.json', year=2021):
    """Import JSON streaming data."""
    # Read in the JSON data
    data = pd.read_json(path)
    
    # Filter by year
    if year != None:
        data = data[(data.endTime >= str(year)+'-01-01')
                  & (data.endTime <= str(year)+'-12-31')]
    
    return data


def get_all_songs(data):
    """Get a DataFrame of songs in the data."""
    all_songs = data.groupby(['artistName', 'trackName'])
    return all_songs.msPlayed.sum().reset_index()


def get_dev_keys(path='../data/api_keys/api_dev_keys.txt'): 
    """Gets the Spotify development keys from file."""
    with open(path, 'r') as f:
        keys = f.read().split('\n')
    return keys[0], keys[1]


SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET = get_dev_keys()
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_song_artists_through_api(artist, track, sp=sp):
    """Get all song artist details for a song using the Spotify API."""
    search_query = artist + ' ' + track
    song_details = sp.search(search_query, limit=1)
    song_artists = song_details['tracks']['items'][0]['artists']
    return song_artists


def get_songs_artists_frame(songs_df, sp=sp):
    """Gets all possible artists for all possible songs in a DataFrame."""
    all_songs_with_artists = []

    for index, row in songs_df.iterrows():
        try:
            # Get song artists
            song_artists = get_song_artists_through_api(row.artistName,
                                                        row.trackName,
                                                        sp=sp)
            
            # Store artists for song
            uris = [artist['uri'] for artist in song_artists]
            for uri in uris:
                all_songs_with_artists.append([row.artistName,
                                               row.trackName,
                                               uri])
        except:
            if ' - ' in row.trackName:
                try:
                    # Get song artists
                    new_track_name = ' - '.join(row.trackName.split(' - ')[:-1])
                    song_artists = get_song_artists_through_api(row.artistName,
                                                                new_track_name,
                                                                sp=sp)
                    
                    # Store artists for song
                    uris = [artist['uri'] for artist in song_artists]
                    for uri in uris:
                        all_songs_with_artists.append([row.artistName,
                                                       row.trackName,
                                                       uri])
                except:
                    print(index, row.artistName, row.trackName)
            else:
                print(index, row.artistName, row.trackName)
    
    # Convert results to dataframe
    all_songs_with_artists = pd.DataFrame(all_songs_with_artists,
                                          columns=['artistName',
                                                   'trackName',
                                                   'artistURI'])
    
    # Get a list of URIs
    artist_uris = list(all_songs_with_artists.artistURI.unique())
    
    return all_songs_with_artists, artist_uris


def get_artists_from_uris(artist_uris, sp=sp):
    """Convert a list of artist URIs to data dicts with the Spotify API."""
    artist_search = {}
    for i in range(0, len(artist_uris), 50):
        search_results = sp.artists(artist_uris[i:i + 50])
        for result in search_results['artists']:
            artist_search[result['uri']] = result
    return artist_search


def check_uri_for_song(song_artists, uri, trackName, artistName):
    """Does an artist URI feature in a given song."""
    song_filter = (song_artists.artistName==artistName) & (song_artists.trackName==trackName)
    return uri in song_artists[song_filter].artistURI.unique()


def get_artists_by_play_time(data, artist_search, all_songs_with_artists):
    """Count play time for each artist."""
    # Get play time for each artist
    df_artists = data[['trackName', 'artistName', 'msPlayed']]
    artist_play_times = []
    for uri in list(artist_search.keys()):
        artist_play_time = df_artists[df_artists.apply(lambda x: check_uri_for_song(all_songs_with_artists, uri, x.trackName, x.artistName), axis=1)].msPlayed.sum()
        artist_play_times.append((uri, artist_play_time))

    # Get artist names and time
    top_artists = pd.DataFrame(artist_play_times, columns=['URI', 'Ms'])
    top_artists['Name'] = top_artists.URI.apply(lambda x: artist_search[x]['name'])
    top_artists['Minutes'] = top_artists.Ms / 60000
    return top_artists


def get_genres_by_play_time(data, artist_search, all_songs_with_artists):
    """Count play time for each genre."""
    # Get a list of genres
    genres = []
    for artist in artist_search:
        genres.extend(artist_search[artist]['genres'])
    genres = list(set(genres))
    
    # Set up genre time dict
    genre_times = {}
    for genre in genres:
        genre_times[genre] = 0
    
    # Get genre for each song
    for index, row in data.iterrows():
        # Get main artist
        song_data = all_songs_with_artists[(all_songs_with_artists.trackName==row.trackName) & (all_songs_with_artists.artistName==row.artistName)]
        song_data = song_data.copy().reset_index()
        try:
            main_artist = song_data.iloc[0].artistURI
        except:
            main_artist = None
        
        # Add genres of main artist to counter
        if main_artist != None:
            artist_genres = artist_search[main_artist]['genres']
            for genre in artist_genres:
                genre_times[genre] += row.msPlayed
    
    # Return as DataFrame
    df_genre = pd.DataFrame(list(genre_times.items()), columns=['Genre', 'Ms'])
    df_genre['Minutes'] = df_genre.Ms / 60000
    return df_genre


def get_songs_by_listens(data):
    """Returns a count for each song, ordered by most listens."""
    song_counts = data.groupby(['artistName', 'trackName']).size().to_frame()
    song_counts = song_counts.reset_index().rename({0 : 'count'}, axis=1)
    return song_counts.sort_values(by='count', ascending=False)


def get_total_song_count(data):
    """Returns the total number of songs listened to."""
    return data.shape[0]


def get_unique_song_count(data):
    """Returns the unique number of songs listened to."""
    return len(list(data.groupby(['artistName', 'trackName']).groups.keys()))


def get_play_time_string(data):
    """Returns a string explaining total listening time on Spotify."""
    total_ms = data.msPlayed.sum()

    total_s = total_ms // 1000
    total_ms -= total_s * 1000

    total_m = total_s // 60
    total_s -= total_m * 60

    total_h = total_m // 60
    total_m -= total_h * 60

    total_d = total_h // 24
    total_h -= total_d * 24

    time_string = ''
    if total_d > 0:
        time_string += str(total_d) + ' Days, '
    if total_h > 0:
        time_string += str(total_h) + ' Hours, '
    if total_m > 0:
        time_string += str(total_m) + ' Minutes, '
    if total_s > 0:
        time_string += str(total_s) + ' Seconds, '
    time_string = time_string[:-2]

    return time_string


def get_days_by_play_time(data):
    """Gets the listening time for each day, and returns in a DataFrame."""
    data_days = data.copy()
    data_days['day'] = data_days.endTime.apply(lambda x: x[:10])
    data_days = data_days.groupby('day').msPlayed.sum().to_frame()
    return data_days.reset_index().sort_values('msPlayed', ascending=False)