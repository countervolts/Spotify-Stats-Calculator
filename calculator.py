import os
import math
import json
from collections import defaultdict, Counter
from datetime import datetime
from tqdm import tqdm

DebugMode = True

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def print_folder_contents(folder_path):
    os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal
    files = []
    directories = []
    streaming_history_count = 0

    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path):
            files.append((entry, os.path.getsize(full_path)))
            if entry.startswith("StreamingHistory_music_") and entry.endswith(".json"):
                streaming_history_count += 1
        elif os.path.isdir(full_path):
            directories.append(entry)

    files.sort(key=lambda f: f[1])
    directories.sort()

    for i, (file, size) in enumerate(files, start=1):
        print(f"{i}. {file} ({convert_size(size)})")

    for i, directory in enumerate(directories, start=len(files)+1):
        print(f"{i}. {directory} (folder)")

    if streaming_history_count > 0:
        print(f"{streaming_history_count} Streaming Histories were found! Auto-Reading both json files")

    return directories, streaming_history_count, files

def process_streaming_history(files):
    total_ms_played = 0
    first_time_listened = None
    tracks = defaultdict(int)
    artists = defaultdict(int)
    track_first_played = defaultdict(str)
    artist_first_played = defaultdict(str)
    lines_read = []

    for file in tqdm(files, desc="Processing files"):
        with open(file, 'r') as f:
            data = json.load(f)
            lines_read.append((os.path.basename(file), len(data)))  # store the file name and the number of lines
            if DebugMode:
                print(f"Reading file: {os.path.basename(file)}")
            for entry in data:
                ms_played = entry['msPlayed']
                total_ms_played += ms_played
                track_name = entry['trackName']
                artist_name = entry['artistName']
                tracks[track_name] += ms_played
                artists[artist_name] += ms_played
                end_time = datetime.strptime(entry['endTime'], '%Y-%m-%d %H:%M')
                if track_name not in track_first_played:
                    track_first_played[track_name] = end_time
                if artist_name not in artist_first_played:
                    artist_first_played[artist_name] = end_time
                if first_time_listened is None or end_time < first_time_listened:
                    first_time_listened = end_time

    return total_ms_played, first_time_listened, tracks, artists, track_first_played, artist_first_played, lines_read

folder_path = os.path.dirname(os.path.abspath(__file__))
streaming_history_count = 0

while streaming_history_count == 0:
    directories, streaming_history_count, files = print_folder_contents(folder_path)
    if streaming_history_count == 0 and directories:
        dir_index = int(input("Enter the number of the directory to switch to: ")) - len(directories) - 1
        folder_path = os.path.join(folder_path, directories[dir_index])

streaming_history_files = [os.path.join(folder_path, file) for file, _ in files if file.startswith("StreamingHistory_music_") and file.endswith(".json")]
total_ms_played, first_time_listened, tracks, artists, track_first_played, artist_first_played, lines_read = process_streaming_history(streaming_history_files)

for file, lines in lines_read:
    print(f"{file} Lines Read: {lines}")

# convert ms to hours and minutes
total_hours = total_ms_played / 1000 / 60 / 60
total_minutes = total_ms_played / 1000 / 60

# convert defaultdict to Counter for most common method
artists = Counter(artists)
tracks = Counter(tracks)


# get the top 50 artists and tracks
top_50_artists = artists.most_common(50)
top_50_tracks = tracks.most_common(50)

customize = input('\nWould you like to customize Stats.txt? (Auto generation includes the top 50 songs and artists) (y/n): ')
if customize.lower() == 'y':
    max_artists = len(artists)
    max_songs = len(tracks)
    while True:
        num_artists = int(input(f'\nHow many artists would you like to include? (Max: {max_artists}): '))
        if 0 < num_artists <= max_artists:
            top_artists = artists.most_common(num_artists)
            break
        else:
            print("Invalid input. Please enter a number between 1 and " + str(max_artists))
    while True:
        num_songs = int(input(f'\nHow many songs would you like to include? (Max: {max_songs}): '))
        if 0 < num_songs <= max_songs:
            top_tracks = tracks.most_common(num_songs)
            break
        else:
            print("Invalid input. Please enter a number between 1 and " + str(max_songs))
else:
    num_artists = 50
    num_songs = 50
    top_artists = top_50_artists
    top_tracks = top_50_tracks

with open('Stats.txt', 'w') as f:
    f.write(f"Total streams: {len(tracks):,}\n")
    f.write(f"Total minutes streamed: {round(total_minutes, 2):,}\n")
    f.write(f"Total hours streamed: {round(total_hours, 2):,}\n")
    f.write(f"Different tracks: {len(set(tracks.keys())):,}\n")
    f.write(f"Different artists: {len(set(artists.keys())):,}\n\n")
    f.write(f"Top {num_artists} Most Streamed Artists:\n")
    f.write("-" * 30 + "\n")
    for i, (artist, ms_played) in enumerate(top_artists, start=1):
        hours = ms_played / 1000 / 60 / 60
        minutes = ms_played / 1000 / 60
        f.write(f'{i}. "{artist}" - {round(hours, 2)} hours ({round(minutes, 2):,.2f} minutes)\n')
    f.write(f"\nTop {num_songs} Most Streamed Tracks:\n")
    f.write("-" * 30 + "\n")
    for i, (track, ms_played) in enumerate(top_tracks, start=1):
        hours = ms_played / 1000 / 60 / 60
        minutes = ms_played / 1000 / 60
        f.write(f'{i}. "{track}" - {round(hours, 2)} hours ({round(minutes, 2):,.2f} minutes)\n')

print(f"\nStats.txt successfully written to {os.getcwd()}/Stats.txt")
print(f"\nIt contains the following: ")
print(f"{num_artists} artists and {num_songs} songs")