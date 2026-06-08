#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sepehr_api.py — کلاینت API سپهر (صداوسیما) با احراز هویت OAuth1
================================================================
این ماژول signature OAuth1 (HMAC-SHA1) می‌سازد و برنامه‌های هر
کانال را از sepehrapi.sepehrtv.ir می‌گیرد.

کلیدهای OAuth از کلاینت رسمی اندروید سپهر:
  ANDROID_MOBILE: key/secret
این کلیدها عمومی هستند (در خود اپ embed شده‌اند).
"""

import hashlib
import hmac
import base64
import urllib.parse
import urllib.request
import urllib.error
import json
import time
import secrets

# کلیدهای OAuth کلاینت اندروید سپهر (از اپ رسمی استخراج شده)
CONSUMER_KEY = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"      # ANDROID_MOBILE
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"

API_BASE = "https://sepehrapi.sepehrtv.ir/beta/v0"

DEFAULT_HEADERS = {
    "User-Agent": "okhttp/4.9.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://sepehrtv.ir",
    "Referer": "https://sepehrtv.ir/",
}


def _percent(s):
    """OAuth percent-encoding (RFC 3986)."""
    return urllib.parse.quote(str(s), safe="~")


def build_oauth_header(method, url, extra_oauth=None):
    """
    یک هدر Authorization به سبک OAuth1 HMAC-SHA1 می‌سازد.
    query parameters موجود در url نیز در امضا لحاظ می‌شوند.
    """
    parsed = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    query_params = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))

    oauth_params = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_nonce": secrets.token_urlsafe(24)[:32],
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": "",
        "oauth_version": "1.0",
    }
    if extra_oauth:
        oauth_params.update(extra_oauth)

    # همه پارامترها برای ساخت base string
    all_params = {**query_params, **oauth_params}
    param_str = "&".join(
        f"{_percent(k)}={_percent(v)}"
        for k, v in sorted(all_params.items())
    )
    base_string = "&".join([
        method.upper(),
        _percent(base_url),
        _percent(param_str),
    ])
    signing_key = f"{_percent(CONSUMER_SECRET)}&"  # token secret خالی
    digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    signature = base64.b64encode(digest).decode()
    oauth_params["oauth_signature"] = signature

    header = "OAuth " + ", ".join(
        f'{_percent(k)}="{_percent(v)}"'
        for k, v in oauth_params.items()
    )
    return header


def api_get(path, params=None, timeout=20):
    """
    یک درخواست GET امضاشده به API سپهر می‌فرستد و JSON برمی‌گرداند.
    """
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    auth = build_oauth_header("GET", url)
    headers = dict(DEFAULT_HEADERS)
    headers["Authorization"] = auth

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            # ممکن است gzip باشد
            if resp.headers.get("Content-Encoding") == "gzip":
                import gzip
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="ignore")[:200]
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} for {path}: {body}")


def get_tvprogram(channel_id, date_str):
    """
    برنامه‌های یک کانال در یک تاریخ مشخص (YYYY-MM-DD).
    """
    return api_get("/epg/tvprogram", {
        "channel_id": channel_id,
        "date": date_str,
    })


if __name__ == "__main__":
    # تست سریع: برنامه شبکه یک امروز
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Testing channel_id=31 for {today}...")
    try:
        data = get_tvprogram(31, today)
        print("✅ SUCCESS!")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])
    except Exception as e:
        print(f"❌ {e}")
