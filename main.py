import sys
sys.path.insert(0, './src/')

from StreamingHistory import StreamingHistory
from create_visualisations import build_song_visualisation, build_artist_visualisation, build_genre_visualisation, build_summary_visualisation


def main():
    # Get run options
    run_options = sys.argv[1:]
    
    # Get streaming history object
    sh = StreamingHistory(data_path='./data/ExampleData/StreamingHistory0.json',
                          key_path='./data/api_keys/api_dev_keys.txt')
    
    # If no options, then run main visualisations
    if len(run_options) == 0:
        build_summary_visualisation(sh)
        build_song_visualisation(sh)
        build_artist_visualisation(sh)
        build_genre_visualisation(sh)
    else:
        if '-s' in run_options:
            build_summary_visualisation(sh)
        if '-t' in run_options:
            build_song_visualisation(sh)
        if '-a' in run_options:
            build_artist_visualisation(sh)
        if '-g' in run_options:
            build_genre_visualisation(sh)
        if '-p' in run_options:
            sh.statistics_to_pdf()


if __name__ == "__main__":
    main()