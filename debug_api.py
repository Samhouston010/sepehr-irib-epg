import urllib.request, urllib.error, json
import sepehr_api

print("=== top-level structure tvprogram channel_id=31 ===")
url = sepehr_api.API_BASE + "/epg/tvprogram?channel_id=31&date=2026-06-08"
auth = sepehr_api.build_oauth_header("GET", url)
headers = dict(sepehr_api.DEFAULT_HEADERS); headers["Authorization"] = auth
try:
    r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15)
    data = json.loads(r.read().decode("utf-8"))
    if isinstance(data, dict):
        print("top keys:", list(data.keys()))
        for k, v in data.items():
            if k != "list":
                print(f"  {k} = {v}")
        if data.get("list"):
            print("\nsample program:")
            print(json.dumps(data["list"][0], ensure_ascii=False, indent=2))
except Exception as e:
    print(f"error: {e}")

print("\n=== channel-info endpoints ===")
for path in ["/epg/channelinfo?channel_id=31", "/channel/31", "/epg/channel/31",
             "/channel?id=31", "/epg/channel?channel_id=31", "/channels",
             "/epg", "/livestream", "/epg/live"]:
    url = sepehr_api.API_BASE + path
    auth = sepehr_api.build_oauth_header("GET", url)
    headers = dict(sepehr_api.DEFAULT_HEADERS); headers["Authorization"] = auth
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12)
        body = r.read().decode("utf-8", errors="ignore")
        print(f"OK {path} -> 200 | {body[:300]}")
    except urllib.error.HTTPError as e:
        print(f"   {path} -> {e.code}")
    except Exception as e:
        print(f"   {path} -> {type(e).__name__}")
