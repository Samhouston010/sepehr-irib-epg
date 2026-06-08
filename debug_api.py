import urllib.request, urllib.error, re

channels = ["IRIBTV1","IRIBTV2","IRIBTV3","IRIBTV4","IRIBTV5","IRIBNews",
            "IRIBNasim","IRIBVarzesh","IRIBMostanad","IRIBAmoozesh","IRIBSalamat",
            "IRIBPooya","IRIBTamasha","IRIBNamayesh","IRIBiFilm"]

total = 0
for ch in channels:
    url = f"https://epg.pw/xmltv/ir/{ch}.xml"
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=15)
        data = r.read().decode("utf-8", errors="ignore")
        progs = data.count("<programme")
        if progs:
            total += 1
            titles = re.findall(r"<title[^>]*>([^<]+)</title>", data)[:2]
            print(f"OK {ch}: {progs} programs | {titles}")
        else:
            print(f"-- {ch}: 0 programs")
    except urllib.error.HTTPError as e:
        print(f"FAIL {ch}: HTTP {e.code}")
    except Exception as e:
        print(f"FAIL {ch}: {type(e).__name__}")

print(f"\nTOTAL: {total}/{len(channels)} channels have programs")
