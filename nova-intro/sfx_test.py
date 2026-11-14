"""Test copy of the 16:9 intro: same video and sound, plus a label in the bottom-left corner naming
each sound effect at the moment it plays, so you can judge how each one fits. No paid calls.

  python sfx_test.py  -> out/sfx_test_labeled.mp4
"""
import json, subprocess
from pathlib import Path

import imageio_ffmpeg
import sfx

HERE = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
LABEL = {"whoosh": "WHOOSH  (scene comes in)", "tick": "TICK  (item appears)", "pop": "POP  (message lands)",
         "click": "CLICK  (button press)", "thud": "THUD  (check fails)", "chime": "CHIME  (done / verified)"}

info = json.loads((HERE / "beats.json").read_text(encoding="utf-8"))
rows = info["beats"]
starts = [sum(r["beat"] for r in rows[:i]) for i in range(len(rows))]
ev = sorted(sfx.events(starts))

# One label per event, shown from the sound until the next event (at most 0.9 s)
font = "C\\:/Windows/Fonts/arialbd.ttf"
parts = []
for i, (t, name) in enumerate(ev):
    end = min(t + .9, ev[i + 1][0] if i + 1 < len(ev) else t + .9)
    txt = f"SFX {i + 1}/{len(ev)}  {LABEL[name]}"
    parts.append(f"drawtext=fontfile='{font}':text='{txt}':x=40:y=h-90:fontsize=34:fontcolor=white:"
                 f"box=1:boxcolor=0x1f9d55@0.9:boxborderw=14:enable='between(t,{t - .05:.3f},{end:.3f})'")
script = HERE / "out" / "sfx_labels.txt"
script.write_text(",\n".join(parts), encoding="utf-8")
out = HERE / "out" / "sfx_test_labeled.mp4"
subprocess.run([FF, "-v", "error", "-y", "-i", str(HERE / "out" / "nova_intro_final.mp4"), "-/vf", str(script),
                "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "copy",
                "-movflags", "+faststart", str(out)], check=True)
for i, (t, name) in enumerate(ev):
    print(f"{i + 1:2d}  {t:6.2f} s  {name}")
print("test video ->", out)
