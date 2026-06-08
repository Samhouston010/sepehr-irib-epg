import urllib.request, urllib.error, json, datetime
import sepehr_api

today = datetime.date.today().strftime("%Y-%m-%d")

print("=== TV2 (channel_id=32) programs on different days ===")
for d in [today, "2026-06-09", "2026-06-10"]:
    url = sepehr_api.API_BASE + f"/epg/tvprogram?channel_id=32&date={d}"
    auth = sepehr_api.build_oauth_header("GET", url)
    headers = dict(sepehr_api.DEFAULT_HEADERS); headers["Authorization"] = auth
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12)
        data = json.loads(r.read().decode("utf-8"))
        items = data.get("list", [])
        real = [it for it in items if it.get("title") and " - " not in it.get("title","")[:8]]
        print(f"  {d}: total={len(items)} real={len(real)}")
        for it in items[:4]:
            print(f"      {it.get('title')}")
    except Exception as e:
        print(f"  {d}: {type(e).__name__}")

print("\n=== telewebion API test ===")
for u in [
    "https://gateway.telewebion.com/kandao/v1.0/epg?channel=tv2",
    "https://ws.telewebion.com/services/getEPGByChannel?channel=tv2",
    "https://api.telewebion.com/v1.0/epg/tv2",
]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=10)
        print(f"OK {r.status} | {u}")
        print(f"   {r.read()[:200]}")
    except urllib.error.HTTPError as e:
        print(f"   HTTP {e.code} | {u}")
    except Exception as e:
        print(f"   {type(e).__name__} | {u}")
