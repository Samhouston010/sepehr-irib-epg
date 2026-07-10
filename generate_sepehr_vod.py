"""Generate sepehr_vod.m3u from Sepehr's on-demand (VOD) catalog.

Streams are token-signed and short-lived, so entries point at a small
Cloudflare Worker (sepehr-vod-proxy) that re-resolves a fresh URL per play.
"""
import json
from pathlib import Path
from requests_oauthlib import OAuth1
import requests

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
PROXY_BASE = "https://sepehr-vod-proxy.samhouston010.workers.dev"
GROUP = "🎬 سپهر VOD"  # single group -- one folder in the playlist, category kept as a title prefix

# id -> Persian name, from vod/categories/5 (skip id 1572 "تازه‌ها", it's a rolling
# duplicate of everything else already covered by ID_DESC ordering per category)
CATEGORIES = {
    67: "فیلم سینمایی",
    110: "سریال",
    350: "کودک و نوجوان",
    433: "مرکز صدا و سیما",
    602: "سپهر رسانه",
    612: "مذهبی",
    737: "مناسبتی",
    762: "ورزشی",
    843: "مستند",
    901: "سلامت و پزشکی",
    1027: "خانواده",
    1030: "مسابقات و سرگرمی",
    1074: "کلام بزرگان",
    1051: "شبکه‌های اختصاصی",
    1039: "نماهنگ",
    1048: "آموزشی",
}

# Category 67 (فیلم سینمایی) is pulled in FULL per user request; everything else stays
# capped at the newest 50 -- 24k items across all 16 categories is too much for a
# personal playlist, but "every movie" is a reasonable, bounded ask (621 items).
FULL_CATEGORIES = {67}
PAGES_PER_CATEGORY = 2  # ponytail: newest N pages only for capped categories
PAGE_SIZE = 25
FULL_PAGE_SIZE = 100  # fewer requests when pulling an entire category

auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")


def fetch_category(cat_id):
    full = cat_id in FULL_CATEGORIES
    page_size = FULL_PAGE_SIZE if full else PAGE_SIZE
    max_pages = 999 if full else PAGES_PER_CATEGORY
    items = []
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(
                f"{API_BASE}/vod/get",
                params={"category_id": cat_id, "page": page, "page_size": page_size, "order_types": "ID_DESC"},
                auth=auth, timeout=20,
            )
            if r.status_code != 200:
                break
            lst = r.json().get("list") or []
            if not lst:
                break
            items.extend(lst)
            if len(lst) < page_size:
                break  # last page
        except Exception as e:
            print(f"  page {page} error: {e}")
            break
    return items


def _e(s):
    return str(s or "").replace('"', "'").strip()


def main():
    lines = ["#EXTM3U"]
    total = 0
    seen_ids = set()  # a title can be listed under more than one category upstream
    for cat_id, name_fa in CATEGORIES.items():
        items = fetch_category(cat_id)
        print(f"{name_fa} ({cat_id}): {len(items)} items")
        for it in items:
            vid = it.get("id")
            title = _e(it.get("title"))
            if not vid or not title or vid in seen_ids:
                continue
            seen_ids.add(vid)
            poster = it.get("poster") or ""
            lines.append(
                f'#EXTINF:-1 tvg-logo="{poster}" group-title="{GROUP}",[{name_fa}] {title}'
            )
            lines.append(f"{PROXY_BASE}/play/{vid}")
            total += 1
    Path("sepehr_vod.m3u").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Total: {total} VOD entries written to sepehr_vod.m3u")


if __name__ == "__main__":
    main()
