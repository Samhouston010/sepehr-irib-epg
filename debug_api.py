import urllib.request, urllib.error, json, datetime
import sepehr_api
today = datetime.date.today().strftime("%Y-%m-%d")

def fetch(path):
    url = sepehr_api.API_BASE + path
    auth = sepehr_api.build_oauth_header("GET", url)
    headers = dict(sepehr_api.DEFAULT_HEADERS); headers["Authorization"] = auth
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=12)
        return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"_error": str(e)[:60]}

print("=== which channel_id has real programs? scan 30-55 ===")
for cid in range(30, 56):
    d = fetch(f"/epg/tvprogram?channel_id={cid}&date={today}")
    items = d.get("list", []) if "_error" not in d else []
    real = [it for it in items if it.get("title") and " - " not in it.get("title","")[:8]]
    if real:
        print(f"  cid={cid}: {len(real)} real | {real[0]['title']} / {real[1]['title'] if len(real)>1 else ''}")
