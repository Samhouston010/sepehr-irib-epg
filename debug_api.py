import urllib.request, urllib.error, json, datetime
import sepehr_api

today = datetime.date.today().strftime("%Y-%m-%d")
print(f"=== test channel_id=31 date {today} ===\n")

url = sepehr_api.API_BASE + "/epg/tvprogram?channel_id=31&date=" + today
print(f"URL: {url}\n")
auth = sepehr_api.build_oauth_header("GET", url)
print(f"Authorization:\n{auth}\n")

headers = dict(sepehr_api.DEFAULT_HEADERS)
headers["Authorization"] = auth
req = urllib.request.Request(url, headers=headers, method="GET")
try:
    r = urllib.request.urlopen(req, timeout=20)
    raw = r.read()
    print(f"OK STATUS: {r.status}")
    print(raw.decode("utf-8", errors="ignore")[:800])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}")
    print(e.read().decode("utf-8", errors="ignore")[:800])
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
