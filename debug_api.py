import urllib.request, urllib.error, json
endpoints = [
    "https://gateway.telewebion.com/v1.0/getEPG?ChannelDescriptor=tv1",
    "https://gw.telewebion.com/api/getEPG?channel=tv1",
    "https://api.telewebion.com/api/v1/channels/tv1/epg",
    "https://ws.telewebion.com/api/v1/epg?channel=tv1",
    "https://servicesapi.telewebion.com/api/v1/epg/tv1",
    "https://gateway.telewebion.com/getEPG/tv1",
    "https://ncdn.telewebion.ir/tv1/epg.json",
]
for u in endpoints:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=10)
        body = r.read().decode("utf-8", errors="ignore")
        print(f"OK {r.status} | {u}")
        print(f"   {body[:200]}")
    except urllib.error.HTTPError as e:
        print(f"   HTTP {e.code} | {u}")
    except Exception as e:
        print(f"   {type(e).__name__} | {u}")
