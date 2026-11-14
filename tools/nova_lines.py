"""
Shared helpers for the tools/ scripts: read the current static lines from
frontend/lines.js (the same file the app loads) and compute their audio
cache file names exactly the way backend/tts.py does.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from config import TTS_VOICES  # noqa: E402

CACHE_DIR = ROOT / "backend" / "tts_cache"

_DUMP_JS = """
const fs = require('fs'), vm = require('vm');
const ctx = { globalThis: {} }; ctx.window = ctx.globalThis;
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
const out = [];
for (const [code, p] of Object.entries(ctx.window.NOVA_LINES.packs))
  for (const [id, line] of Object.entries(p.lines))
    out.push({ code, voice: p.voice, id, text: line.hi, en: line.en });
console.log(JSON.stringify(out));
"""


def static_lines():
    """[{code, voice, id, text, en}, ...] for every static spoken line, all packs."""
    out = subprocess.run(["node", "-e", _DUMP_JS, str(ROOT / "frontend" / "lines.js")],
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(out.stdout)


def cache_key(text, voice):
    """File name backend/tts.py uses for this text + voice role."""
    model, name, lang = TTS_VOICES[voice]
    return hashlib.sha256(f"{model}|{name}|{lang}|{text}".encode("utf-8")).hexdigest()[:20] + ".wav"


def voice_label(voice):
    model, name, _ = TTS_VOICES[voice]
    return f"{name} ({model})"
