#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug_api.py — تست خام API سپهر برای تشخیص مشکل"""
import urllib.request, urllib.error, json, datetime
import sepehr_api

today = datetime.date.today().strftime("%Y-%m-%d")
print(f"=== تست API سپهر برای channel_id=31 تاریخ {today} ===\n")

# 1) تست با OAuth (کلید اندروید)
url = sepehr_api.API_BASE + "/epg/tvprogram?channel_id=31&date=" + today
print(f"URL: {url}\n")
auth = sepehr_api.build_oauth_header("GET", url)
print(f"Authorization header:\n{auth}\n")

headers = dict(sepehr_api.DEFAULT_HEADERS)
headers["Authorization"] = auth
req = urllib.request.Request(url, headers=headers, method="GET")
try:
    r = urllib.request.urlopen(req, timeout=20)
    raw = r.read()
    print(f"✅ STATUS: {r.status}")
    print(f"RESPONSE (first 800 chars):\n{raw.decode('utf-8', errors='ignore')[:800]}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='ignore')
    print(f"❌ HTTP {e.code}")
    print(f"BODY (first 800 chars):\n{body[:800]}")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")

# 2) تست بدون OAuth (ببینیم چه خطایی میده)
print("\n=== تست بدون احراز هویت ===")
req2 = urllib.request.Request(url, headers=sepehr_api.DEFAULT_HEADERS, method="GET")
try:
    r2 = urllib.request.urlopen(req2, timeout=20)
    print(f"STATUS: {r2.status}")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode('utf-8',errors='ignore')[:300]}")
except Exception as e:
    print(f"ERROR: {e}")
