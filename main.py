import subprocess

import requests
import sys
import os
from os.path import exists
from bs4 import BeautifulSoup
import json
import shutil
from urllib.parse import urlparse
import urllib.request


def die(mes):
    if mes is not None:
        print(mes)
    input("Press enter to exit")
    sys.exit(-1)


# Go
video_url = input("URL: ")

# Get page url
page = None
try:
    page = requests.get(video_url)
except Exception as e:
    die(str(e))

if page.status_code != 200:
    die("Error " + str(page.status_code))

# Parse
soup = BeautifulSoup(page.text, 'html.parser')
val = soup.find('div', class_='relative h-full w-full')

if val is None:
    die("Wrong url")

# Value
data = json.loads(str(val['data-player-ad-value']))
if data is None:
    die("Wrong data")

# m3u8 URL
m3u8 = str(val['data-player-source-value'])
if m3u8 is None:
    die("Wrong data (no m3u8 url)")

# Video title
title = str(val['data-player-title-value'])
if title is None:
    die("Wrong data (no title)")
print(title)

# Video resolution
m3u8_file = ""
try:
    m3u8_file = requests.get(m3u8)
except ImportError:
    die("Can't load m3u8_file")

# Read resolutions
lines = str(m3u8_file.text)
video_exist = False
videos = []

for line in lines.splitlines():
    pos = line.find("iframes-")
    resol = ""
    vid_id = ""
    if pos != -1:
        s = line.split(",")
        for ss in s:
            if ss.find("RESOLUTION=") != -1:
                resol = ss.replace("RESOLUTION=", "")

        vid_id = line[pos + 8:pos + 24]
        print(str(resol) + " " + str(vid_id))
        videos.append([str(resol), str(vid_id)])
        if str(resol) != "" and str(vid_id) != "":
            video_exist = True

if not video_exist:
    die("No video available")

counter = 0
for video_counter in videos:
    counter += 1
    print(str(counter) + ": " + str(video_counter[0]))
res = int(input("Select resolution: ")) - 1

res_url = videos[res][1]

video_id = urlparse(data["preroll"]['url']).query.replace("episode_id=", "")

if (video_id is None) or (video_id == ""):
    die("Wrong video ID")

output_file = input("Input filename [ENTER] for \"" + title + ".ts\": ")
if output_file is None or output_file == "":
    output_file = str(title) + ".ts"
else:
    output_file = str(output_file) + ".ts"

if exists(output_file):
    die("File " + str(output_file) + " already exist")

counter = 1
parts_count = 0
total = 0
tmp_size = 0

# Write file

if not os.path.isdir(dir_name := "hole_tmp"):
    os.mkdir(dir_name)

with open(output_file, 'wb') as merged:
    while True:

        fn = str(counter)
        for i in range(len(str(counter)), 9):
            fn = "0" + fn
        fn = dir_name + "/" + fn + ".ts"

        url = "https://video-cdn.the-hole.tv/episodes/" + video_id + "/segment-" + str(counter) + "-" + str(
            res_url) + ".ts"

        t = requests.head(url)

        if t.status_code == 200:

            urllib.request.urlretrieve(url, fn)

            with open(fn, 'rb') as mergefile:
                shutil.copyfileobj(mergefile, merged)
            tmp_size = os.path.getsize(fn) / 1048576
            if os.path.exists(fn):
                os.remove(fn)
            print(str(parts_count) + " - " + fn + " - " + str(round(tmp_size, 2)))
            total += tmp_size
        else:
            mergefile.close()
            print("Finish")
            print(str(round(total, 2)) + " MB")
            if os.path.isdir(dir_name):
                os.rmdir(dir_name)
            y = input("Convert to Matroska (.mkv)? [y/N]: ")
            if y == "y" or y == "Y" or y == "Yes":
                print("Converting...")
                subprocess.run(['ffmpeg', '-i', output_file, output_file.replace(".ts", ".mkv")])
                print(str(round(int(os.path.getsize(output_file.replace(".ts", ".mkv")) / 1048576), 2)) + " MB")
            y = input("Convert to MPEG-4 (.mp4)? [y/N]: ")
            if y == "y" or y == "Y" or y == "Yes":
                print("Converting...")
                subprocess.run(['ffmpeg', '-i', output_file, output_file.replace(".ts", ".mp4")])
                print(str(round(int(os.path.getsize(output_file.replace(".ts", ".mp4")) / 1048576), 2)) + " MB")
            y = input("Convert to AVI (.avi)? [y/N]: ")
            if y == "y" or y == "Y" or y == "Yes":
                print("Converting...")
                subprocess.run(['ffmpeg', '-i', output_file, output_file.replace(".ts", ".avi")])
                print(str(round(int(os.path.getsize(output_file.replace(".ts", ".avi")) / 1048576), 2)) + " MB")
            break
        parts_count += 1
        counter += 1
