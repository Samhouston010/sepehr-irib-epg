#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate.py — تولیدکننده M3U و EPG شبکه‌های صداوسیما (سپهر / تلوبیون)
====================================================================
خروجی:
  sepehr.m3u       لیست پخش با لینک مستقیم CDN تلوبیون
  sepehr.xml       راهنمای برنامه (XMLTV)
  sepehr.xml.gz    نسخه فشرده برای IPTV player ها

روی GitHub Actions هر ۶ ساعت اجرا می‌شود.
"""

import json
import gzip
import time
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

import sepehr_api

# CDN مستقیم تلوبیون (لینک ثابت، بدون توکن)
CDN_BASE = "https://ncdn.telewebion.ir/{slug}/live/playlist.m3u8"

REPO = "Samhouston010/sepehr-irib-epg"
EPG_URL = f"https://raw.githubusercontent.com/{REPO}/main/sepehr.xml.gz"

EPG_DAYS = 3           # امروز + ۲ روز آینده
TEHRAN_OFFSET = "+0330"


def load_channels():
    with open("channels.json", "r", encoding="utf-8-sig") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# M3U
# ---------------------------------------------------------------------------
def build_m3u(channels):
    lines = [f'#EXTM3U x-tvg-url="{EPG_URL}"']
    for ch in channels:
        stream = CDN_BASE.format(slug=ch["slug"])
        logo = ch.get("logo", "")
        lines.append(
            f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-name="{ch["name"]}" '
            f'tvg-logo="{logo}" group-title="{ch.get("group","ایران")}",{ch["name"]}'
        )
        lines.append(stream)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# کمک‌کننده زمان
# ---------------------------------------------------------------------------
def parse_dt(value):
    """انواع فرمت زمانی که سپهر ممکن است برگرداند را تجزیه می‌کند."""
    if value is None:
        return None
    # عدد یونیکس (ثانیه یا میلی‌ثانیه)
    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 1e12:   # میلی‌ثانیه
            ts /= 1000.0
        return datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=3, minutes=30)
    s = str(value).strip()
    if s.isdigit():
        return parse_dt(int(s))
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M", "%H:%M:%S", "%H:%M"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt
        except ValueError:
            continue
    return None


def xmltv_time(dt):
    if dt is None:
        return None
    return dt.strftime("%Y%m%d%H%M%S") + " " + TEHRAN_OFFSET


def extract_programs(api_response, date_str):
    """
    از پاسخ API سپهر، لیست برنامه‌ها را بیرون می‌کشد.

    ساختار واقعی پاسخ سپهر:
      {"list": [
         {"id":..., "title":"...", "start": 1780864199000,  # میلی‌ثانیه یونیکس
          "duration": 120,                                   # دقیقه
          "channelId": 31, "descSummary": "...", "descFull": null, ...},
         ...
      ]}
    پایان برنامه = start + duration دقیقه (فیلد end جداگانه ندارد).
    """
    if not api_response:
        return []

    items = None
    if isinstance(api_response, list):
        items = api_response
    elif isinstance(api_response, dict):
        for key in ("list", "data", "result", "results", "items", "programs", "epg"):
            if key in api_response and isinstance(api_response[key], list):
                items = api_response[key]
                break
    if items is None:
        items = []

    programs = []
    for it in items:
        if not isinstance(it, dict):
            continue
        title = (it.get("title") or it.get("name") or "برنامه")
        desc = (it.get("descFull") or it.get("descSummary")
                or it.get("description") or it.get("desc") or "")

        start = parse_dt(it.get("start"))
        if not start:
            continue

        # پایان = شروع + مدت (دقیقه)
        end = None
        dur = it.get("duration")
        if dur is not None:
            try:
                end = start + datetime.timedelta(minutes=float(dur))
            except (TypeError, ValueError):
                end = None

        programs.append({"title": title, "desc": desc, "start": start, "end": end})
    return programs


# ---------------------------------------------------------------------------
# XMLTV
# ---------------------------------------------------------------------------
def build_xmltv(channels, epg_data):
    tv = ET.Element("tv", attrib={
        "generator-info-name": "Sepehr-IRIB-EPG",
        "source-info-name": "Sepehr / Telewebion",
    })
    for ch in channels:
        c = ET.SubElement(tv, "channel", attrib={"id": ch["tvg_id"] or ch["slug"]})
        dn = ET.SubElement(c, "display-name", attrib={"lang": "fa"})
        dn.text = ch["name"]
        if ch.get("name_en"):
            dn2 = ET.SubElement(c, "display-name", attrib={"lang": "en"})
            dn2.text = ch["name_en"]
        if ch.get("logo"):
            ET.SubElement(c, "icon", attrib={"src": ch["logo"]})

    total = 0
    for ch in channels:
        cid = ch["tvg_id"] or ch["slug"]
        for p in epg_data.get(cid, []):
            start = xmltv_time(p["start"])
            if not start:
                continue
            attrib = {"start": start, "channel": cid}
            stop = xmltv_time(p["end"])
            if stop:
                attrib["stop"] = stop
            prog = ET.SubElement(tv, "programme", attrib=attrib)
            t = ET.SubElement(prog, "title", attrib={"lang": "fa"})
            t.text = p["title"]
            if p.get("desc"):
                d = ET.SubElement(prog, "desc", attrib={"lang": "fa"})
                d.text = p["desc"]
            total += 1

    print(f"\n📺 مجموع برنامه‌ها: {total}")
    rough = ET.tostring(tv, encoding="utf-8")
    return minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")


# ---------------------------------------------------------------------------
# اصلی
# ---------------------------------------------------------------------------
def main():
    channels = load_channels()
    print(f"✅ {len(channels)} کانال بارگذاری شد")

    # M3U
    with open("sepehr.m3u", "w", encoding="utf-8") as f:
        f.write(build_m3u(channels))
    print("✅ sepehr.m3u ساخته شد")

    # تاریخ‌ها
    today = datetime.date.today()
    dates = [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
             for i in range(EPG_DAYS)]

    epg_data = {}
    ok_channels = 0
    for ch in channels:
        cid = ch["tvg_id"] or ch["slug"]
        epg_data[cid] = []
        got_any = False
        for d in dates:
            try:
                resp = sepehr_api.get_tvprogram(ch["channel_id"], d)
                progs = extract_programs(resp, d)
                epg_data[cid].extend(progs)
                if progs:
                    got_any = True
            except Exception as e:
                print(f"  ⚠️  {ch['name']} {d}: {e}")
            time.sleep(0.4)
        status = "✅" if got_any else "—"
        print(f"{status} {ch['name']}: {len(epg_data[cid])} برنامه")
        if got_any:
            ok_channels += 1

    print(f"\n📊 {ok_channels}/{len(channels)} کانال EPG دارند")

    xml_bytes = build_xmltv(channels, epg_data)
    with open("sepehr.xml", "wb") as f:
        f.write(xml_bytes)
    with gzip.open("sepehr.xml.gz", "wb") as f:
        f.write(xml_bytes)
    print("✅ sepehr.xml و sepehr.xml.gz ساخته شد")


if __name__ == "__main__":
    main()
