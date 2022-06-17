import requests
import sys
import os
from os.path import exists
from bs4 import BeautifulSoup
import json
import shutil
from urllib.parse import urlparse
import urllib.request

# Go
video_url = input("URL: ")

# Get page url
try:
    page = requests.get(video_url)
except Exception as e:
    print(str(e))
    sys.exit(1)

if page.status_code != 200:
    print("Error " + str(page.status_code))
    sys.exit(1)

# Parse
soup = BeautifulSoup(page.text, 'html.parser')
val = soup.find('div', class_='relative h-full w-full')

if val is None:
    print("Wrong url")
    sys.exit(1)

# Value
data = json.loads(str(val['data-player-ad-value']))
if data is None:
    print("Wrong data")
    sys.exit(1)

# m3u8 URL
m3u8 = str(val['data-player-source-value'])
if m3u8 is None:
    print("Wrong data (no m3u8 url)")
    sys.exit(1)

# Video title
title = str(val['data-player-title-value'])
if title is None:
    print("Wrong data (no title)")
    sys.exit(1)

print(title)

# Video resolution
try:
    m3u8_file = requests.get(m3u8)
except ImportError:
    print("Can't load m3u8_file")
    sys.exit(1)

lines = str(m3u8_file.text)

# Read resolutions
l852x428 = "852x4801"
f852x428 = None
l1920x1080 = "1920x1080"
f1920x1080 = None
l1280x720 = "1280x720"
f1280x720 = None
l640x360 = "640x360"
f640x360 = None

video_exist = False
videos = []

for line in lines.splitlines():
    pos = line.find("iframes-")
    if pos != -1:
        video_exist = True
        c = 1
        t = line.find(l852x428)
        if t != -1:
            f852x428 = line[pos + 8:pos + 24]
            videos.append([l852x428, f852x428])
        t = line.find(l1920x1080)
        if t != -1:
            f1920x1080 = line[pos + 8:pos + 24]
            videos.append([l1920x1080, f1920x1080])
        t = line.find(l1280x720)
        if t != -1:
            f1280x720 = line[pos + 8:pos + 24]
            videos.append([l1280x720, f1280x720])
        t = line.find(l640x360)
        if t != -1:
            f640x360 = line[pos + 8:pos + 24]
            videos.append([l640x360, f640x360])

if not video_exist:
    print("No video available")
    sys.exit(1)

c = 0
for video_counter in videos:
    c += 1
    print(str(c) + ": " + str(video_counter[0]))
res = int(input("Select resolution: "))-1


res_url = videos[res][1]

video_id = urlparse(data["preroll"]['url']).query.replace("episode_id=", "")

if (video_id is None) or (video_id == ""):
    print("Wrong video ID")
    sys.exit(1)

output_file = input("Input filename [ENTER] for \"" + title + ".ts\": ")
if output_file is None or output_file == "":
    output_file = str(title) + ".ts"
else:
    output_file = str(output_file) + ".ts"

if exists(output_file):
    print("File " + str(output_file) + " already exist")
    sys.exit(1)

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
