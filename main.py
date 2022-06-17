import requests
import sys
import os
from os.path import exists
from bs4 import BeautifulSoup
import json
import shutil
from urllib.parse import urlparse
import urllib.request


def getVideoRes():
    if (f852x428):
        print("1: 852x428")
    else:
        print("none : 852x428")

    if (f1920x1080):
        print("2: 1920x1080")
    else:
        print("none : 1920x1080")

    if (f1280x720):
        print("3: 1280x720")
    else:
        print("none : 1280x720")

    if (f640x360):
        print("4: 640x360")
    else:
        print("none : 640x360")

    return input("Select resolution: ")


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

# Video video resolution
try:
    m3u8_file = requests.get(m3u8)
except:
    print("Can't load m3u8_file")
    sys.exit(1)

lines = str(m3u8_file.text)

# Read resolutions
l852x428 = "852x480"
f852x428 = None
l1920x1080 = "1920x1080"
f1920x1080 = None
l1280x720 = "1280x720"
f1280x720 = None
l640x360 = "640x360"
f640x360 = None
video_exist = False

for line in lines.splitlines():
    pos = line.find("iframes-")
    if pos != -1:
        video_exist = True
        t = line.find(l852x428)
        if t != -1:
            f852x428 = line[pos + 8:pos + 24]
        t = line.find(l1920x1080)
        if t != -1:
            f1920x1080 = line[pos + 8:pos + 24]
        t = line.find(l1280x720)
        if t != -1:
            f1280x720 = line[pos + 8:pos + 24]
        t = line.find(l640x360)
        if t != -1:
            f640x360 = line[pos + 8:pos + 24]

if video_exist == False:
    print("No video available")
    sys.exit(1)

res_url = ""
res = int(getVideoRes())

if (int(res) < 1 or int(res) > 4):
    print("Wrong")
    sys.exit(1)

if (res == 1 and f852x428 == None) or (res == 2 and f1920x1080 == None) or (res == 3 and f1280x720 == None) or (
        res == 4 and f640x360 == None):
    print("Wrong")
    sys.exit(1)

if (res == 1):
    res_url = f852x428
elif (res == 2):
    res_url = f1920x1080
elif (res == 3):
    res_url = f1280x720
elif (res == 4):
    res_url = f640x360

video_id = urlparse(data["preroll"]['url']).query.replace("episode_id=", "")

if (video_id is None) or (video_id == ""):
    print("Wrong video ID")
    sys.exit(1)

output_file = input("Input filename [ENTER] for \"" + title + ".ts\": ")
if (output_file == None or output_file == ""):
    output_file = str(title) + ".ts"
else:
    output_file = str(output_file) + ".ts"

if (exists(output_file)):
    print("File " + str(output_file) + " already exist")
    sys.exit(1)

counter = 1
parts_count = 0
total = 0
tmp_size = 0

# Write file
if (os.path.isdir("tmp") == False):
    os.mkdir("tmp")

with open(output_file, 'wb') as merged:
    while True:

        fn = str(counter)
        for i in range(len(str(counter)), 9):
            fn = "0" + fn
        fn = "tmp/" + fn + ".ts"

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
            break
        parts_count += 1
        counter += 1