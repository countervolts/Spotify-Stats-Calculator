import os,time,glob,zipfile,re,pandas as pd
from tqdm import tqdm
import requests,base64,shutil,subprocess,urllib.parse
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
current_dir=os.path.dirname(os.path.realpath(__file__))
home_dir=os.path.expanduser('~')
os.system('cls'if os.name=='nt'else'clear')
scan_dirs=[os.path.join(home_dir,dir_name)for dir_name in['Downloads']]
total_files={dir_name:sum(len(files)for files in os.walk(dir_name))for dir_name in scan_dirs}
should_break=False
for dir_name in scan_dirs:
	if should_break:break
is_found=False
file_count=0
for(root,dirs,files)in os.walk(dir_name):
	if should_break:break
	for file in files:
		if file=='my_spotify_data.zip':
			with zipfile.ZipFile(os.path.join(root,file),'r')as zip_ref:print(f"\nExtracting {file} in {root}...\n");zip_ref.extractall(root);is_found=True;print(f"\nSuccess! 'my_spotify_data.zip' was found and extracted to {root}.")
	json_files=[]
	for dir_name in scan_dirs:json_files.extend(glob.glob(os.path.join(dir_name,'**','StreamingHistory_music_*.json'),recursive=True));json_files=[os.path.relpath(file,current_dir)for file in json_files];selected_files=json_files
