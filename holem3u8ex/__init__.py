import sys

# Die
import requests


def die(mes):
    if mes is not None:
        print(mes)
    input("Press Enter to exit")
    sys.exit(-1)


def get_max_segment(vid, r_url):
    m3file = None
    cnt = 0
    ur = "https://video-cdn.the-hole.tv/episodes/" + vid + "/iframes-" + r_url + ".m3u8"
    try:
        m3file = requests.get(ur)
    except ImportError:
        die("Can't load m3u8_file")
    lns = str(m3file.text)
    for ln in reversed(lns.splitlines()):
        if ln.find("segment-") != -1:
            ln = ln.replace("segment-", "")
            ln = ln.replace(".ts", "")
            ln = ln.replace(r_url, "")
            ln = ln.replace("-", "")
            cnt = int(ln)
            break
    return cnt
