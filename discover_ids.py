#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
discover_ids.py — کشف channel_id درست هر کانال سپهر
====================================================
آیدی‌های ۱ تا ۱۲۰ را امتحان می‌کند. برای هر آیدی که برنامه برگرداند،
نام اولین برنامه و channelId را نشان می‌دهد تا channels.json را دقیق کنیم.
"""

import json
import time
import datetime
import sepehr_api


def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"کشف آیدی کانال‌ها برای تاریخ {today}\n")

    found = {}
    for cid in range(1, 121):
        try:
            resp = sepehr_api.get_tvprogram(cid, today)
        except Exception as e:
            if "401" in str(e):
                print(f"  ⚠️  id={cid}: خطای احراز هویت — {e}")
                break
            continue

        items = resp.get("list", []) if isinstance(resp, dict) else []
        if items:
            # نام چند برنامه برای شناسایی کانال
            titles = [it.get("title", "") for it in items[:3] if isinstance(it, dict)]
            ch_id = items[0].get("channelId") if isinstance(items[0], dict) else None
            sample = " / ".join(t for t in titles if t)
            print(f"✅ id={cid} (channelId={ch_id}): {len(items)} برنامه | {sample}")
            found[cid] = {
                "count": len(items),
                "channelId": ch_id,
                "samples": titles,
            }
        time.sleep(0.25)

    print(f"\n📊 {len(found)} کانال فعال پیدا شد")
    with open("discovered_ids.json", "w", encoding="utf-8") as f:
        json.dump(found, f, ensure_ascii=False, indent=2)
    print("✅ در discovered_ids.json ذخیره شد")


if __name__ == "__main__":
    main()
