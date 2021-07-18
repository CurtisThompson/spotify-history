from PIL import Image
import matplotlib.pyplot as plt
import requests

from StreamingHistory import StreamingHistory

# Create an instance of the streaming history class
sh = StreamingHistory()

def create_listicle_plot(data, title, file_name):
    colour_main = 'purple'
    colour_second = 'black'
    colour_background = 'orange'
    
    # data = [('Text', 'Image URL', Count)]
    data = data[:5]
    data.sort(key=lambda x: x[2])

    # Create plots
    f, (a0, a1, a2) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [2, 10, 1]}, figsize=(8, 11))

    # Display bars
    a1.axis('off')
    for i, x in enumerate(data):
        im = Image.open(requests.get(x[1], stream=True).raw)
        inset = f.add_axes([.3, .2+(.11*i), .11, .11], label=('img' + str(i)))
        inset.imshow(im)
        inset.axis('off')
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


def get_song_image(artistName, trackName):
    song_res = sh.sp.search(artistName + ' ' + trackName, limit=1)
    return song_res['tracks']['items'][0]['album']['images'][0]['url']


def get_artist_image(artistURI):
    art_res = sh.sp.artist(artistURI)
    return art_res['images'][0]['url']

# Top songs
songs = sh.get_top_songs(n=5)
songs_list = []
for index, row in songs.iterrows():
    song_img = get_song_image(row.artistName, row.trackName)
    songs_list.append((row.trackName, song_img, row['count']))
create_listicle_plot(songs_list, 'Top Songs', 'top-songs.png')

# Top genres
"""
artists = sh.get_top_artists(n=5)
print(artists)
artists_list = []
for index, row in artists.iterrows():
    song_img = get_artist_image(row.URI)
    artists_list.append((row.Name, song_img, row.Minutes))
create_listicle_plot(artists_list, 'Top Artists', 'top-artists.png')
"""