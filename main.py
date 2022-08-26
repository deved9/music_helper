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

def download_yt_video_as_mp3(video):
    stream = video.streams.filter(only_audio=True).order_by("abr").desc().first()
    path = stream.download("staging_area")
    os.system(f'ffmpeg -i \"{path}\" -vn -ab 156k -ar 44100 -y \"{path[:path.index(".webm")]}\".mp3')
    os.system(f'rm \"{path}\"')

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
                audio['album'] = ''
                audio.save(v2_version=3)
            except ValueError:
                print('error occured')

def main():
    print("Pro stažení playlistu z YT zvolte 1.\nPro upravení ID3 tagů mp3 souborů zadejte 2.\n")
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
        iterate_in_folder(os.path.abspath("./staging_area/"))
        os.system("mp3gain -c -r -d 6 staging_area/*")
        os.system("mp3check -r -3 -s -B -o -e -K --fix-headers --cut-junk-end staging_area/")
        return
    else:
        return

if __name__ == "__main__":
    main()
