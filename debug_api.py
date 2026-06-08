import urllib.request, urllib.error, json
import sepehr_api

candidates = [
    "/epg/livechannel", "/epg/channel", "/epg/channels",
    "/epg/channellist", "/epg/livechannels", "/channel/live",
    "/channel/list", "/live/channels", "/epg/tvchannel", "/epg/livetv",
]

for path in candidates:
    url = sepehr_api.API_BASE + path
    auth = sepehr_api.build_oauth_header("GET", url)
    headers = dict(sepehr_api.DEFAULT_HEADERS)
    headers["Authorization"] = auth
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        r = urllib.request.urlopen(req, timeout=15)
        body = r.read().decode("utf-8", errors="ignore")
        print(f"OK {path} -> {r.status}")
        print(f"   {body[:500]}")
        print()
    except urllib.error.HTTPError as e:
        print(f"   {path} -> HTTP {e.code}")
    except Exception as e:
        print(f"   {path} -> {type(e).__name__}")
