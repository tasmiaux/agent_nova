"""
Voice every STATIC spoken line in frontend/lines.js once and save it in
backend/tts_cache/ (the same cache the app uses). Lines already cached are
skipped. Dynamic lines (name / number read-backs), the WhatsApp text and the
founder summary are NOT voiced here.

Every run also rebuilds listen/ (hi_<lineId>.wav, kn_<lineId>.wav + README.md)
so you can play the current lines.

    python tools/voice_lines.py             voices missing lines (PAID Gnani TTS calls)
    python tools/voice_lines.py --dry-run   no Gnani calls at all: shows what is cached / would be voiced
"""

import io
import shutil
import sys
import wave

from nova_lines import CACHE_DIR, ROOT, cache_key, static_lines, voice_label

import requests  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
DRY_RUN = "--dry-run" in sys.argv
LISTEN = ROOT / "listen"
SHORT = {"hi-IN": "hi", "kn-IN": "kn"}

# Count every request that goes to Gnani; in a dry run, block them outright
calls = {"n": 0}
_post = requests.post


def guarded_post(url, *a, **k):
    if "vachana.ai" in url:
        if DRY_RUN:
            raise RuntimeError("dry run: Gnani call blocked")
        calls["n"] += 1
    return _post(url, *a, **k)


import offline  # noqa: E402
import tts  # noqa: E402

tts.requests.post = guarded_post
offline.enable(False)  # read/write the real cache (not offline fallbacks)


def seconds(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes)) as w:
        return w.getnframes() / w.getframerate()


def write_listen_folder(lines):
    """listen/<hi|kn>_<lineId>.wav copies of the cached lines + README with their text."""
    LISTEN.mkdir(exist_ok=True)
    for old in LISTEN.glob("*.wav"):
        old.unlink()
    md = ["# Nova's current lines", "",
          "Copies of the cached audio for every static line in `frontend/lines.js`.",
          "Rebuilt by `python tools/voice_lines.py` (also with `--dry-run`). Don't edit by hand.", ""]
    for code in ("hi-IN", "kn-IN"):
        pack = [ln for ln in lines if ln["code"] == code]
        if not pack:
            continue
        md += [f"## {'Hindi' if code == 'hi-IN' else 'Kannada'} · {voice_label(pack[0]['voice'])}", "",
               "| File | Line | English meaning |", "|---|---|---|"]
        for ln in pack:
            src = CACHE_DIR / cache_key(ln["text"], ln["voice"])
            name = f"{SHORT[code]}_{ln['id']}.wav"
            if src.exists():
                shutil.copyfile(src, LISTEN / name)
                cell = f"`{name}`"
            else:
                cell = f"{name} (not voiced yet)"
            md.append(f"| {cell} | {ln['text'].replace('|', '/')} | {ln['en'].replace('|', '/')} |")
        md.append("")
    (LISTEN / "README.md").write_text("\n".join(md), encoding="utf-8")


lines = static_lines()
rows, chars_sent = [], 0
for ln in lines:
    path = CACHE_DIR / cache_key(ln["text"], ln["voice"])
    if path.exists():
        rows.append((ln, "cached", seconds(path.read_bytes())))
        continue
    if DRY_RUN:
        rows.append((ln, "would voice", 0.0))
        continue
    try:
        audio = tts.speak(ln["text"], voice=ln["voice"])  # caches on success
        chars_sent += len(ln["text"])
        rows.append((ln, "newly voiced", seconds(audio)))
    except Exception as e:  # noqa: BLE001
        rows.append((ln, f"FAILED: {str(e)[:60]}", 0.0))

print(("DRY RUN (no Gnani calls)\n" if DRY_RUN else "") +
      f"{'line':<15} {'lang':<6} {'voice':<24} {'chars':>5}  {'status':<13} {'secs':>5}")
for ln, status, secs in rows:
    print(f"{ln['id']:<15} {ln['code']:<6} {voice_label(ln['voice']):<24} {len(ln['text']):>5}  {status:<13} {secs:>5.1f}")
count = lambda s: sum(1 for _, st, _ in rows if st == s)  # noqa: E731
print(f"\nLines: {len(rows)} · cached: {count('cached')} · newly voiced: {count('newly voiced')}"
      f" · would voice: {count('would voice')} · failed: {sum(1 for _, st, _ in rows if st.startswith('FAILED'))}")
print(f"Characters sent to Gnani: {chars_sent} · Gnani calls made: {calls['n']}")

write_listen_folder(lines)
print(f"listen/ rebuilt: {len(list(LISTEN.glob('*.wav')))} wav files + README.md")
