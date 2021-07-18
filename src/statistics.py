import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth1 import SpotifyClientCredentials


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


def get_dev_keys(): 
    """Gets the Spotify development keys from file."""
    with open('../data/api_keys/api_dev_keys.txt', 'r') as f:
        keys = f.read().split('\n')
    return keys[0], keys[1]


SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET = get_dev_keys()
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



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

    print(time_string)


def get_days_by_play_time(data):
    """Gets the listening time for each day, and returns in a DataFrame."""
    data_days = data.copy()
    data_days['day'] = data_days.endTime.apply(lambda x: x[:10])
    data_days = data_days.groupby('day').msPlayed.sum().to_frame()
    return data_days.reset_index().sort_values('msPlayed', ascending=False)