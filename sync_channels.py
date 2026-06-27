"""
sync_channels.py — auto-discover new Telewebion channels + remove dead ones
Runs weekly via GitHub Actions. Updates channels.json in-place.
"""
import json, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

STREAM = "https://ncdn.telewebion.ir/{slug}/live/playlist.m3u8"
TW_LOGO = "https://static.televebion.net/web/content_images/channel_images/thumbs/new/240/v4/{slug}.png"

# Master list of all known + candidate slugs to probe
KNOWN_SLUGS = [
    # سراسری
    "tv1","tv2","tv3","tv4","tehran","ofogh","amouzesh","faratar","tv1plus","tamasha",
    # خبری
    "irinn","irinn2",
    # ورزشی
    "varzesh","sport1","sport2","sport3",
    # سرگرمی
    "nasim","namayesh","ifilm","omid","sepehr","golkhane","habib",
    # مستند
    "mostanad",
    # کودک
    "pooya",
    # مذهبی
    "quran","noor","kawthar","velayat","labbayk","tekyemadahi",
    # سلامت
    "salamat",
    # بین‌المللی
    "alalam","palestine","presstv",
    # استانی
    "abadan","aflak","aftab","alborz","ara","atrak","azarbayjangharbi","baran",
    "bushehr","dena","eshragh","esfahan","fars","hamoon","ilam","iraneman",
    "jahanbin","karoon","kerman","khalijefars","khavaran","khoosetan","khorasanrazavi",
    "kish","kordestan","mahabad","makran","nesfejahan","qazvin","sabalan","sahand",
    "sarbedaran","sabz","semnan","sina","taban","tabarestan","zagros","zaferan",
    "iribu","khoozestan",
    # احتمالی (probe only)
    "sport4","sport5","tv5","documentary","cinema","iran","hd1","hd2",
    "music","radio","comedy","kids","nature","history",
]

GROUPS = {
    "tv1plus":"سراسری","tamasha":"سرگرمی","sport1":"ورزشی","sport2":"ورزشی","sport3":"ورزشی",
    "noor":"مذهبی","kawthar":"مذهبی","velayat":"مذهبی","labbayk":"مذهبی","habib":"مذهبی",
    "tekyemadahi":"مذهبی","alalam":"بین‌المللی","palestine":"بین‌المللی","presstv":"بین‌المللی",
    "golkhane":"سرگرمی","sabz":"استانی","makran":"استانی","zaferan":"استانی",
}
NAMES_FA = {
    "tv1plus":"مثبت یک","sport1":"تلوبیون اسپرت ۱","sport2":"تلوبیون اسپرت ۲",
    "sport3":"تلوبیون اسپرت ۳","noor":"نور","kawthar":"الکوثر","velayat":"ولایت",
    "labbayk":"لبیک","habib":"حبیب","tekyemadahi":"تکیه مداحی","alalam":"العالم",
    "palestine":"فلسطین","golkhane":"گلخانه","sabz":"گلستان","makran":"مکران",
    "zaferan":"زعفران","presstv":"پرس تی وی",
}

def probe(slug):
    # ncdn.telewebion.ir returns 302 → Akamai CDN; use GET with small range to avoid full download
    url = STREAM.format(slug=slug)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Range": "bytes=0-0",
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            return slug, r.status in (200, 206, 302)
    except urllib.error.HTTPError as e:
        # 416 Range Not Satisfiable still means the URL exists
        return slug, e.code in (200, 206, 302, 416)
    except Exception:
        return slug, False

def main():
    ch_path = Path("channels.json")
    channels = json.loads(ch_path.read_text(encoding="utf-8"))
    existing = {c["slug"]: c for c in channels}
    print(f"Existing: {len(existing)} channels")

    # Probe all candidates in parallel
    all_slugs = list(set(KNOWN_SLUGS) | set(existing.keys()))
    results = {}
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(probe, s): s for s in all_slugs}
        for f in as_completed(futures):
            slug, ok = f.result()
            results[slug] = ok

    alive = {s for s, ok in results.items() if ok}
    dead  = {s for s, ok in results.items() if not ok}
    print(f"Alive: {len(alive)}  Dead: {len(dead)}")

    new_channels = []
    for ch in channels:
        if ch["slug"] in alive:
            new_channels.append(ch)
        else:
            print(f"  REMOVED (dead): {ch['name']} ({ch['slug']})")

    added = 0
    for slug in sorted(alive - set(existing.keys())):
        ch = {
            "slug": slug,
            "channel_id": None,
            "tvg_id": "",
            "name": NAMES_FA.get(slug, slug),
            "name_en": slug,
            "group": GROUPS.get(slug, "استانی"),
            "logo": TW_LOGO.format(slug=slug),
        }
        new_channels.append(ch)
        print(f"  ADDED: {ch['name']} ({slug})")
        added += 1

    ch_path.write_text(json.dumps(new_channels, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done: {len(new_channels)} channels total (+{added} added)")

if __name__ == "__main__":
    main()
