"""
api_check.py — Telewebion/Sepehr API health check + auto-fallback
Runs daily via GitHub Actions. Updates api_config.json and generate.py if URL changes.
Sends Telegram alert on failure.
"""
import json, os, re, urllib.request, urllib.error, time
from pathlib import Path
from requests_oauthlib import OAuth1
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "")

# ── Telewebion stream CDN alternatives (ordered by priority) ──────────────────
STREAM_ALTERNATIVES = [
    "https://ncdn.telewebion.ir/{slug}/live/playlist.m3u8",
    "https://cdn.telewebion.ir/{slug}/live/playlist.m3u8",
    "https://live.telewebion.ir/{slug}/live/playlist.m3u8",
]

# ── Telewebion channel-list API alternatives ──────────────────────────────────
KANDOO_ALTERNATIVES = [
    "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.9.0",
    "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=6.0.0",
    "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=300&v=5.8.0",
    "https://gateway.telewebion.ir/kandoo/channel/getChannelsList/?NumOfItems=200",
]

# ── Sepehr EPG API ─────────────────────────────────────────────────────────────
SEPEHR_ALTERNATIVES = [
    "https://sepehrapi.sepehrtv.ir/beta/v0",
    "https://sepehrapi.sepehrtv.ir/v1",
    "https://api.sepehrtv.ir/beta/v0",
]
CONSUMER_KEY    = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"

TEST_SLUG = "tv1"
HEADS = {"User-Agent": "Mozilla/5.0", "Referer": "https://telewebion.ir/"}


def alert(msg):
    print(f"[ALERT] {msg}")
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    try:
        data = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  Telegram error: {e}")


def test_stream(pattern):
    # Use GET with Range header to avoid full download; 302 is fine (CDN redirect)
    url = pattern.format(slug=TEST_SLUG)
    try:
        req = urllib.request.Request(url, headers={**HEADS, "Range": "bytes=0-0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 206, 302)
    except urllib.error.HTTPError as e:
        return e.code in (200, 206, 302, 416)
    except Exception:
        return False


def test_kandoo(url):
    try:
        r = requests.get(url, headers=HEADS, timeout=10)
        return r.ok and "queryChannel" in r.text
    except Exception:
        return False


def test_sepehr(base_url):
    try:
        auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, signature_method="HMAC-SHA1")
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        r = requests.get(f"{base_url}/epg/tvprogram",
                         params={"channel_id": 31, "date": today},
                         auth=auth, timeout=15)
        return r.status_code == 200
    except Exception:
        return False


def load_cfg():
    p = Path("api_config.json")
    if p.exists():
        text = p.read_text(encoding="utf-8").strip()
        if text:
            return json.loads(text)
    return {}


def save_cfg(cfg):
    Path("api_config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def patch_generate(key, new_val):
    """Update a constant in generate.py."""
    gen_path = Path("generate.py")
    if not gen_path.exists():
        return
    text = gen_path.read_text(encoding="utf-8")
    patterns = {
        "stream_pattern": (r'STREAM\s*=\s*"[^"]*"', f'STREAM = "{new_val}"'),
        "sepehr_base":    (r'API_BASE\s*=\s*"[^"]*"', f'API_BASE = "{new_val}"'),
    }
    if key not in patterns:
        return
    regex, replacement = patterns[key]
    new_text = re.sub(regex, replacement, text)
    if new_text != text:
        gen_path.write_text(new_text, encoding="utf-8")
        print(f"  generate.py patched: {key} → {new_val}")


def check_stream(cfg):
    current = cfg.get("stream_pattern", STREAM_ALTERNATIVES[0])
    if test_stream(current):
        print(f"✅ Stream CDN OK: {current}")
        return True

    print(f"❌ Stream CDN FAILED: {current}")
    for alt in STREAM_ALTERNATIVES:
        if alt == current:
            continue
        if test_stream(alt):
            print(f"  ✅ Fallback found: {alt}")
            cfg["stream_pattern"] = alt
            save_cfg(cfg)
            patch_generate("stream_pattern", alt)
            alert(f"⚠️ Telewebion CDN changed!\nNew URL: {alt}\nAuto-updated.")
            return True

    alert("🚨 Telewebion stream CDN ALL FAILED!\nncdn.telewebion.ir is down. Manual fix needed.")
    return False


def check_kandoo(cfg):
    current = cfg.get("kandoo_url", KANDOO_ALTERNATIVES[0])
    if test_kandoo(current):
        print(f"✅ Kandoo API OK")
        return True

    print(f"❌ Kandoo API FAILED: {current}")
    for alt in KANDOO_ALTERNATIVES:
        if alt == current:
            continue
        if test_kandoo(alt):
            print(f"  ✅ Kandoo fallback: {alt}")
            cfg["kandoo_url"] = alt
            save_cfg(cfg)
            # patch import_channels.py if it exists
            imp_path = Path("import_channels.py")
            if imp_path.exists():
                text = imp_path.read_text(encoding="utf-8")
                new_text = re.sub(r'https://gateway\.telewebion\.ir/kandoo/[^\'"]+', alt, text)
                if new_text != text:
                    imp_path.write_text(new_text, encoding="utf-8")
            alert(f"⚠️ Telewebion Kandoo API URL changed!\nNew: {alt}\nAuto-updated.")
            return True

    alert("🚨 Telewebion Kandoo API ALL FAILED! Manual fix needed.")
    return False


def check_sepehr(cfg):
    current = cfg.get("sepehr_base", SEPEHR_ALTERNATIVES[0])
    if test_sepehr(current):
        print(f"✅ Sepehr EPG API OK")
        return True

    print(f"❌ Sepehr EPG API FAILED: {current}")
    for alt in SEPEHR_ALTERNATIVES:
        if alt == current:
            continue
        if test_sepehr(alt):
            print(f"  ✅ Sepehr fallback: {alt}")
            cfg["sepehr_base"] = alt
            save_cfg(cfg)
            patch_generate("sepehr_base", alt)
            alert(f"⚠️ Sepehr EPG API changed!\nNew: {alt}\nAuto-updated.")
            return True

    alert("🚨 Sepehr EPG API ALL FAILED!\nEPG will be empty. Manual fix needed.\nCheck: sepehrapi.sepehrtv.ir")
    return False


def main():
    cfg = load_cfg()
    print("=== API Health Check ===")
    stream_ok = check_stream(cfg)
    kandoo_ok = check_kandoo(cfg)
    sepehr_ok = check_sepehr(cfg)
    print(f"\nSummary: stream={'✅' if stream_ok else '❌'} kandoo={'✅' if kandoo_ok else '❌'} sepehr={'✅' if sepehr_ok else '❌'}")
    if not (stream_ok and kandoo_ok and sepehr_ok):
        exit(1)


if __name__ == "__main__":
    main()
