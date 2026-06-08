import json, gzip, requests, argparse
from requests_oauthlib import OAuth1
from datetime import datetime, timezone, timedelta
from pathlib import Path

API_BASE        = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY    = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
EPG_URL         = "https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz"
STREAM          = "https://ncdn.telewebion.ir/{slug}/live/playlist.m3u8"

def load_channels():
    with open("channels.json", encoding="utf-8-sig") as f:
        return json.load(f)

def build_m3u(channels):
    lines = [f'#EXTM3U x-tvg-url="{EPG_URL}"']
    for ch in channels:
        lines.append(f'#EXTINF:-1 tvg-id="{ch.get("tvg_id","")}" tvg-name="{ch["name"]}" tvg-logo="{ch.get("logo","")}" group-title="{ch["group"]}",{ch["name"]}')
        lines.append(STREAM.format(slug=ch["slug"]))
    return "\n".join(lines)

def fetch_epg(channels):
    auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")
    programs = []
    today = datetime.now(timezone.utc)
    epg_channels = [c for c in channels if c.get("channel_id")]
    for i, ch in enumerate(epg_channels):
        ch_total = 0
        print(f"[{i+1}/{len(epg_channels)}] {ch['name']}...", end=" ", flush=True)
        for day_offset in range(3):
            date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            try:
                r = requests.get(f"{API_BASE}/epg/tvprogram", params={"channel_id": ch["channel_id"], "date": date}, auth=auth, timeout=15)
                if r.status_code != 200:
                    continue
                for prog in (r.json().get("list") or []):
                    start_dt = datetime.fromtimestamp(prog.get("start",0)/1000, tz=timezone.utc)
                    end_dt = start_dt + timedelta(minutes=prog.get("duration") or 30)
                    programs.append({"channel": ch["tvg_id"], "start": start_dt.strftime("%Y%m%d%H%M%S +0000"), "stop": end_dt.strftime("%Y%m%d%H%M%S +0000"), "title": prog.get("title") or "برنامه", "desc": prog.get("descSummary") or ""})
                    ch_total += 1
            except Exception as e:
                print(f"error {date}: {e}", end=" ")
        print(f"{ch_total} programs")
    return programs

def _e(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def build_xml(channels, programs):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv>']
    for ch in channels:
        lines.append(f'  <channel id="{_e(ch.get("tvg_id",""))}"><display-name lang="fa">{_e(ch["name"])}</display-name>')
        if ch.get("logo"):
            lines.append(f'    <icon src="{_e(ch["logo"])}"/>')
        lines.append('  </channel>')
    for p in programs:
        lines.append(f'  <programme start="{p["start"]}" stop="{p["stop"]}" channel="{_e(p["channel"])}"><title lang="fa">{_e(p["title"])}</title>')
        if p.get("desc"):
            lines.append(f'    <desc lang="fa">{_e(p["desc"])}</desc>')
        lines.append('  </programme>')
    lines.append('</tv>')
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--m3u", action="store_true")
    parser.add_argument("--epg", action="store_true")
    args = parser.parse_args()
    do_m3u = args.m3u or not (args.m3u or args.epg)
    do_epg = args.epg or not (args.m3u or args.epg)
    channels = load_channels()
    print(f"Loaded {len(channels)} channels")
    if do_m3u:
        m3u = build_m3u(channels)
        Path("sepehr.m3u").write_text(m3u, encoding="utf-8")
        print(f"M3U: {m3u.count('#EXTINF')} channels written")
    if do_epg:
        print(f"Fetching EPG for {sum(1 for c in channels if c.get('channel_id'))} channels...")
        programs = fetch_epg(channels)
        print(f"Total: {len(programs)} programs")
        xml = build_xml(channels, programs)
        Path("sepehr.xml").write_text(xml, encoding="utf-8")
        with gzip.open("sepehr.xml.gz", "wb") as f:
            f.write(xml.encode("utf-8"))
        print("sepehr.xml + sepehr.xml.gz written")
    print("Done!")

if __name__ == "__main__":
    main()
