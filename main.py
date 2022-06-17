import requests
import sys
import os
from os.path import exists
from bs4 import BeautifulSoup
import json
import shutil
from urllib.parse import urlparse
import urllib.request


def die():
    input("Press enter to exit")
    sys.exit(-1)


# Go
video_url = input("URL: ")

# Get page url
try:
    page = requests.get(video_url)
except Exception as e:
    print(str(e))
    die()

if page.status_code != 200:
    print("Error " + str(page.status_code))
    die()

# Parse
soup = BeautifulSoup(page.text, 'html.parser')
val = soup.find('div', class_='relative h-full w-full')

if val is None:
    print("Wrong url")
    die()

# Value
data = json.loads(str(val['data-player-ad-value']))
if data is None:
    print("Wrong data")
    die()

# m3u8 URL
m3u8 = str(val['data-player-source-value'])
if m3u8 is None:
    print("Wrong data (no m3u8 url)")
    die()

# Video title
title = str(val['data-player-title-value'])
if title is None:
    print("Wrong data (no title)")
    die()
print(title)

# Video resolution
try:
    m3u8_file = requests.get(m3u8)
except ImportError:
    print("Can't load m3u8_file")
    die()

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
    print("No video available")
    die()

counter = 0
for video_counter in videos:
    counter += 1
    print(str(counter) + ": " + str(video_counter[0]))
res = int(input("Select resolution: ")) - 1

res_url = videos[res][1]

video_id = urlparse(data["preroll"]['url']).query.replace("episode_id=", "")

if (video_id is None) or (video_id == ""):
    print("Wrong video ID")
    die()

output_file = input("Input filename [ENTER] for \"" + title + ".ts\": ")
if output_file is None or output_file == "":
    output_file = str(title) + ".ts"
else:
    output_file = str(output_file) + ".ts"

if exists(output_file):
    print("File " + str(output_file) + " already exist")
    die()

counter = 1
parts_count = 0
total = 0
tmp_size = 0

# Write file
dir_name = "hole_tmp"
if not os.path.isdir(dir_name):
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
            print("Finish")
            print(str(round(total, 2)) + " MB")
            if os.path.isdir(dir_name):
                os.rmdir(dir_name)
            break
        parts_count += 1
        counter += 1
