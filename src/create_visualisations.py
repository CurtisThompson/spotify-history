from PIL import Image
import matplotlib.pyplot as plt
import requests

from StreamingHistory import StreamingHistory
from colour_schemes import colour_schemes

# Create an instance of the streaming history class
sh = StreamingHistory()


def create_listicle_plot(data, title, file_name, colour_scheme=colour_schemes[0]):
    colour_main = colour_scheme['main']
    colour_second = colour_scheme['second']
    colour_background = colour_scheme['background']
    
    # data = [('Text', 'Image URL', Count)]
    data = data[:5]
    data.sort(key=lambda x: x[2])

    # Create plots
    f, (a0, a1, a2) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [2, 10, 1]}, figsize=(8, 11))

    # Display bars
    a1.axis('off')
    for i, x in enumerate(data):
        # Display image
        if type(x[1]) is list:
            # Image 1
            im = Image.open(requests.get(x[1][1], stream=True).raw)
            inset1 = f.add_axes([.3, .23+(.11*i), .08, .08], label=('img' + str(i)))
            inset1.imshow(im)
            inset1.axis('off')
            
            # Image 2
            im = Image.open(requests.get(x[1][0], stream=True).raw)
            inset2 = f.add_axes([.33, .2+(.11*i), .08, .08], label=('img' + str(i)))
            inset2.imshow(im)
            inset2.axis('off')
        else:
            # Only 1 image anyway
            im = Image.open(requests.get(x[1], stream=True).raw)
            inset = f.add_axes([.3, .2+(.11*i), .11, .11], label=('img' + str(i)))
            inset.imshow(im)
            inset.axis('off')
        
        # Display side text
        f.text(.23, .25+(.11*i), '#'+str(5-i), color=colour_main, fontweight='bold', fontsize=16, ha='center', va='center')
        main_text = x[0][:40] + '...' if len(x[0]) > 42 else x[0]
        f.text(.45, .25+(.11*i), main_text, color=colour_second, fontsize=12)

    # Display title
    a0.text(0.1, 0.3, title, color=colour_main, fontweight='bold', fontsize=36, ha='left', va='center')
    a0.axis('off')

    # Display songs
    a2.axis('off')

    a2.text(0.1, 0.5, 'Image created with https://github.com/CurtisThompson/spotify-history', color=colour_second, fontsize=10, ha='left', va='center')

    f.set_facecolor(colour_background)

    plt.savefig(file_name, bbox_inches='tight', pad_inches=0.05)


def create_summary_plot(artists, songs, minutes, genre, image_url, file_name, colour_scheme=colour_schemes[5]):
    artists = artists[::-1]
    songs = songs[::-1]
    genre = genre.title()
    
    colour_main = colour_scheme['main']
    colour_second = colour_scheme['second']
    colour_background = colour_scheme['background']

    # Create plots
    f, (a0, a1, a2) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [2, 10, 1]}, figsize=(8, 11))

    # Remove axes
    a0.axis('off')
    a1.axis('off')
    a2.axis('off')

    # Display image
    im = Image.open(requests.get(image_url, stream=True).raw)
    inset = f.add_axes([.2, .6, .6, .25])
    inset.imshow(im)
    inset.axis('off')

    # Display artists
    f.text(.2, .55, 'Top Artists', color=colour_main, fontweight='bold', fontsize=16)
    for i, x in enumerate(artists):
        main_text = x[:23] + '...' if len(x) > 25 else x
        f.text(.23, .35+(.04*i), '#'+str(5-i), color=colour_main, fontweight='bold', fontsize=14, ha='center', va='center')
        f.text(.26, .35+(.04*i), main_text, color=colour_second, fontsize=12, va='center')

    # Display songs
    f.text(.55, .55, 'Top Songs', color=colour_main, fontweight='bold', fontsize=16)
    for i, x in enumerate(songs):
        main_text = x[:23] + '...' if len(x) > 25 else x
        f.text(.58, .35+(.04*i), '#'+str(5-i), color=colour_main, fontweight='bold', fontsize=14, ha='center', va='center')
        f.text(.61, .35+(.04*i), main_text, color=colour_second, fontsize=12, va='center')

    # Display time
    f.text(.55, .27, 'Minutes Played', color=colour_main, fontweight='bold', fontsize=16)
    f.text(.56, .225, str(minutes), color=colour_second, fontweight='bold', fontsize=14)

    # Display genre
    f.text(.2, .27, 'Top Genre', color=colour_main, fontweight='bold', fontsize=16)
    f.text(.21, .225, genre, color=colour_second, fontweight='bold', fontsize=14)

    # Display bottom
    a2.text(0.1, 0.5, 'Image created with https://github.com/CurtisThompson/spotify-history', color=colour_second, fontsize=10, ha='left', va='center')
    
    # Set background colour
    f.set_facecolor(colour_background)
    
    # Save image
    plt.savefig(file_name, bbox_inches='tight', pad_inches=0.05)


