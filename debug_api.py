import urllib.request, urllib.error, json, datetime
import sepehr_api

today = datetime.date.today().strftime("%Y-%m-%d")
for cid in [31, 39, 40, 54]:
    url = sepehr_api.API_BASE + f"/epg/tvprogram?channel_id={cid}&date={today}&include_details=true"
    auth = sepehr_api.build_oauth_header("GET", url)
    headers = dict(sepehr_api.DEFAULT_HEADERS); headers["Authorization"] = auth
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12)
        data = json.loads(r.read().decode("utf-8"))
        items = data.get("list", [])
        imgs = set()
        for it in items:
            if it.get("imageUrl"): imgs.add(it["imageUrl"])
            m = it.get("media") or {}
            if m.get("logo"): imgs.add("LOGO:" + str(m["logo"]))
            if m.get("preview"): imgs.add("PREVIEW:" + str(m["preview"]))
        print(f"id={cid}: {list(imgs)[:3] if imgs else 'no image'}")
    except Exception as e:
        print(f"id={cid}: {type(e).__name__}")

print("\n=== logo url test ===")
for u in [
    "https://sepehrtv.ir/_next/static/media/tv1.png",
    "https://cdnt.telewebion.com/teleicon/tv1.png",
    "https://static.telewebion.com/teleicon/tv1.png",
]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=8)
        print(f"OK {r.status} | {u}")
    except urllib.error.HTTPError as e:
        print(f"   {e.code} | {u}")
    except Exception as e:
        print(f"   {type(e).__name__} | {u}")
