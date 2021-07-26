import sys
sys.path.insert(0, './src/')

from StreamingHistory import StreamingHistory
from create_visualisations import build_song_visualisation, build_artist_visualisation, build_genre_visualisation, build_summary_visualisation


def main():
    """Run the visualisation builder.
    
    Options:
    -s          summary visualisation
    -t          track visualisation
    -a          artist visualisation
    -g          genre visualisation
    -p          pdf of statistics
    -y [year]   year of statistics
    -k [path]   path to key file
    -d [path]   path to directory with streaming history
    """
    # Get run options
    run_options = sys.argv[1:]
    
    # Default key path
    key_path = './data/api_keys/api_dev_keys.txt'
    # Get user input key path if given
    if '-k' in run_options:
        key_index = run_options.index('-k') + 1
        if len(run_options) > key_index:
            key_path = run_options[key_index]
    
    # Default streaming history path
    data_path = './data/ExampleData/'
    # Get user input data path if given
    if '-d' in run_options:
        data_index = run_options.index('-d') + 1
        if len(run_options) > data_index:
            data_path = run_options[data_index]
    
    # Default year
    year = 2021
    # Get user input year if given
    if '-y' in run_options:
        year_index = run_options.index('-y') + 1
        if len(run_options) > year_index:
            year = run_options[year_index]
    
    # Get streaming history object
    sh = StreamingHistory(data_path=data_path,
                          key_path=key_path,
                          year=year)
    
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