os.system('cls'if os.name=='nt'else'clear')
data=[]
missing_msPlayed_files=[]
downloads_dir=os.path.join(os.path.expanduser('~'),'Downloads')
for file in selected_files:file_name=os.path.basename(file);file_dir=os.path.join(downloads_dir,'Spotify Account Data',file_name);df=pd.read_json(file_dir);data.append(df)
os.system('cls'if os.name=='nt'else'clear')
df=pd.concat(data,ignore_index=True)
if'msPlayed'in df.columns:df['msPlayed']=df['msPlayed']/60000
else:print(f"msPlayed column not found in the following JSON files: {', '.join(missing_msPlayed_files)}")
grouped_artist=df.groupby('artistName')['msPlayed'].sum()
grouped_artist=grouped_artist.apply(lambda x:round(x/60,1))
top_50_artists=grouped_artist.sort_values(ascending=False).head(50)
grouped_track=df.groupby(['artistName','trackName'])['msPlayed'].sum()
grouped_track=grouped_track.apply(lambda x:round(x/60,1))
top_50_tracks=grouped_track.sort_values(ascending=False).head(50)
streams=len(df)
minutes_streamed=df['msPlayed'].sum()
hours_streamed=round(minutes_streamed/60,1)
different_tracks=df['trackName'].nunique()
different_artists=df['artistName'].nunique()
days_streamed=hours_streamed/24
downloads_dir=os.path.expanduser('~/Downloads')
spotify_stats_dir=os.path.join(downloads_dir,'SpotifyStats')
os.makedirs(spotify_stats_dir,exist_ok=True)
max_artists=len(df['artistName'].unique())
max_songs=len(df['trackName'].unique())
top_artists=grouped_artist.sort_values(ascending=False)
for artist in top_artists.index:artist_data=df[df['artistName']==artist];top_songs=artist_data.groupby('trackName')['msPlayed'].sum().sort_values(ascending=False).head(10);total_streaming_time=artist_data['msPlayed'].sum();different_tracks=artist_data['trackName'].nunique();num_artists=10;num_songs=10;top_artists=top_50_artists;top_tracks=top_50_tracks
total_unique_tracks=df['trackName'].nunique()
with open(os.path.join(spotify_stats_dir,'Stats.txt'),'w',encoding='utf-8')as f:f.write(f"Total streams: {streams:,}\n");f.write(f"Total minutes streamed: {round(minutes_streamed,2):,}\n");f.write(f"Total hours streamed: {hours_streamed:,}\n");f.write(f"Different tracks: {total_unique_tracks:,}\n");f.write(f"Different artists: {different_artists:,}\n\n");f.write(f"Top {num_artists} Most Streamed Artists:\n")
os.makedirs(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified'),exist_ok=True)
def write_top_artists_func(top_artists_param,num_artists_param):
	with open(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified/TopArtists.txt'),'w',encoding='utf-8')as f_param:
		f_param.write('Top Artists:\n')
		for(i_param,(artist_param,time_param))in enumerate(sorted(top_artists_param.items(),key=lambda x:x[1],reverse=True)[:num_artists_param],start=1):minutes_param=time_param*60;safe_artist_param=artist_param.encode('ascii','ignore').decode();f_param.write(f"{i_param}. {safe_artist_param} - {time_param} hours ({minutes_param:,.2f} minutes)\n")
write_top_artists_func(top_artists,num_artists)
with open(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified/TopSongs.txt'),'w',encoding='utf-8')as f_param:
	f_param.write('Top Songs:\n')
	for(i_param,(song_param,time_param))in enumerate(list(top_tracks.items())[:num_songs],start=1):song_name,artist_name=song_param;minutes_param=time_param*60;f_param.write(f"{i_param}. {song_name} - {artist_name} - {time_param} hours ({minutes_param:,.2f} minutes)\n")
with open(os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified/StatsSimplified.txt'),'w',encoding='utf-8')as f:f.write(f"Total streams: {streams:,}\n");f.write(f"Total minutes streamed: {round(minutes_streamed,2):,}\n");f.write(f"Total hours streamed: {hours_streamed:,}\n");f.write(f"Total days streamed: {round(hours_streamed/24,1):,}\n");f.write(f"Different tracks: {max_songs:,}\n");f.write(f"Different artists: {different_artists:,}\n\n")
print('Everything has be correctly written!\n')
print('\x1b[91m'+'from now on, the code will create a website for you to view your stats on,')
print('this will include a website with your top 10 artists and songs, along with general stats')
print('this will be written to a folder in your downloads folder called SpotifyStats')
print('if you are just running the source code, it wont work, you need to run the executable'+'\x1b[0m')
user_input=input('Press enter if you would like to continue with website creation, or type "n" to just open the folder with all your stats: ').lower()
if user_input.lower()=='n':stats_folder=os.path.expanduser('~/Downloads/SpotifyStats');subprocess.run(['open',stats_folder])
else:
	print('\nNow writing website code...');print('please wait');client_id='nope';client_secret='nope';client_credentials_manager=SpotifyClientCredentials(client_id=client_id,client_secret=client_secret);sp=spotipy.Spotify(client_credentials_manager=client_credentials_manager)
	def write_spotify_ids(filename,type,ids_filename):
		filename=os.path.expanduser(filename);ids_filename=os.path.expanduser(ids_filename)
		with open(filename,'r',encoding='utf-8')as f:lines=f.readlines()
		top_ten=lines[1:11];names=[line.split('. ')[1].split(' - ')[0]if type=='artist'else line.split('. ')[1].split(' - ')[1]for line in top_ten];artists=[line.split('. ')[1].split(' - ')[0]for line in top_ten]if type=='track'else None;ids=[]
		for(i,name)in enumerate(names):
			query=f"artist:{artists[i]} track:{name}"if type=='track'else name;results=sp.search(q=query,type=type,limit=1);id=results['tracks']['items'][0]['id']if type=='track'else results['artists']['items'][0]['id'];ids.append(id)
			if type=='track':album=sp.album(results['tracks']['items'][0]['album']['id']);image_url=album['images'][0]['url']
			else:artist=sp.artist(id);image_url=artist['images'][0]['url']
			response=requests.get(image_url);safe_name=quote(name,safe='');image_filename=os.path.expanduser(f"~/Downloads/SpotifyStats/Images/{type}s/{safe_name}.jpg");os.makedirs(os.path.dirname(image_filename),exist_ok=True)
			with open(image_filename,'wb')as f:f.write(response.content)
		with open(ids_filename,'w',encoding='utf-8')as f:
			for id in ids:f.write(id+'\n')
		return ids
	print("\nCollecting Spotify ID's... :)");write_spotify_ids('~/Downloads/SpotifyStats/StatsSimplified/TopArtists.txt','artist','~/Downloads/SpotifyStats/StatsSimplified/TopArtistIDs.txt');write_spotify_ids('~/Downloads/SpotifyStats/StatsSimplified/TopSongs.txt','track','~/Downloads/SpotifyStats/StatsSimplified/TopSongIDs.txt');print("Collected Spotify ID's... :)\n")
	def upload_to_github(filename,repo,path,token):
		with open(filename,'rb')as f:content=base64.b64encode(f.read()).decode('utf-8')
		url=f"https://api.github.com/repos/{repo}/contents/{path}";headers={'Authorization':f"token {token}",'Content-Type':'application/json'};data={'message':'ur cute','content':content};response=requests.put(url,headers=headers,json=data);response.raise_for_status()
	def upload_to_github(file_path,repo,path_in_repo,github_pat):
		with open(file_path,'rb')as f:content=base64.b64encode(f.read()).decode('utf-8')
		url=f"https://api.github.com/repos/{repo}/contents/{path_in_repo}";headers={'Authorization':f"token {github_pat}"};data={'message':f"ur cute :3",'content':content};response=requests.put(url,headers=headers,json=data)
	print('Calling you cute... :3\n')
	def generate_html_content():
		styles_file='website/styles.css';html_file='website/index.html';website_folder='website'
		if not os.path.exists(website_folder):os.makedirs(website_folder)
		print('Checking for necessary files...')
		if not os.path.exists(styles_file):
			print('File not found.. :(');url='https://raw.githubusercontent.com/countervolts/Apple-Music-Stats-Calculator/main/website/styles.css';r=requests.get(url)
			with open(styles_file,'w')as f:f.write(r.text)
		if not os.path.exists(html_file):
			print('File not found.. :(');url='https://raw.githubusercontent.com/countervolts/Apple-Music-Stats-Calculator/main/website/index.html';r=requests.get(url)
			with open(html_file,'w')as f:f.write(r.text)
		print('Files downloaded successfully... :D');print('Files located successfully... :D\n');github_pat='nope';username=input('Enter your username (up to 16 characters): ')[:16]
		if'/'in username:print('you cant have / in ur username cause it will break repo');return
		repo='countervolts/59problems';url=f"https://api.github.com/repos/{repo}/contents/spotify/users/{username}";headers={'Authorization':f"token {github_pat}"};response=requests.get(url,headers=headers)
		if response.status_code==200:print('already in use re-run code please');return
		elif response.status_code!=404:print('github or network error');return
		base_path=os.path.expanduser('~/Downloads/SpotifyStats/StatsSimplified');artist_file=os.path.join(base_path,'TopArtists.txt');song_file=os.path.join(base_path,'TopSongs.txt');stats_file=os.path.join(base_path,'StatsSimplified.txt')
		with open(stats_file,'r')as f:stats=f.readlines()
		print('\nDeciding where to put everything... :)');stats_html=f'''
        <div class="box">
            <p class="left-text">{username}</p>
            <p class="right-text">{stats[0]}<br>
            {stats[1]}<br>
            {stats[2]}<br>
            {stats[3]}<br>
            {stats[4]}<br>
            {stats[5]}</p>
        </div>
        ''';print('Decided where to put stuff... :)\n');print('Writing website code...');artists_html='<div class="box box-left">\n'
		with open(artist_file,'r')as f:
			artists=f.readlines()[1:11]
			for artist in artists:full_name,streams=artist.split(' - ',1);_,name=full_name.split('. ',1);name_without_spaces=name.replace(' ','');artists_html+=f'''
                <div class="section">
                    <img src="/spotify/users/{username}/images/artists/{name_without_spaces}.jpg" alt="{name}">
                    <p>{name}</p>
                    <p>{streams}</p>
                </div>
                '''
		artists_html+='</div>\n';songs_html='<div class="box box-right">\n'
		with open(song_file,'r')as f:
			songs=f.readlines()[1:11]
			for song in songs:_,full_name=song.split('. ',1);artist_name,song_name,streams=full_name.split(' - ',2);song_name=re.sub(' \\(feat.*','',song_name);song_name_without_spaces=song_name.replace(' ','').replace('/','').replace('!','').replace('(','').replace(')','');hours_played=streams.split(' ')[0];songs_html+=f'''
                    <div class="section">
                        <img src="/spotify/users/{username}/images/songs/{song_name_without_spaces}.jpg" alt="{song_name}">
                        <p>{song_name}</p>
                        <p>{hours_played} hours</p>
                    </div>
                    '''
		songs_html+='</div>\n';styles_file='website/styles.css';html_file='website/index.html';website_folder='website'
		with open(styles_file,'r')as f:styles=f.read()
		html_content=f"""
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
        """;print('Wrote all code with no issues... :D');soup=BeautifulSoup(html_content,'html.parser');pretty_html=soup.prettify()
		with open('output.html','w')as f:f.write(pretty_html)
		with open(html_file,'w')as f:f.write(html_content)
		print('Code made pretty... :D');github_pat='nope';repo='countervolts/59problems';upload_to_github('website/index.html',repo,f"spotify/users/{username}/index.html",github_pat);image_dirs={'artists':os.path.expanduser('~/Downloads/SpotifyStats/Images/artists'),'songs':os.path.expanduser('~/Downloads/SpotifyStats/Images/tracks')}
		for(image_type,image_dir)in image_dirs.items():
			for image_file in os.listdir(image_dir):
				full_path=os.path.join(image_dir,image_file)
				if os.path.isfile(full_path):decoded_image_file=urllib.parse.unquote(image_file);image_file_without_special_chars=re.sub('feat*','',decoded_image_file);image_file_without_special_chars=image_file_without_special_chars.replace(' ','').replace('/','').replace('!','').replace('(','').replace(')','');image_path=f"spotify/users/{username}/images/{image_type}/{image_file_without_special_chars}";upload_to_github(full_path,repo,image_path,github_pat)
		print(f"your website is located at https://59problems.me/spotify/users/{username}");print('\nWrote code to GitHub repo with no issues!!! :)\n')
	generate_html_content();print(f"Stats where also written to {os.path.expanduser('~/Downloads/SpotifyStats')}");input('\nPress Enter to view you stats :)');os.system('start '+os.path.expanduser('~/Downloads/SpotifyStats'))