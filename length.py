from mutagen.mp3 import MP3
import os
from stat import *

path = input("path to directory with mp3: ")
path = os.path.abspath(path)

def iterate_in_folder(path):
    ln = 0
    num = 0
    for item in os.listdir(path):
        if S_ISDIR(os.stat(os.path.join(path,item))[ST_MODE]):
            ln_temp, num_temp = iterate_in_folder(os.path.join(path,item))
            ln += ln_temp
            num += num_temp
        elif item.endswith("mp3"):
            audio = MP3(os.path.join(path,item))
            print(str(item) + "  " + str(audio.info.length))
            num += 1
            ln += audio.info.length
    return ln, num


total_time_s, num_of_mp3 = iterate_in_folder(path)
total_hours = int(total_time_s/3600)
zbytek_minut_int = total_time_s/3600 - int(total_time_s/3600)
minuty = int(zbytek_minut_int*60)
sec_int = zbytek_minut_int*60 - int(zbytek_minut_int*60)
sec = sec_int*60

print(f"Total time: {total_hours}:{minuty}:{sec} ve {num_of_mp3} mp3 souborech")