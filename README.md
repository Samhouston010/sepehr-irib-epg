# شبکه‌های صداوسیما — M3U و EPG خودکار

لیست پخش (M3U) و راهنمای برنامه (EPG) کانال‌های صداوسیمای جمهوری اسلامی ایران.
لینک‌ها از CDN مستقیم تلوبیون (`ncdn.telewebion.ir`) — **ثابت و بدون توکن**.
برنامه‌ها (EPG) از API سپهر گرفته می‌شوند و هر ۶ ساعت به‌روزرسانی می‌شوند.

## آدرس‌های استفاده

**M3U (لیست پخش):**
```
https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.m3u
```

**EPG (راهنمای برنامه — XMLTV فشرده):**
```
https://raw.githubusercontent.com/Samhouston010/sepehr-irib-epg/main/sepehr.xml.gz
```

فایل M3U خودش به EPG اشاره می‌کند (`x-tvg-url`)، پس در TiviMate / IPTV player
کافی است فقط آدرس M3U را وارد کنید و EPG خودکار بارگذاری می‌شود.

## ساختار

| فایل | توضیح |
|------|--------|
| `channels.json` | لیست کانال‌ها (slug تلوبیون، channel_id سپهر، نام، گروه) |
| `sepehr_api.py` | کلاینت API سپهر با احراز هویت OAuth1 |
| `generate.py` | ساخت M3U + گرفتن EPG + خروجی XMLTV |
| `discover_ids.py` | کشف channel_id درست کانال‌ها |
| `.github/workflows/update.yml` | اجرای خودکار هر ۶ ساعت |

## اجرای دستی

از تب **Actions** در گیت‌هاب → **Update Sepehr IRIB EPG** → **Run workflow**.

## نکته فنی

- لینک‌های پخش از CDN تلوبیون است که برخلاف لینک‌های توکن‌دار سپهر، ثابت می‌مانند.
- EPG از API سپهر (`sepehrapi.sepehrtv.ir`) با امضای OAuth1 (HMAC-SHA1) گرفته می‌شود.
- زمان‌ها به وقت تهران (+03:30) ثبت می‌شوند.
