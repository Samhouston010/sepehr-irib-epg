import urllib.request, urllib.error

logos = {
    "wikimedia": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/IRIBTV1.svg/960px-IRIBTV1.svg.png",
    "televebion_net": "https://static.televebion.net/web/content_images/channel_images/thumbs/new/240/v4/tv1.png",
    "telewebion_com": "https://static.telewebion.com/web/content_images/channel_images/thumbs/new/240/v4/tv1.png",
}
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
for name, url in logos.items():
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua}), timeout=12)
        ct = r.headers.get("Content-Type","")
        size = len(r.read())
        print(f"OK {name}: {r.status} | {ct} | {size} bytes")
    except urllib.error.HTTPError as e:
        print(f"FAIL {name}: HTTP {e.code}")
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__}")
