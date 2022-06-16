import sys
import urllib.request
import requests
import os
import shutil
import json

from urllib.parse import urlparse
from bs4 import BeautifulSoup


if __name__ == '__main__':

    counter = 1
    max_count = 5
    parts_count = 0
    total = 0
    tmp_size = 0

    video_url = "https://the-hole.tv/episodes/istorii-zvezda"

    print("Hello")

    page = requests.get(video_url)

    soup = BeautifulSoup(page.text, 'html.parser')
    val = soup.find('div', class_='relative h-full w-full')

    if val is None:
        print("Wrong url")
        sys.exit()

    data = json.loads(str(val['data-player-ad-value']))
    if data is None:
        print("Wrong data")
        sys.exit()

    m3u8 = str(val['data-player-source-value'])
    print(m3u8)

    title = str(val['data-player-title-value'])
    print(title)

    m3u8_file = requests.get(m3u8)
    lines = str(m3u8_file.text)

    l852x428 = "852x480"
    f852x428 = None
    l1920x1080 = "1920x1080"
    f1920x1080 = None
    l1280x720 = "1280x720"
    f1280x720 = None
    l640x360 = "640x360"
    f640x360 = None

    for line in lines.splitlines():
        pos = line.find("iframes-")
        if pos != -1:
            t = line.find(l852x428)
            if t != -1:
                f852x428 = line[pos + 8:pos + 16 + 8]
                print(str(l852x428)+" "+f852x428)
            t = line.find(l1920x1080)
            if t != -1:
                f1920x1080 = line[pos + 8:pos + 16 + 8]
                print(str(l1920x1080) + " " + f1920x1080)
            if t != -1:
                f1280x720 = line[pos + 8:pos + 16 + 8]
                print(str(l1280x720) + " " + f1280x720)
            if t != -1:
                f640x360 = line[pos + 8:pos + 16 + 8]
                print(str(l640x360) + " " + f640x360)

    video_id = urlparse(data["preroll"]['url']).query.replace("episode_id=", "")

    if (video_id is None) or (video_id == ""):
        print("Wrong data")
        sys.exit()

    with open("f:\\thehole\\"+title+'.ts', 'wb') as merged:
        while True:

            fn = str(counter)
            for i in range(len(str(counter)), 9):
                fn = "0" + fn
            fn = fn + ".ts"

            url = "https://video-cdn.the-hole.tv/episodes/"+video_id+"/segment-"+str(counter)+"-"+f640x360+".ts"

            t = requests.head(url)

            if t.status_code == 200:
                # if parts_count >= max_count:
                if False:
                    print(str(parts_count) + " Finish")
                    print(str(round(total, 2)) + " MB")
                    break

                urllib.request.urlretrieve(url, fn)

                with open(fn, 'rb') as mergefile:
                    shutil.copyfileobj(mergefile, merged)

                tmp_size = os.path.getsize(fn)/1048576
                if os.path.exists(fn):
                    os.remove(fn)
                print(str(parts_count) + " - " + fn + " - " + str(round(tmp_size, 2)))
                total += tmp_size
            else:
                print(str(parts_count) + " Finish")
                print(str(round(total, 2)) + " MB")
                break
            parts_count += 1
            counter += 1
