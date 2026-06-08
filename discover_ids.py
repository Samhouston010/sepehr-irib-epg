#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
discover_ids.py — کشف channel_id درست هر کانال
================================================
چون فقط می‌دانیم شبکه یک = ۳۱، این اسکریپت آیدی‌های ۱ تا ۱۲۰ را
امتحان می‌کند و برای هرکدام که برنامه برگرداند، نام کانال را نشان می‌دهد.

با خروجی این اسکریپت می‌توانیم channels.json را دقیق کنیم.

روی GitHub Actions اجرا کنید (چون از خارج ایران به API دسترسی ندارید مگر
IP دیتاسنتر مجاز باشد).
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
            # 404/401 یعنی این آیدی وجود ندارد یا مشکل auth
            if "401" in str(e):
                print(f"  ⚠️  id={cid}: خطای احراز هویت — {e}")
                break
            continue

        # تلاش برای یافتن نام کانال و تعداد برنامه‌ها
        items = []
        ch_name = ""
        if isinstance(resp, dict):
            for k in ("data", "result", "items", "programs"):
                if isinstance(resp.get(k), list):
                    items = resp[k]
                    break
            ch_name = (resp.get("channel_name") or resp.get("channel")
                       or resp.get("channelTitle") or "")
        elif isinstance(resp, list):
            items = resp

        if items:
            # نام اولین برنامه برای کمک به شناسایی
            first = items[0] if isinstance(items[0], dict) else {}
            sample = first.get("title") or first.get("name") or ""
            print(f"✅ id={cid}: {len(items)} برنامه | کانال={ch_name} | نمونه='{sample}'")
            found[cid] = {"count": len(items), "channel": ch_name, "sample": sample}
        time.sleep(0.3)

    print(f"\n📊 {len(found)} کانال فعال پیدا شد")
    with open("discovered_ids.json", "w", encoding="utf-8") as f:
        json.dump(found, f, ensure_ascii=False, indent=2)
    print("✅ در discovered_ids.json ذخیره شد")


if __name__ == "__main__":
    main()
