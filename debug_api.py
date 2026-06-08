import urllib.request, gzip

for name, url in [
    ("IR1", "https://epgshare01.online/epgshare01/epg_ripper_IR1.xml.gz"),
    ("IR", "https://epgshare01.online/epgshare01/epg_ripper_IR.xml.gz"),
]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=20)
        content = gzip.decompress(r.read()).decode("utf-8", errors="ignore")
        progs = content.count("<programme")
        # list channel ids
        import re
        chans = sorted(set(re.findall(r"channel id=\"([^\"]+)\"", content)))
        irib_chans = [c for c in chans if "IRIB" in c or "irib" in c.lower() or ".ir" in c]
        print(f"OK {name}: {progs} programs, {len(chans)} channels")
        print(f"   IRIB-like: {irib_chans[:30]}")
    except Exception as e:
        print(f"FAIL {name}: {type(e).__name__} {str(e)[:50]}")
