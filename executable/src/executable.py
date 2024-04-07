import os
import time
import glob
import zipfile
import re
import pandas as pd
from tqdm import tqdm
import requests
import base64
import shutil
import subprocess
import urllib.parse
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

current_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = os.path.expanduser("~")

os.system('cls' if os.name == 'nt' else 'clear')

def create_progress_bar(max_value):
    return tqdm(total=max_value, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')

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
        json_files.extend(glob.glob(os.path.join(dir_name, '**', 'Streaming_History_Audio_*.json'), recursive=True))
        json_files = [os.path.relpath(file, current_dir) for file in json_files]
        selected_files = json_files

os.system('cls' if os.name == 'nt' else 'clear')

data = []
missing_ms_played_files = []

downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')

for file in selected_files:
    file_name = os.path.basename(file)
    file_dir = os.path.join(downloads_dir, 'Spotify Extended Streaming History', file_name)
    df = pd.read_json(file_dir)
    data.append(df)
    print(f"Read data from file: {file_name}")

os.system('cls' if os.name == 'nt' else 'clear')

df = pd.concat(data, ignore_index=True)

if 'ms_played' in df.columns:
    df['ms_played'] = df['ms_played'] / 60000
else:
    print(f"ms_played column not found in the following JSON files: {', '.join(missing_ms_played_files)}")

grouped_artist = df.groupby('master_metadata_album_artist_name')['ms_played'].sum()
grouped_artist = grouped_artist.apply(lambda x: round(x/60, 1))
top_50_artists = grouped_artist.sort_values(ascending=False).head(50)

grouped_track = df.groupby(['master_metadata_album_artist_name', 'master_metadata_track_name'])['ms_played'].sum()
grouped_track = grouped_track.apply(lambda x: round(x/60, 1)) 
top_50_tracks = grouped_track.sort_values(ascending=False).head(50)

streams = len(df)
minutes_streamed = df['ms_played'].sum()
hours_streamed = round(minutes_streamed / 60, 1)
different_tracks = df['master_metadata_track_name'].nunique()
different_artists = df['master_metadata_album_artist_name'].nunique()
days_streamed = hours_streamed / 24

print(f"\nTotal streams: {streams:,}")
print(f"Total minutes streamed: {round(minutes_streamed, 2):,}")
print(f"Total hours streamed: {hours_streamed:,}")
print(f"Total days streamed: {round(days_streamed, 2):,}")
print(f"Different tracks: {different_tracks:,}")
print(f"Different artists: {different_artists:,}")

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

downloads_dir = os.path.expanduser('~/Downloads')
spotify_stats_dir = os.path.join(downloads_dir, 'SpotifyStats')
os.makedirs(spotify_stats_dir, exist_ok=True)

artists_dir = os.path.join(spotify_stats_dir, 'Artists')
os.makedirs(artists_dir, exist_ok=True)

max_artists = len(df['master_metadata_album_artist_name'].unique())
max_songs = len(df['master_metadata_track_name'].unique())

num_top_artists = int(input(f"\nHow many top artists do you want to create a file for? (Max: {max_artists}): "))

top_artists = grouped_artist.sort_values(ascending=False).head(num_top_artists)

for artist in top_artists.index:
    artist_data = df[df['master_metadata_album_artist_name'] == artist]
    top_songs = artist_data.groupby('master_metadata_track_name')['ms_played'].sum().sort_values(ascending=False).head(10)
    total_streaming_time = artist_data['ms_played'].sum()
    first_time_streamed = artist_data['ts'].min()
    different_tracks = artist_data['master_metadata_track_name'].nunique()
    with open(os.path.join(artists_dir, f"{artist}.txt"), 'w', encoding='utf-8') as f:
        f.write(f"Total streaming time: {total_streaming_time:,.2f} minutes\n")
        f.write(f"First time streamed: {first_time_streamed}\n")
        f.write(f"Different tracks: {different_tracks:,}\n\n")
        f.write("Top 10 Most Played Songs:\n")
        for song, time in top_songs.items():
            f.write(f"{song} - {time:,.2f} minutes\n")

customize = input('\nWould you like to customize Stats.txt? (Auto generation includes the top 50 songs and artists) (y/n): ')
if customize.lower() == 'y':
    max_artists = len(df['master_metadata_album_artist_name'].unique())
    max_songs = len(df['master_metadata_track_name'].unique())
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

total_unique_tracks = df['master_metadata_track_name'].nunique()

with open(os.path.join(spotify_stats_dir, 'Stats.txt'), 'w', encoding='utf-8') as f:
    f.write(f"Total streams: {streams:,}\n")
    f.write(f"Total minutes streamed: {round(minutes_streamed, 2):,}\n")
    f.write(f"Total hours streamed: {hours_streamed:,}\n")
    f.write(f"Different tracks: {total_unique_tracks:,}\n")
    f.write(f"Different artists: {different_artists:,}\n\n")
    f.write(f"Top {num_artists} Most Streamed Artists:\n")
    f.write("-" * 30 + "\n")
    for artist, time in list(top_artists.items())[:num_artists]:
        artist_df = df[df['master_metadata_album_artist_name'] == artist]
        if artist_df.empty:
            continue
        minutes = time * 60
        df['ts'] = pd.to_datetime(df['ts'])
        first_listened = df['ts'].min().date()
        first_song = artist_df['master_metadata_track_name'].iloc[0]
        most_streamed_song = artist_df.groupby('master_metadata_track_name')['ms_played'].sum().idxmax()
        most_streamed_song_time = artist_df.groupby('master_metadata_track_name')['ms_played'].sum().max()
        most_streamed_song_time_hours = round(most_streamed_song_time / 60, 1)
        f.write(f'"{artist}"\n')
        f.write(f'   -> first listened on: {first_listened}\n')
        f.write(f'   -> first song streamed: {first_song}\n')
        f.write(f'   -> total listening time: {time} hours ({minutes:,.2f} minutes)\n')
        f.write(f'   -> most streamed song: {most_streamed_song} - {most_streamed_song_time_hours} hours ({most_streamed_song_time:,.2f} minutes)\n\n')
    f.write(f"\nTop {num_songs} Most Streamed Tracks:\n")
    f.write("-" * 30 + "\n")
    for (artist, track), time in list(top_tracks.items())[:num_songs]:
        minutes = time * 60
        track_df = df.loc[df['master_metadata_track_name'] == track].copy()  # use .copy() to avoid SettingWithCopyWarning from pandas
        if track_df.empty:
            continue
        track_df.loc[:, 'ts'] = pd.to_datetime(track_df['ts'])  # use .loc to modify the DataFrame in place
        first_listened = track_df['ts'].min().date()
        f.write(f'"{artist} - {track}"\n')
        f.write(f'   -> listened for {time} hours ({minutes:,.2f} minutes)\n')
        f.write(f'   -> first listened on {first_listened}\n\n')


os.makedirs(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified'), exist_ok=True)

def write_top_artists_func(top_artists_param, num_artists_param):
    with open(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified/TopArtists.txt'), 'w', encoding='utf-8') as f_param:
        f_param.write("Top Artists:\n")
        for i_param, (artist_param, time_param) in enumerate(sorted(top_artists_param.items(), key=lambda x: x[1], reverse=True)[:num_artists_param], start=1):
            minutes_param = time_param * 60
            safe_artist_param = artist_param.encode('ascii', 'ignore').decode()
            try:
                f_param.write(f"{i_param}. {safe_artist_param} - {time_param} hours ({minutes_param:,.2f} minutes)\n")
            except UnicodeEncodeError as e_param:
                with open(os.path.expanduser('~/Downloads/SpotifyStats/ErrorArtists.txt'), 'a', encoding='utf-8') as error_file_param:
                    error_file_param.write(f"Artist: {safe_artist_param}\n")
                    error_file_param.write(f"Error: {str(e_param)}\n\n")

write_top_artists_func(top_artists, num_artists)

with open(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified/TopSongs.txt'), 'w', encoding='utf-8') as f_param:
    f_param.write("Top Songs:\n")
    for i_param, (song_param, time_param) in enumerate(list(top_tracks.items())[:num_songs], start=1):
        song_name, artist_name = song_param
        minutes_param = time_param * 60
        try:
            f_param.write(f"{i_param}. {song_name} - {artist_name} - {time_param} hours ({minutes_param:,.2f} minutes)\n")
        except UnicodeEncodeError as e_param:
            with open(os.path.expanduser('~/Downloads/SpotifyStats/ErrorSongs.txt'), 'a', encoding='utf-8') as error_file_param:
                error_file_param.write(f"Song: {song_name}\n")
                error_file_param.write(f"Error: {str(e_param)}\n\n")
with open(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified/StatsSimplified.txt'), 'w', encoding='utf-8') as f:
    f.write(f"Total streams: {streams:,}\n")
    f.write(f"Total minutes streamed: {round(minutes_streamed, 2):,}\n")
    f.write(f"Total hours streamed: {hours_streamed:,}\n")
    f.write(f"Total days streamed: {round(hours_streamed / 24, 1):,}\n")
    f.write(f"Different tracks: {max_songs:,}\n")
    f.write(f"Different artists: {different_artists:,}\n\n")

print("Everything has be correctly written!\n")

print('\033[91m' + 'from now on, the code will create a website for you to view your stats on,')
print('this will include a website with your top 10 artists and songs, along with general stats')
print('this will be written to a folder in your downloads folder called SpotifyStats')
print('if you are just running the source code, it wont work, you need to run the executable' + '\033[0m' )
user_input = input('Press enter if you would like to continue with website creation, or type "n" to just open the folder with all your stats: ').lower()

if user_input.lower() == 'n':
    stats_folder = os.path.expanduser('~/Downloads/SpotifyStats')
    subprocess.run(['open', stats_folder])
else:
    print("\nNow writing website code...")
    print("please wait")

    client_id = 'nuhuh' # spotifyAPI is free???
    client_secret = 'nuhuh' # spotifyAPI is free???

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def write_spotify_ids(filename, type, ids_filename):
        filename = os.path.expanduser(filename)
        ids_filename = os.path.expanduser(ids_filename)

        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        top_ten = lines[1:11]
        names = [line.split('. ')[1].split(' - ')[0] if type == 'artist' else line.split('. ')[1].split(' - ')[1] for line in top_ten]
        artists = [line.split('. ')[1].split(' - ')[0] for line in top_ten] if type == 'track' else None

        ids = []
        for i, name in enumerate(names):
            query = f'artist:{artists[i]} track:{name}' if type == 'track' else name
            results = sp.search(q=query, type=type, limit=1)
            id = results['tracks']['items'][0]['id'] if type == 'track' else results['artists']['items'][0]['id']
            ids.append(id)

            if type == 'track':
                album = sp.album(results['tracks']['items'][0]['album']['id'])
                image_url = album['images'][0]['url']
            else:
                artist = sp.artist(id)
                image_url = artist['images'][0]['url']

            response = requests.get(image_url)

            safe_name = quote(name, safe='')
            image_filename = os.path.expanduser(f'~/Downloads/SpotifyStats/Images/{type}s/{safe_name}.jpg')
            os.makedirs(os.path.dirname(image_filename), exist_ok=True)
            with open(image_filename, 'wb') as f:
                f.write(response.content)

        with open(ids_filename, 'w', encoding='utf-8') as f:
            for id in ids:
                f.write(id + '\n')

        return ids

    print("\nCollecting Spotify ID's... :)")

    write_spotify_ids('~/Downloads/SpotifyStats/StatsSimplified/TopArtists.txt', 'artist',  '~/Downloads/SpotifyStats/StatsSimplified/TopArtistIDs.txt')
    write_spotify_ids('~/Downloads/SpotifyStats/StatsSimplified/TopSongs.txt', 'track',     '~/Downloads/SpotifyStats/StatsSimplified/TopSongIDs.txt')

    print("Collected Spotify ID's... :)\n")

    def upload_to_github(filename, repo, path, token):
        with open(filename, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')

        url = f'https://api.github.com/repos/{repo}/contents/{path}'
        headers = {
            'Authorization': f'token {token}',
            'Content-Type': 'application/json'
        }
        data = {
            'message': 'ur cute',
            'content': content
        }

        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()

    def upload_to_github(file_path, repo, path_in_repo, github_pat):
        with open(file_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')

        url = f'https://api.github.com/repos/{repo}/contents/{path_in_repo}'
        headers = {'Authorization': f'token {github_pat}'}
        data = {
            'message': f'ur cute :3',
            'content': content
        }
        response = requests.put(url, headers=headers, json=data)

    print('Calling you cute... :3\n')

    def generate_html_content():
        styles_file = 'website/styles.css'
        html_file = 'website/index.html'
        website_folder = 'website'

        if not os.path.exists(website_folder):
            os.makedirs(website_folder)

        print('Checking for necessary files...')

        if not os.path.exists(styles_file):
            print('File not found.. :(')
            url = 'https://raw.githubusercontent.com/countervolts/Apple-Music-Stats-Calculator/main/website/styles.css'
            r = requests.get(url)
            with open(styles_file, 'w') as f:
                f.write(r.text)

        if not os.path.exists(html_file):
            print('File not found.. :(')
            url = 'https://raw.githubusercontent.com/countervolts/Apple-Music-Stats-Calculator/main/website/index.html'
            r = requests.get(url)
            with open(html_file, 'w') as f:
                f.write(r.text)
        print('Files downloaded successfully... :D')

        print('Files located successfully... :D\n')

        github_pat = 'nope'

        username = input("Enter your username (up to 16 characters): ")[:16]

        if "/" in username:
            print("you cant have / in ur username cause it will break repo")
            return

        repo = 'countervolts/59problems'
        url = f'https://api.github.com/repos/{repo}/contents/spotify/users/{username}'
        headers = {'Authorization': f'token {github_pat}'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("already in use re-run code please")
            return
        elif response.status_code != 404:
            print("github or network error")
            return

        base_path = os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified')
        artist_file = os.path.join(base_path, 'TopArtists.txt')
        song_file = os.path.join(base_path, 'TopSongs.txt')
        stats_file = os.path.join(base_path, 'StatsSimplified.txt')

        with open(stats_file, 'r') as f:
            stats = f.readlines()

        print('\nDeciding where to put everything... :)')

        stats_html = f"""
        <div class="box">
            <p class="left-text">{username}</p>
            <p class="right-text">{stats[0]}<br>
            {stats[1]}<br>
            {stats[2]}<br>
            {stats[3]}<br>
            {stats[4]}<br>
            {stats[5]}</p>
        </div>
        """
        print('Decided where to put stuff... :)\n')
        print('Writing website code...')

        artists_html = '<div class="box box-left">\n'
        with open(artist_file, 'r') as f:
            artists = f.readlines()[1:11]
            for artist in artists:
                full_name, streams = artist.split(' - ', 1)
                _, name = full_name.split('. ', 1)
                name_without_spaces = name.replace(' ', '')
                artists_html += f"""
                <div class="section">
                    <img src="/spotify/users/{username}/images/artists/{name_without_spaces}.jpg" alt="{name}">
                    <p>{name}</p>
                    <p>{streams}</p>
                </div>
                """
        artists_html += '</div>\n'

        songs_html = '<div class="box box-right">\n'
        with open(song_file, 'r') as f:
                songs = f.readlines()[1:11]
                for song in songs:
                    _, full_name = song.split('. ', 1)
                    artist_name, song_name, streams = full_name.split(' - ', 2)
                    song_name = re.sub(r' \(feat.*', '', song_name)
                    song_name_without_spaces = song_name.replace(' ', '').replace('/', '').replace('!', '').replace('(',    '').replace(')', '')
                    hours_played = streams.split(' ')[0]
                    songs_html += f"""
                    <div class="section">
                        <img src="/spotify/users/{username}/images/songs/{song_name_without_spaces}.jpg" alt="{song_name}">
                        <p>{song_name}</p>
                        <p>{hours_played} hours</p>
                    </div>
                    """
        songs_html += '</div>\n'

        styles_file = 'website/styles.css'
        html_file = 'website/index.html'
        website_folder = 'website'

        with open(styles_file, 'r') as f:
            styles = f.read()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
            {styles}
            </style>
        </head>
        <body>
        {stats_html}
        {artists_html}
        {songs_html}
        </body>
        </html>
        """

        print('Wrote all code with no issues... :D')

        soup = BeautifulSoup(html_content, 'html.parser')
        pretty_html = soup.prettify()

        with open('output.html', 'w') as f:
            f.write(pretty_html)

        with open(html_file, 'w') as f:
            f.write(html_content)

        print('Code made pretty... :D')


        github_pat = 'nope'

        repo = 'countervolts/59problems'
        upload_to_github('website/index.html', repo, f'spotify/users/{username}/index.html', github_pat)

        image_dirs = {
            'artists': os.path.expanduser('~/Downloads/SpotifyStats/Images/artists'),
            'songs': os.path.expanduser('~/Downloads/SpotifyStats/Images/tracks')
        }

        for image_type, image_dir in image_dirs.items():
            for image_file in os.listdir(image_dir):
                full_path = os.path.join(image_dir, image_file)
                if os.path.isfile(full_path):
                    decoded_image_file = urllib.parse.unquote(image_file)
                    image_file_without_special_chars = re.sub(r'feat*', '', decoded_image_file)
                    image_file_without_special_chars = image_file_without_special_chars.replace(' ', '').replace('/', '').replace('!',  '').replace('(', '').replace(')', '')
                    image_path = f'spotify/users/{username}/images/{image_type}/{image_file_without_special_chars}'
                    upload_to_github(full_path, repo, image_path, github_pat)

        print(f'your website is located at https://59problems.me/spotify/users/{username}')

        print('\nWrote code to GitHub repo with no issues!!! :)\n')
    generate_html_content()

    print(f"Stats where also written to {os.path.expanduser('~/Downloads/SpotifyStats')}")

    input("\nPress Enter to view you stats :)")

    os.system("start " + os.path.expanduser('~/Downloads/SpotifyStats'))
