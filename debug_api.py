import urllib.request, urllib.error, json, datetime, time
import sepehr_api

today = datetime.date.today().strftime("%Y-%m-%d")
active = [31,32,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,
          55,56,57,58,59,60,61,63,64,65,66,67,68,69,70,72]

print(f"fingerprint date {today}:\n")
for cid in active:
    url = sepehr_api.API_BASE + f"/epg/tvprogram?channel_id={cid}&date={today}"
    auth = sepehr_api.build_oauth_header("GET", url)
    headers = dict(sepehr_api.DEFAULT_HEADERS); headers["Authorization"] = auth
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12)
        data = json.loads(r.read().decode("utf-8"))
        items = data.get("list", [])
        titles = []
        for it in items:
            t = it.get("title","")
            if t and " - " not in t[:8] and t not in titles:
                titles.append(t)
        fp = " | ".join(titles[:6]) if titles else "(only empty slots)"
        print(f"id={cid}: {fp}")
    except Exception as e:
        print(f"id={cid}: error {type(e).__name__}")
    time.sleep(0.2)
