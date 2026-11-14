"""
Audit backend/tts_cache/: match every cached file to a current static line in
frontend/lines.js by recomputing its cache key. Anything that doesn't match a
current line is "stale" (old wording, old names, old founder summaries, etc.).

    python tools/audit_cache.py           list only
    python tools/audit_cache.py --move    also move stale files into tts_cache/_old/ (never deletes)

No Gnani calls.
"""

import shutil
import sys

from nova_lines import CACHE_DIR, cache_key, static_lines, voice_label

sys.stdout.reconfigure(encoding="utf-8")
move = "--move" in sys.argv

current = {cache_key(ln["text"], ln["voice"]): ln for ln in static_lines()}
files = sorted(p for p in CACHE_DIR.glob("*.wav"))

print(f"{'file':<26} {'line id':<15} {'lang':<6} {'voice':<24} status")
n_cur = n_stale = 0
for f in files:
    ln = current.get(f.name)
    if ln:
        n_cur += 1
        print(f"{f.name:<26} {ln['id']:<15} {ln['code']:<6} {voice_label(ln['voice']):<24} current")
    else:
        n_stale += 1
        print(f"{f.name:<26} {'-':<15} {'-':<6} {'-':<24} stale")

missing = [ln for k, ln in current.items() if not (CACHE_DIR / k).exists()]
print(f"\nCurrent: {n_cur} · stale: {n_stale} · current lines not cached: {len(missing)}")
for ln in missing:
    print(f"  not cached: {ln['code']} {ln['id']}")

if move and n_stale:
    old = CACHE_DIR / "_old"
    old.mkdir(exist_ok=True)
    for f in files:
        if f.name not in current:
            shutil.move(str(f), str(old / f.name))
    print(f"Moved {n_stale} stale files to {old.relative_to(CACHE_DIR.parent.parent)}")
