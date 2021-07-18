from StreamingHistory import StreamingHistory

# Create an instance of the streaming history class
sh = StreamingHistory()

# Output your total streaming time by calling the function
print(sh.get_play_time())

# This method uses the API and will take longer when first run
print(sh.get_top_genres(n=8))