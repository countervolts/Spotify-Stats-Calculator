import os
import time
import glob
import zipfile
import pandas as pd
from tqdm import tqdm

current_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = os.path.expanduser("~")

os.system('cls' if os.name == 'nt' else 'clear')

def create_progress_bar(max_value):
    return tqdm(total=max_value, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')

print("Disclaimer: The program will scan your Downloads folder.\ntyping I agree will allow the program to scan your downloads.")
agreement = input("Type 'I agree' to continue: ")

if agreement != 'I agree':
    print("why? :(")
    exit(1)

os.system('cls' if os.name == 'nt' else 'clear')

scan_dirs = [os.path.join(home_dir, dir_name) for dir_name in ['Downloads']]
total_files = {dir_name: sum(len(files) for files in os.walk(dir_name)) for dir_name in scan_dirs}
print("\n================== File Count ==================\n")
for dir_name in scan_dirs:
    print(f"Directory: {os.path.basename(dir_name)}")
    print(f"Total Files: {total_files[dir_name]}")
    print("----------------------------------------------")

should_break = False
for dir_name in scan_dirs:
    if should_break:
        break

is_found = False
file_count = 0
progress_bar = create_progress_bar(total_files[dir_name])

for root, dirs, files in os.walk(dir_name):
    if should_break:
        break
    for file in files:
        if file == "my_spotify_data.zip":
            with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                print(f"\nExtracting {file} in {root}...\n")
                zip_ref.extractall(root)
                is_found = True
                print(f"\nSuccess! 'my_spotify_data.zip' was found and extracted to {root}.")
                print("\nPress enter to to see your stats...")
                input()
                should_break = True
                break
        file_count += 1
        progress_bar.update()
if progress_bar is not None:
    progress_bar.close()
    if is_found:
        print(f"{os.path.basename(dir_name)}: ✓")
    else:
        print(f"{os.path.basename(dir_name)}: ✗")
    print(f"\rCurrently scanning: {os.path.basename(dir_name)} {total_files[dir_name]}/{total_files[dir_name]} Files scanned", end="")
    json_files = []
    for dir_name in scan_dirs:
        json_files.extend(glob.glob(os.path.join(dir_name, '**', 'StreamingHistory_music_*.json'), recursive=True))
    json_files = [os.path.relpath(file, current_dir) for file in json_files]  # Get the relative paths, not the full paths
selected_files = json_files

os.system('cls' if os.name == 'nt' else 'clear')

data = []
missing_msPlayed_files = []  # List to keep track of files missing 'msPlayed'

downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')

for file in selected_files:
    file_name = os.path.basename(file)  # Get the base name of the file
    file_dir = os.path.join(downloads_dir, 'Spotify Account Data', file_name)  # Join downloads_dir with 'Spotify Account Data' and the base name of the file
    df = pd.read_json(file_dir)  # Read the JSON file into a dataframe
    data.append(df)  # Append the dataframe to the data list

# Concatenate all the dataframes
df = pd.concat(data, ignore_index=True)

# Check if 'msPlayed' is in df columns before performing the operation
if 'msPlayed' in df.columns:
    # Convert msPlayed to minutes
    df['msPlayed'] = df['msPlayed'] / 60000
else:
    print(f"msPlayed column not found in the following JSON files: {', '.join(missing_msPlayed_files)}")

# Group by artistName and sum the msPlayed for each artist
grouped_artist = df.groupby('artistName')['msPlayed'].sum()
grouped_artist = grouped_artist.apply(lambda x: round(x/60, 1))  # Convert minutes to hours
top_50_artists = grouped_artist.sort_values(ascending=False).head(50)  # Get the top 50 artists

# Group by artistName and trackName and sum the msPlayed for each group
grouped_track = df.groupby(['artistName', 'trackName'])['msPlayed'].sum()
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


print("\nTop 10 Most Streamed Tracks:")
print("-" * 30)
for i, ((artist, track), time) in enumerate(top_50_tracks.items(), start=1):
    if i > 10:
        break
    minutes = time * 60
    print(f'{i}. "{artist} - {track}" - {time} hours ({minutes:,.2f} minutes)')

# Create a new directory in the user's downloads folder
downloads_dir = os.path.expanduser('~/Downloads')
spotify_stats_dir = os.path.join(downloads_dir, 'SpotifyStats')
os.makedirs(spotify_stats_dir, exist_ok=True)

# Create a new directory for the artist files
artists_dir = os.path.join(spotify_stats_dir, 'Artists')
os.makedirs(artists_dir, exist_ok=True)

max_artists = len(df['artistName'].unique())
max_songs = len(df['trackName'].unique())

num_artists = int(input(f"\nHow many top artists do you want to create a file for? (Max: {max_artists}): "))

top_artists = grouped_artist.sort_values(ascending=False).head(num_artists)

for artist in top_artists.index:
    # Get the data for this artist
    artist_df = df[df['artistName'] == artist]

    # Get the top 10 most played songs by this artist
    top_songs = artist_df.groupby('trackName')['msPlayed'].sum().sort_values(ascending=False).head(10)

    # Calculate some statistics about the artist
    total_time = artist_df['msPlayed'].sum()
    first_listened = artist_df['endTime'].min()
    different_tracks = artist_df['trackName'].nunique()

    # Create a new file named after the artist in the Artists directory
    with open(os.path.join(artists_dir, f"{artist}.txt"), 'w', encoding='utf-8') as f:
        # Write the statistics about the artist to the file with formatting
        f.write(f"Total streaming time: {total_time:,.2f} minutes\n")
        f.write(f"First time streamed: {first_listened}\n")
        f.write(f"Different tracks: {different_tracks:,}\n\n")

        # Write the top 10 most played songs by the artist to the file
        f.write("Top 10 Most Streamed Tracks:\n")
        for song, time in top_songs.items():
            f.write(f"{song} - {time:,.2f} minutes\n")

customize = input('\nWould you like to customize Stats.txt? (Auto generation includes the top 50 songs and artists) (y/n): ')
if customize.lower() == 'y':
    max_artists = len(df['artistName'].unique())
    max_songs = len(df['trackName'].unique())
    while True:
        num_artists = int(input(f'\nHow many artists would you like to include? (Max: {max_artists}): '))
        if 0 < num_artists <= max_artists:
            top_artists = grouped_artist.sort_values(ascending=False).head(num_artists)
            break
        print("Invalid input. Please enter a number between 1 and " + str(max_artists))
    while True:
        num_songs = int(input(f'\nHow many songs would you like to include? (Max: {max_songs}): '))
        if 0 < num_songs <= max_songs:
            top_tracks = grouped_track.sort_values(ascending=False).head(num_songs)
            break
        print("Invalid input. Please enter a number between 1 and " + str(max_songs))
else:
    num_artists = 50
    num_songs = 50
    top_artists = top_50_artists
    top_tracks = top_50_tracks

with open(os.path.join(spotify_stats_dir, 'Stats.txt'), 'w', encoding='utf-8') as f:
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
    for (artist, track), time in list(top_tracks.items())[:num_songs]:
        minutes = time * 60
        track_df = df.loc[df['trackName'] == track].copy()  # use .copy() to avoid SettingWithCopyWarning from pandas
        if track_df.empty:
            continue
        track_df.loc[:, 'endTime'] = pd.to_datetime(track_df['endTime'])  # use .loc to modify the DataFrame in place
        first_listened = track_df['endTime'].min().date()
        f.write(f'"{artist} - {track}"\n')
        f.write(f'   -> listened for {time} hours ({minutes:,.2f} minutes)\n')
        f.write(f'   -> first listened on {first_listened}\n\n')

print(f"\SpotifyStats successfully written to {os.path.expanduser('~/Downloads/SpotifyStats')}")

for dirpath, dirnames, filenames in os.walk(os.path.expanduser('~/Downloads/SpotifyStats')):
    print(f'\n{dirpath}')
    for filename in filenames:
        print(f'├── {filename}')

input("\nPress Enter to view you stats :)")

os.system("start " + os.path.expanduser('~/Downloads/SpotifyStats'))
