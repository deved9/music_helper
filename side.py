#!/usr/bin/python

# Init Virtual environment
exec(open("venv/bin/activate_this.py").read(), {'__file__': "venv/bin/activate_this.py"})

#For YT downloading
from pytube import Playlist
import os, sys
from multiprocessing import Pool

#For ID3 tags
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from stat import *

#For spotify
import requests
from urllib.parse import quote

def download_yt_video_as_mp3(video):
    stream = video.streams.filter(only_audio=True).order_by("abr").desc().first()
    path = stream.download("staging_area")
    os.system(f'ffmpeg -i \"{path}\" -vn -ab 160k -ar 44100 -y \"{path[:path.index(".webm")]}\".mp3')
    os.system(f'rm \"{path}\"')

def get_album_from_spotify(item):
    headers = {"Accept" : "application/json",
               "Content-Type" : "application/json",
               "Authorization" : "Bearer BQBpvGjAOlCEEO6yt8TULtsckLht8VxJdIhp8TqIqk1Wqvk-YZfC1HS5x6fYJGUrTCBzrJj7azCWNpIpRLSaFLS7CBajpGE3R66PGFGGAGiMWZOoz9Bir-5B4IaX6n5O4YWc8o0-yS6ekekFAB4_TJoko7Pl0qwQPFzQ5BkzHuf1QUcuVWVEwAsLTiOXG1aKL4I"
               }
    url = f"https://api.spotify.com/v1/search?q={quote(item)}&type=track&market=CZ&limit=10"

    print(f"firefox https://www.google.com/search?q={item.replace(' ', '+')}")
    os.system(f'firefox https://www.google.com/search?q={quote(item+" album")}')
    response = requests.get(url, headers = headers)
    print(response.status_code)
    album_names = []
    print(item)
    for i in range(len(response.json()["tracks"]["items"])):
        name = response.json()["tracks"]["items"][i]["album"]["name"]
        if "(" in name:
            name = name[:name.index("(")]
            while name.endswith(" "): name = name[:-1]
        album_names.append(name)
        print(str(i) + " " + name)
    
    index = input("Select album name: ")
    if index == "":
        return input("Zadej název alba: ")
    
    return album_names[int(index)]

#Clean ID3 tags in all mp3 files
def iterate_in_folder(path):
    ln = 0
    num = 0
    for item in os.listdir(path):
        if S_ISDIR(os.stat(os.path.join(path,item))[ST_MODE]):
            iterate_in_folder(os.path.join(path,item))
        elif item.endswith("mp3"):
            audio = MP3(os.path.join(path,item))
            print(str(item) + "  " + str(audio.info.length))
            try:
                mp3 = MP3(os.path.join(path,item))
                mp3.delete()
                mp3.save()
                audio = EasyID3(os.path.join(path,item))
                audio["artist"] = item[:item.index("-")-1] if item[:item.index("-")-1] else None
                audio['genre'] = ''
                audio['title'] = item[:item.index(".mp3")]
                audio['date'] = ''
                audio['album'] = get_album_from_spotify(item.replace(".mp3", "")) if False else ""
                audio.save(v2_version=3)
            except ValueError:
                print(f'error occured {item}')

def main():
    print("Pro stažení playlistu z YT zvolte 1.\nPro upravení ID3 tagů mp3 souborů a vyrovnání hlasitosti zadejte 2.\nPro upravení ID3 tagů mp3 souborů zadejte 3.\n")
    mode = input("Co chcete udělat: ")
    if(mode == "1"):
        global PLAYLIST_URL
        PLAYLIST_URL = input("Vložte URL adresu Youtube playlistu pro stažení: ")
        #Download and convert songs from YT to mp3
        pl = Playlist(PLAYLIST_URL)
        
        with Pool(5) as p:
            p.map(download_yt_video_as_mp3, pl.videos)
        return
    elif(mode == "2"):
        #Clean out the names and ID3 tags
        iterate_in_folder(os.path.abspath("Music"))
        # stabilize audio and clear shit
        os.system("mp3gain -c -r -d 6 Music/* Music/Deathcore/* Music/Bluez/Czech/* Music/Bluez/Worldwide/* Music/Funkrock/*")
        os.system("mp3check -r -3 -s -B -o -e -K --fix-headers --cut-junk-end Music/* Music/Deathcore/* Music/Bluez/Czech/* Music/Bluez/Worldwide/* Music/Funkrock/*")
        return
    elif(mode == "3"):
        #only clear tags
        iterate_in_folder(os.path.abspath("./staging_area/"),True)
    else:
        return

if __name__ == "__main__":
    main()
