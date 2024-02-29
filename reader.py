import os
import pandas as pd
from tqdm import tqdm
import time
import json

current_dir = os.path.dirname(os.path.realpath(__file__))

os.system('cls' if os.name == 'nt' else 'clear')

while True:
    contents = os.listdir(current_dir)
    print(f'Current directory: {current_dir}')
    
    json_files = [item for item in contents if item.endswith('.json')]
    if json_files:
        json_files.sort(key=lambda x: os.path.getsize(os.path.join(current_dir, x)), reverse=True)
        for i, item in enumerate(json_files, start=1):
            size = os.path.getsize(os.path.join(current_dir, item))
            size_mb = size / (1024 * 1024)
            size_kb = size / 1024
            if size_mb < 1:
                print(f'{i}. {item} - {size_kb:.2f} KB')
            else:
                print(f'{i}. {item} - {size_mb:.2f} MB')
        prompt = '\nJson files found! \nPick a JSON (a json that is called streaming_history_music_*.json): '
    else:
        for i, item in enumerate(contents, start=1):
            print(f'{i}. {item}')
        prompt = 'Enter the number of the item to select: '

    choice = input(prompt)

    try:
        choice = int(choice)
        file_dir = os.path.join(current_dir, json_files[choice-1] if json_files else contents[choice-1])
        
        if os.path.isdir(file_dir):
            current_dir = file_dir
            os.system('cls' if os.name == 'nt' else 'clear')  # clear the command line
            continue
        else:
            break
    except (ValueError, IndexError):
        print('Invalid choice, please try again.')

os.system('cls' if os.name == 'nt' else 'clear')

# Load the JSON file into a DataFrame
with open(file_dir, 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Convert msPlayed to minutes
df['msPlayed'] = df['msPlayed'] / 60000

# Group by artistName and sum the msPlayed for each artist
grouped_artist = df.groupby('artistName')['msPlayed'].sum()
grouped_artist = grouped_artist.apply(lambda x: round(x/60, 1))  # Convert minutes to hours
top_50_artists = grouped_artist.sort_values(ascending=False).head(50)  # Get the top 50 artists

# Group by trackName and sum the msPlayed for each track
grouped_track = df.groupby('trackName')['msPlayed'].sum()
grouped_track = grouped_track.apply(lambda x: round(x/60, 1))  # Convert minutes to hours
top_50_tracks = grouped_track.sort_values(ascending=False).head(50)  # Get the top 50 tracks

# Calculate some statistics
streams = len(df)
minutes_streamed = df['msPlayed'].sum()
hours_streamed = round(minutes_streamed / 60, 1)
different_tracks = df['trackName'].nunique()
different_artists = df['artistName'].nunique()

# Print the statistics
print(f"\nTotal streams: {streams:,}")
print(f"Total minutes streamed: {round(minutes_streamed, 2):,}")
print(f"Total hours streamed: {hours_streamed:,}")
print(f"Different tracks: {different_tracks:,}")
print(f"Different artists: {different_artists:,}")

# Print the top 10 most streamed artists
print("\nTop 10 Most Streamed Artists:")
print("-" * 30)
for i, (artist, time) in enumerate(top_50_artists.items(), start=1):
    if i > 10:
        break
    minutes = time * 60
    print(f'{i}. "{artist}" - {time} hours ({minutes:,.2f} minutes)')

# Print the top 10 most streamed tracks
print("\nTop 10 Most Streamed Tracks:")
print("-" * 30)
for i, (track, time) in enumerate(top_50_tracks.items(), start=1):
    if i > 10:
        break
    minutes = time * 60
    print(f'{i}. "{track}" - {time} hours ({minutes:,.2f} minutes)')

# Ask the user if they want to customize the output
customize = input('\nWould you like to customize Stats.txt? (Auto generation includes the top 50 songs and artists) (y/n): ')
if customize.lower() == 'y':
    max_artists = len(df['artistName'].unique())
    max_songs = len(df['trackName'].unique())
    while True:
        num_artists = int(input(f'\nHow many artists would you like to include? (Max: {max_artists}): '))
        if 0 < num_artists <= max_artists:
            top_artists = grouped_artist.sort_values(ascending=False).head(num_artists)
            break
        else:
            print("Invalid input. Please enter a number between 1 and " + str(max_artists))
    while True:
        num_songs = int(input(f'\nHow many songs would you like to include? (Max: {max_songs}): '))
        if 0 < num_songs <= max_songs:
            top_tracks = grouped_track.sort_values(ascending=False).head(num_songs)
            break
        else:
            print("Invalid input. Please enter a number between 1 and " + str(max_songs))
else:
    num_artists = 50
    num_songs = 50
    top_artists = top_50_artists
    top_tracks = top_50_tracks

with open('Stats.txt', 'w') as f:
    f.write(f"Total streams: {streams:,}\n")
    f.write(f"Total minutes streamed: {round(minutes_streamed, 2):,}\n")
    f.write(f"Total hours streamed: {hours_streamed:,}\n")
    f.write(f"Different tracks: {different_tracks:,}\n")
    f.write(f"Different artists: {different_artists:,}\n\n")
    f.write(f"Top {num_artists} Most Streamed Artists:\n")
    f.write("-" * 30 + "\n")
    for artist, time in list(top_artists.items())[:num_artists]:
        artist_df = df[df['artistName'] == artist]
        if artist_df.empty:
            continue
        minutes = time * 60
        df['endTime'] = pd.to_datetime(df['endTime'])
        first_listened = df['endTime'].min().date()
        first_song = artist_df['trackName'].iloc[0]
        most_streamed_song = artist_df.groupby('trackName')['msPlayed'].sum().idxmax()
        most_streamed_song_time = artist_df.groupby('trackName')['msPlayed'].sum().max()
        most_streamed_song_time_hours = round(most_streamed_song_time / 60, 1)
        f.write(f'"{artist}" listened for {time} hours ({minutes:,.2f} minutes)\n')
        f.write(f'   -> first listened on: {first_listened}\n')
        f.write(f'   -> first song streamed: {first_song}\n')
        f.write(f'   -> total listening time: {time} hours ({minutes:,.2f} minutes)\n')
        f.write(f'   -> most streamed song: {most_streamed_song} - {most_streamed_song_time_hours} hours ({most_streamed_song_time:,.2f} minutes)\n\n')
    f.write(f"\nTop {num_songs} Most Streamed Tracks:\n")
    f.write("-" * 30 + "\n")
    for track, time in list(top_tracks.items())[:num_songs]:
        minutes = time * 60
        first_listened = df[df['trackName'] == track]['endTime'].min().date()
        f.write(f'"{track}"\n')
        f.write(f'   -> listened for {time} hours ({minutes:,.2f} minutes)\n')
        f.write(f'   -> first listened on {first_listened}\n\n')

print(f"\nStats.txt successfully written to {os.getcwd()}/Stats.txt")
print(f"\nIt contains the following: ")
print(f"{num_artists} artists and {num_songs} songs")
