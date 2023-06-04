#!/usr/bin/python

# Init Virtual environment
exec(open("venv/bin/activate_this.py").read(), {'__file__': "venv/bin/activate_this.py"})

#For YT downloading
from pytube import Playlist, YouTube
import re
import os, sys, time
from multiprocessing import Process, Queue, active_children

#For ID3 tags
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from stat import *

#For argument parsing
import argparse

#colored error message
from termcolor import colored

def download_yt_video_as_mp3(down_queue):
    while True:
        if down_queue.empty():
            # nothing more to download
            return

        # download next video
        video = down_queue.get()
        stream = video.streams.filter(only_audio=True).order_by("abr").desc().first()
        path = stream.download("staging_area")
        conv_queue.put(path)

def convert_vid(conv_queue,down_done):
    while True:
        while conv_queue.empty():
            time.sleep(1)

        path = conv_queue.get()
        if path == "SHUTDOWN":
            return
        
        
        os.system(f'ffmpeg -i \"{path}\" -vn -ab 156k -ar 44100 -y \"{path[:path.index(".webm")]}\".mp3')
        os.system(f'rm \"{path}\"')

#Clean ID3 tags in all mp3 files
def iterate_in_folder(path, recurse):
    for item in os.listdir(path):
        if S_ISDIR(os.stat(os.path.join(path,item))[ST_MODE]) and recurse:
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
            except ValueError as E:
                print(colored(f'error occured on song {item}','red'))
                print(E)

def main():
    parser = argparse.ArgumentParser(description='''Youtube playlist download software\n
Modes:
(1) Download from yt link
(2) Clear ID3 tags and normalize volume
(3) Only clear ID3 tags''',
formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-r','--recurse', help='recurse into subfolders (only for mode 2 and 3)', action='store_true')
    parser.add_argument('mode',help='select mode of operation',default=1)
    parser.add_argument('-l','--link',help='link to YouTube playlist to download (only for mode 1)', action='store')
    
    args = parser.parse_args()

    #print("Pro stažení playlistu z YT zvolte 1.\nPro upravení ID3 tagů mp3 souborů a vyrovnání hlasitosti zadejte 2.\nPro upravení ID3 tagů mp3 souborů zadejte 3.\n")
    
    mode = args.mode #input("Co chcete udělat: ")
    if(mode == "1"):
        global PLAYLIST_URL
        PLAYLIST_URL = args.link
        if not args.link: parser.error('Link not provided or wrong mode selected')
        
        #Download and convert songs from YT to mp3
        pl = Playlist(PLAYLIST_URL)
        
        global down_queue
        global conv_queue
        global down_done
        down_done = False
        down_queue = Queue()
        conv_queue = Queue()

        for video in pl.videos:
            down_queue.put(video)

        # Create download workers
        num_workers = 5
        down_workers = []
        conv_workers = []
        try:
            for _ in range(num_workers):
                p = Process(target=download_yt_video_as_mp3,args=(down_queue,))
                p.start()

                down_workers.append(p)

                # Create convert workers
                x = Process(target=convert_vid,args=(conv_queue,down_done,))
                x.start()

                conv_workers.append(x)

            # downloading is done
            for proc in down_workers:
                proc.join()

            for _ in range(num_workers):
                conv_queue.put("SHUTDOWN")
                
            #wait for conversion to complete
            for proc in conv_workers:
                proc.join()
        except KeyboardInterrupt:
            for child in active_children():
                child.terminate()

        return
    elif(mode == "2"):
        #Clean out the names and ID3 tags
        iterate_in_folder(os.path.abspath("./staging_area/"),False)
        # stabilize audio and clear shit
        os.system("mp3gain -c -r -d 6 staging_area/*")
        os.system("mp3check -r -3 -s -B -o -e -K --fix-headers --cut-junk-end staging_area/")
        return
    elif(mode == "3"):
        #only clear tags
        iterate_in_folder(os.path.abspath("./staging_area/"))
    else:
        return

if __name__ == "__main__":
    main()
