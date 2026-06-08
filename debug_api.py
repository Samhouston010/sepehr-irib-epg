import urllib.request, urllib.error, json, datetime, time
import sepehr_api

today = datetime.date.today().strftime("%Y-%m-%d")

print("=== full media for a program (TV1) ===")
url = sepehr_api.API_BASE + f"/epg/tvprogram?channel_id=31&date={today}&include_media_resources=true"
auth = sepehr_api.build_oauth_header("GET", url)
headers = dict(sepehr_api.DEFAULT_HEADERS); headers["Authorization"] = auth
try:
    r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15)
    data = json.loads(r.read().decode("utf-8"))
    items = data.get("list", [])
    for it in items:
        m = it.get("media") or {}
        if m.get("streams") or m.get("logo") or m.get("preview"):
            print(json.dumps(it, ensure_ascii=False, indent=2)[:800])
            break
    else:
        print("no full media. last item:")
        if items:
            print(json.dumps(items[-1], ensure_ascii=False, indent=2)[:600])
except Exception as e:
    print(f"error: {e}")

print("\n=== telewebion CDN quality test (TV1) ===")
variants = [
    "https://ncdn.telewebion.ir/tv1/live/playlist.m3u8",
    "https://ncdn.telewebion.ir/tv1/live/1080p/playlist.m3u8",
    "https://ncdn.telewebion.ir/tv1/live/720p/playlist.m3u8",
    "https://ncdn.telewebion.ir/tv1/live/index.m3u8",
]
for v in variants:
    try:
        req = urllib.request.Request(v, headers={"User-Agent": "Mozilla/5.0"})
        r = urllib.request.urlopen(req, timeout=10)
        body = r.read().decode("utf-8", errors="ignore")
        qualities = [l for l in body.split("\n") if "RESOLUTION" in l or "BANDWIDTH" in l]
        print(f"OK {v.split('/live/')[1]} -> {r.status}")
        for q in qualities[:6]:
            print(f"    {q.strip()[:90]}")
    except urllib.error.HTTPError as e:
        print(f"   {v.split('/live/')[1]} -> {e.code}")
    except Exception as e:
        print(f"   {v.split('/live/')[1]} -> {type(e).__name__}")