def get_song_image(artistName, trackName):
    song_res = sh.sp.search(artistName + ' ' + trackName, limit=1)
    return song_res['tracks']['items'][0]['album']['images'][0]['url']


def get_artist_image(artistURI):
    art_res = sh.sp.artist(artistURI)
    return art_res['images'][0]['url']


def get_genre_image(genre):
    gen_uris = sh.get_top_artists_in_genre(genre, n=2)
    gen_res = []
    for index, row in gen_uris.iterrows():
        gen_res.append(get_artist_image(row.URI))
    return gen_res


def build_summary_visualisation(colour_scheme=colour_schemes[5]):
    # Get top artists
    artists = sh.get_top_artists(n=5)
    top_artist_uri = artists.iloc[0].URI
    artists = list(artists.Name)
    image_url = get_artist_image(top_artist_uri)
    
    # Get top songs
    songs = sh.get_top_songs(n=5)
    songs = list(songs.trackName)
    
    # Get top genre
    genre = sh.get_top_genres(n=1).iloc[0].Genre
    
    # Get minutes
    minutes = sh.get_minutes_played()
    
    # Build visualisation
    create_summary_plot(artists, songs, minutes, genre, image_url, 'summary.png', colour_scheme=colour_scheme)


def build_song_visualisation(colour_scheme=colour_schemes[0]):
    # Get top songs
    songs = sh.get_top_songs(n=5)
    
    # Format list correctly
    songs_list = []
    for index, row in songs.iterrows():
        song_img = get_song_image(row.artistName, row.trackName)
        songs_list.append((row.trackName, song_img, row['count']))
    
    # Build visualisation
    create_listicle_plot(songs_list, 'Top Songs', 'top-songs.png', colour_scheme=colour_scheme)


def build_artist_visualisation(colour_scheme=colour_schemes[1]):
    # Get top artists
    artists = sh.get_top_artists(n=5)
    
    # Format list correctly
    artists_list = []
    for index, row in artists.iterrows():
        song_img = get_artist_image(row.URI)
        artists_list.append((row.Name, song_img, row.Minutes))
    
    # Build visualisation
    create_listicle_plot(artists_list, 'Top Artists', 'top-artists.png', colour_scheme=colour_scheme)


def build_genre_visualisation(colour_scheme=colour_schemes[2]):
    # Get top genres
    genres = sh.get_top_genres(n=5)
    
    # Format list correctly
    genres_list = []
    for index, row in genres.iterrows():
        genre_img = get_genre_image(row.Genre)
        genres_list.append((row.Genre, genre_img, row.Minutes))
    
    # Build visualisation
    create_listicle_plot(genres_list, 'Top Genres', 'top-genres.png', colour_scheme=colour_scheme)


build_song_visualisation()
build_artist_visualisation()
build_genre_visualisation()
build_summary_visualisation()