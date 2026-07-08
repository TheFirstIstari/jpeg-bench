#!/usr/bin/env python3
"""JPEG encoder benchmark: libjpeg-turbo vs IJG libjpeg vs mozjpeg.
Uses PPM as interchange format (all cjpeg implementations support it).
"""

import subprocess, time, os, sys, json, statistics
from PIL import Image

SOURCE_PNG = "/tmp/bench_realistic.png"
SOURCE_PPM = "/tmp/bench_source.ppm"
QUALITIES = [75, 85, 95, 100]
TRIALS = 3

ENCODERS = {
    "libjpeg-turbo": "/opt/homebrew/opt/jpeg-turbo/bin/cjpeg",
    "IJG":           "/opt/homebrew/opt/jpeg/bin/cjpeg",
    "mozjpeg":       "/opt/homebrew/opt/mozjpeg/bin/cjpeg",
}
DECODERS = {
    "libjpeg-turbo": "/opt/homebrew/opt/jpeg-turbo/bin/djpeg",
    "IJG":           "/opt/homebrew/opt/jpeg/bin/djpeg",
    "mozjpeg":       "/opt/homebrew/opt/mozjpeg/bin/djpeg",
}

img = Image.open(SOURCE_PNG)
img.save(SOURCE_PPM)
src_mb = round(os.path.getsize(SOURCE_PPM) / 1024 / 1024, 1)

def run(cmd, **kw):
    t0 = time.perf_counter()
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return (time.perf_counter() - t0) * 1000, r

RESULTS = {}
for short, enc in ENCODERS.items():
    print(f"\n=== {short} ===")
    RESULTS[short] = {}
    for q in QUALITIES:
        times, sizes, dtimes = [], [], []
        for t in range(TRIALS):
            jpg = f"/tmp/bench_{short}_{q}_{t}.jpg"
            ms, r = run([enc, "-quality", str(q), "-outfile", jpg, SOURCE_PPM])
            if r.returncode: continue
            times.append(ms); sizes.append(os.path.getsize(jpg))
            ms2, r2 = run([DECODERS[short], "-outfile", f"/tmp/bench_dec_{short}_{q}_{t}.ppm", jpg])
            if r2.returncode == 0: dtimes.append(ms2)
        if not times: continue
        RESULTS[short][q] = {
            "enc_ms": round(statistics.mean(times), 1),
            "sz_kb": round(statistics.mean(sizes) / 1024, 1),
            "dec_ms": round(statistics.mean(dtimes), 1) if dtimes else 0,
        }
        r = RESULTS[short][q]
        print(f"  q{q:>3}: {r['enc_ms']:>7.1f}ms enc  {r['dec_ms']:>7.1f}ms dec  {r['sz_kb']:>8.1f}KB")

# Save
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "results.json"), "w") as f:
    json.dump(RESULTS, f, indent=2)

# Report
print(f"\n\n# JPEG Encoder Benchmark — {src_mb}MB PPM source\n")
print("## Encode Time (ms)")
print(f"{'Encoder':<16}", "".join(f"{'q'+str(q):>9}" for q in QUALITIES))
print("-" * (16 + 9 * len(QUALITIES)))
for s in ["libjpeg-turbo", "IJG", "mozjpeg"]:
    if s not in RESULTS: continue
    v = "".join(f"{RESULTS[s][q]['enc_ms']:>8.1f}ms" if q in RESULTS[s] else f"{'ERR':>9}" for q in QUALITIES)
    print(f"{s:<16} {v}")

print("\n## Decode Time (ms)")
print(f"{'Encoder':<16} {'q85':>9}")
print("-" * 26)
for s in ["libjpeg-turbo", "IJG", "mozjpeg"]:
    if s not in RESULTS: continue
    print(f"{s:<16} {RESULTS[s][85]['dec_ms']:>8.1f}ms")

print("\n## File Size (KB)")
print(f"{'Encoder':<16}", "".join(f"{'q'+str(q):>9}" for q in QUALITIES))
print("-" * (16 + 9 * len(QUALITIES)))
for s in ["libjpeg-turbo", "IJG", "mozjpeg"]:
    if s not in RESULTS: continue
    v = "".join(f"{RESULTS[s][q]['sz_kb']:>8.1f}KB" if q in RESULTS[s] else f"{'ERR':>9}" for q in QUALITIES)
    print(f"{s:<16} {v}")

print("\n## Speedup vs IJG @ q85")
base = RESULTS.get("IJG", {}).get(85, {})
for s in ["libjpeg-turbo", "mozjpeg"]:
    d = RESULTS.get(s, {}).get(85, {})
    if d and base:
        print(f"  {s:<16}: enc {base['enc_ms']/d['enc_ms']:.1f}x  dec {base['dec_ms']/d['dec_ms']:.1f}x")

print("\n## Size vs libjpeg-turbo @ q85")
tur = RESULTS.get("libjpeg-turbo", {}).get(85, {})
for s in ["IJG", "mozjpeg"]:
    d = RESULTS.get(s, {}).get(85, {})
    if d and tur:
        print(f"  {s:<16}: {d['sz_kb']/tur['sz_kb']:.2f}x")
