# Stat Calculator
## How to request your Spotify listening history
1. Go to https://www.spotify.com/ca-en/account/privacy/
2. Login to your spotify account (if needed)
3. Scroll all the way down and click the box for "Extended Streaming History" and "Account Data"
4. then click "Request Data"
5. You should get a email from spotify for a confirmation, just do whatever it says.

## How to use this
ever since i added the executable within the releases tab its never been easier!
1. go to [releases](https://github.com/countervolts/Spotify-Stats-Calculator/releases/tag/exe)
2. click on reader.exe
3. wait for it to download
4. run file!

very easy, and it should automatically detect the "my_spotify_data.zip" within your downloads folder!

## How to use the code (non executable version)
1. run ```git clone https://github.com/countervolts/Spotify-Stats-Calculator```
2. make sure that your "my_spotify_data" folder is in same folder as the stat calculator (should be ```C:\Users\<username>\Spotify-Stats-Calculator```)
3. run ```cd Spotify-Music-Stats-Calculator```
4. run ```pip install -r requirements.txt```
5. run ```python reader.py```
6. when ran it should print "Pick a JSON: " if it says that and the "Streaming_History_music_*.json" json is in the folder press 1
7. allow it to process the streams (this should take a couple seconds)
8. when done it will print your top 10 artists as well as you top 10 songs, if you type "n" to writing a stats.txt file it will contain 50 artists and 50 songs and save in the same directory, type y to customize how much artists/songs you want in the stats.txt file.
 

## Examples
1. [command prompt output](https://github.com/countervolts/Spotify-Stats-Calculator/blob/main/examples/CommandPromptOutput.txt)
2. [full stats.txt output](https://github.com/countervolts/Spotify-Stats-Calculator/blob/main/examples/Stats.txt)

## Support / Suggestions
my discord is [._ayo](https://discord.com/users/488368000055902228) <--- or just click the link
support discord server: [invite](https://discord.gg/rP63gxfKQJ)

## **DISCLAIMER**
1. SemiAutomaticMode not automatically scanning the dir its chosen to (literally the only thing its meant to do and it cant even) 
2. im aware of when you try to get ALL your stats (literally max both artists and songs) majority will display as 0.0 hours (0.0 minutes)
## pylint
pylint rated my updated code at 7.17/10 (previous run: 7.27/10, -0.10) im sad :(
