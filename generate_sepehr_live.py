"""Generate sepehr_live.m3u from Sepehr TV live channel API."""
import base64, hashlib, hmac, json, time, uuid, urllib.parse, urllib.request, ssl, sys

CONSUMER_KEY    = "QKORpgyu9mpw3MZUUwu8Mm4qxYMsXq3L"
CONSUMER_SECRET = "jtroj3hkyjlU06j7MtJimJ1I3PTTpx39"
GROUP           = "📡 سپهر"
PROXY_BASE      = "https://sepehr-proxy.samhoustonbot.workers.dev"

# Exclude radio, internal, iFrame/mosaic channels
_SKIP_PREFIXES = ("rn-", "radio", "r-", "itv3", "ctv3", "ivarzesh", "ifaratar",
                  "ostanifull", "3x3", "iribresearch", "pirib", "itv3balance",
                  "rn-moghavemat", "radioboroonmarzi")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def _oauth_header(method, url):
    p = {
        "oauth_consumer_key": CONSUMER_KEY,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_version": "1.0",
    }
    base = "&".join([
        method.upper(),
        urllib.parse.quote(url, safe=""),
        urllib.parse.quote(
            "&".join(f"{k}={urllib.parse.quote(v, safe='')}" for k, v in sorted(p.items())),
            safe=""
        ),
    ])
    sig = base64.b64encode(
        hmac.new(f"{CONSUMER_SECRET}&".encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    p["oauth_signature"] = sig
    return "OAuth " + ", ".join(f'{k}="{urllib.parse.quote(v, safe="")}"' for k, v in sorted(p.items()))


def fetch_channels():
    url = "https://sepehrapi.sepehrtv.ir/beta/v0/channels/live"
    req = urllib.request.Request(url, headers={
        "Authorization": _oauth_header("GET", url),
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return json.loads(r.read()).get("list", [])


def build_m3u(channels):
    lines = ["#EXTM3U", ""]
    count = 0
    for ch in channels:
        uid = ch.get("uid", "")
        if any(uid.startswith(p) for p in _SKIP_PREFIXES):
            continue
        streams = ch.get("streams", [])
        if not streams:
            continue
        src = streams[0].get("src", "")
        if not src or not src.startswith(("http://", "https://")):
            continue
        name = ch.get("name", uid).replace(" - HD", " HD").replace(" - ", " ")
        icon = ch.get("icon", "")
        tvg_id = ch.get("uid", "")
        proxy_url = f"{PROXY_BASE}/{uid}"
        extinf = f'#EXTINF:-1 group-title="{GROUP}" tvg-id="{tvg_id}" tvg-logo="{icon}",{name}'
        lines += [extinf, proxy_url, ""]
        count += 1
    print(f"sepehr_live: {count} channels", flush=True)
    return "\n".join(lines)


if __name__ == "__main__":
    channels = fetch_channels()
    m3u = build_m3u(channels)
    with open("sepehr_live.m3u", "w", encoding="utf-8") as f:
        f.write(m3u)
    print("Written: sepehr_live.m3u", flush=True)
