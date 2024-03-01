import os
import time
import json
import glob
import zipfile
import sys
import pandas as pd
from tqdm import tqdm

current_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = os.path.expanduser("~")

os.system('cls' if os.name == 'nt' else 'clear')

################################################################################################################################################################
# scanning methods

# SemiAutomaticMode: If True, enables semi-automatic selection of the JSON files. 
# This mode requires user interaction to select the directory but automates the file scanning process 
# Press enter when the folder containing your streaming history is found. (due to some weird bug i gotta fix)
SemiAutomaticMode = False # change to True if you would like, makes the process of locating the files a slightly bit easier

# ManualMode: If True, enables manual selection of the JSON files. This will disable DebugMode.
# If False, the program will automatically scan for the JSON files.
ManualMode = True

# DebugMode: If True, enables debug mode, which prints out the files found and the directory it is looking in.
# Requirements: ManualMode to be False.
DebugMode = False

# FullyAutomatic: If True, the program will automatically scan for my_spotify_data.zip in the following directories, Desktop, Downloads, Documents.
# This mode does all the work for you.
FullyAutomatic = False # currently still being tested due to it not correctly reading the directories, resort to using manual mode/semiautomaticmode

# AutomaticDebugMode: If True, enables debug features for the auto scan method.
# Requirements: FullyAutomatic = True.
AutomaticDebugMode = False
################################################################################################################################################################

def AutomaticDebugModePrint(file_name):
    if AutomaticDebugMode:
        print(f"Successfully read {file_name}", end='\r', file=sys.stderr)
        sys.stderr.flush()

def create_progress_bar(max_value):
    return tqdm(total=max_value, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')

if SemiAutomaticMode:
    json_files = glob.glob(os.path.join(current_dir, 'StreamingHistory_music_*.json'))  
    
    if json_files:
        for file in json_files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
    else:
        contents = [item for item in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, item))]
        for i, item in enumerate(contents, start=1):
            print(f'{i}. {item}')
        
        prompt = 'Enter the number of the directory to select (if the directory contains the streaming history press enter): '
        choice = input(prompt)
        try:
            choice = int(choice) 
            selected_dir = contents[choice-1] 
            current_dir = os.path.join(current_dir, selected_dir)  
            json_files = glob.glob(os.path.join(current_dir, 'StreamingHistory_music_*.json'))  
            if json_files:
                for file in json_files:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
        except (ValueError, IndexError):
            print('Invalid choice, please try again.')
    
    if not json_files:
        print("No 'StreamingHistory_music_*.json' files found in the selected directory.")

if FullyAutomatic and DebugMode:
    print("ERROR: DebugMode is set to True, in order to use full auto scan you need to set it to False! You can do this at line: 29, DebugMode = False")
    exit(1)

if FullyAutomatic:
    print("Fully Automated mode set True (you can change this via the code lines 16-37)\n\nDisclaimer: The program will scan your Desktop, Downloads, Documents, and the directory where this code is saved.\n\nby typing 'I agree' you agree that this program is allowed to view your local files and other stuff (no info is sent or saved to any servers or anyone.)")
    agreement = input("Type 'I agree' to continue: ")
    
    if agreement != 'I agree':
        print("why? :(")
        exit(1)
    
scan_dirs = [os.path.join(home_dir, dir_name) for dir_name in ['Desktop', 'Downloads', 'Documents']]
scan_dirs.append(current_dir)
total_files = {dir_name: sum(len(files) for r, d, files in os.walk(dir_name)) for dir_name in scan_dirs}

print("Scanning next:", ', '.join(f"{os.path.basename(dir_name)} (Files: {total_files[dir_name]}/{total_files[dir_name]})" for dir_name in scan_dirs))

print("\nFile Count")
for dir_name in scan_dirs:
    print(f"{os.path.basename(dir_name)}: {total_files[dir_name]}/{total_files[dir_name]}")

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
                print(f"\rExtracting {file} in {root}")
                zip_ref.extractall(root)
                is_found = True
                print(f"\nmy_spotify_data.zip was found and extracted successfully to {root}. \nPress enter to continue")
                input()
                should_break = True
                break
        file_count += 1
        progress_bar.update()
    AutomaticDebugModePrint(file)

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

if ManualMode:
    contents = os.listdir(current_dir)
    for i, item in enumerate(contents, start=1):
        print(f'{i}. {item}')
    prompt = 'Enter the number of the directory to select: '
    choice = input(prompt)
    try:
        choice = int(choice)  # Convert the input to an integer
        selected_dir = contents[choice-1]  # Select the chosen directory
        current_dir = os.path.join(current_dir, selected_dir)  # Update current_dir to the selected directory
        json_files = glob.glob(os.path.join(current_dir, 'StreamingHistory_music_*.json'))  # Look for specific JSON files within the selected directory
        json_files = [os.path.basename(file) for file in json_files]  # Get just the file names, not the full paths
    except (ValueError, IndexError):
        print('Invalid choice, please try again.')
elif SemiAutomaticMode:
    contents = os.listdir(current_dir)
    for i, item in enumerate(contents, start=1):
        print(f'{i}. {item}')
    prompt = 'Enter the number of the directory to select: '
    choice = input(prompt)
    try:
        choice = int(choice)  # Convert the input to an integer
        selected_dir = contents[choice-1]  # Select the chosen directory
        current_dir = os.path.join(current_dir, selected_dir)  # Update current_dir to the selected directory
        json_files = glob.glob(os.path.join(current_dir, '**', 'StreamingHistory_music_*.json'), recursive=True)  # Look for specific JSON files within the selected directory and its subdirectories
        json_files = [os.path.relpath(file, current_dir) for file in json_files]  # Get the relative paths, not the full paths
    except (ValueError, IndexError):
        print('Invalid choice, please try again.')
else:
    json_files = glob.glob(os.path.join(current_dir, '**', 'StreamingHistory_music_*.json'), recursive=True)
    if DebugMode:
        print(f"Looking for files in directory: {current_dir}")
        print(f"Found files: {json_files}")
    json_files = [os.path.relpath(file, current_dir) for file in json_files]  # Get the relative paths, not the full paths
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
    if not ManualMode:
        selected_files = json_files  # All files are selected automatically when ManualMode is off
    else:
        prompt = '\nJson files found! \nPick a JSON (a json that is called streaming_history_music_*.json): '
        choice = input(prompt)
        try:
            choices = map(int, choice.split(','))  # Convert the input to a list of integers
            selected_files = [json_files[i-1] for i in choices]  # Select the chosen files
        except (ValueError, IndexError):
            print('Invalid choice, please try again.')

os.system('cls' if os.name == 'nt' else 'clear')

data = []
missing_msPlayed_files = []  # List to keep track of files missing 'msPlayed'
for file in selected_files:
    file_dir = os.path.join(current_dir, file)
    if DebugMode:
        print(f"Reading file: {file_dir}")
    with open(file_dir, 'r', encoding='utf-8') as f:
        file_data = json.load(f)
        if 'msPlayed' not in file_data[0]:  # Check if 'msPlayed' is in the first item of the JSON data
            missing_msPlayed_files.append(file)
        data.append(pd.DataFrame(file_data))

if not data:  # Check if data is empty
    if DebugMode:
        print(f"No data found in the selected files: {selected_files}")
    print("No data found in the selected JSON files.")
    sys.exit(1)  # Stop the program

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

with open('Stats.txt', 'w', encoding='utf-8') as f:
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

print("\nStats.txt successfully written to {}/Stats.txt".format(os.getcwd()))
print("\nIt contains the following: ")
print(f"{num_artists} artists and {num_songs} songs")
