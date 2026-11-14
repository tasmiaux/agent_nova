"""Complete Nova video: intro up to the Approve step -> pause -> live demo -> hold -> intro end card.
No speed changes: every part keeps its own timing; the pauses only hold a still frame with silence.

  python build_complete.py  -> nova_complete_demo.mp4
"""
import json, subprocess
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
INTRO = HERE.parent / "nova-intro" / "out" / "nova_intro_final.mp4"
DEMO = HERE / "nova_live_demo_kannada_50s.mp4"
OUT = HERE / "nova_complete_demo.mp4"

beats = json.loads((HERE.parent / "nova-intro" / "beats.json").read_text(encoding="utf-8"))["beats"]
END_CARD = round(sum(b["beat"] for b in beats[:5]), 3)   # where the "Nova. Powered by..." card starts
PAUSE_BEFORE_DEMO = 0.6    # dark background held after the intro, before the app appears
HOLD_AFTER_DEMO = 1.2      # "Live. Onboarding complete." held before the end card

A = "aformat=sample_rates=48000:channel_layouts=stereo"
V = "fps=30,format=yuv420p,setsar=1"
graph = ";".join([
    # 1. intro up to the end card, then a pause on the intro's plain dark background (#111318)
    f"[0:v]trim=0:{END_CARD},setpts=PTS-STARTPTS,{V},tpad=stop_mode=add:color=0x111318:stop_duration={PAUSE_BEFORE_DEMO}[v1]",
    f"[0:a]atrim=0:{END_CARD},asetpts=PTS-STARTPTS,{A},afade=t=out:st={END_CARD - 0.08}:d=0.08,apad=pad_dur={PAUSE_BEFORE_DEMO}[a1]",
    # 2. the live demo, then hold its last frame ("Live")
    f"[1:v]{V},tpad=stop_mode=clone:stop_duration={HOLD_AFTER_DEMO}[v2]",
    f"[1:a]{A},afade=t=in:d=0.03,apad=pad_dur={HOLD_AFTER_DEMO}[a2]",
    # 3. the intro's end card
    f"[0:v]trim=start={END_CARD},setpts=PTS-STARTPTS,{V}[v3]",
    f"[0:a]atrim=start={END_CARD},asetpts=PTS-STARTPTS,{A},afade=t=in:d=0.05[a3]",
    "[v1][a1][v2][a2][v3][a3]concat=n=3:v=1:a=1[v][a]",
])
subprocess.run([FF, "-v", "error", "-y", "-i", str(INTRO), "-i", str(DEMO), "-filter_complex", graph,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(OUT)], check=True)
demo_len = float(subprocess.run([FF, "-i", str(DEMO)], capture_output=True, text=True).stderr.split("Duration: ")[1].split(",")[0].split(":")[-1])
t2 = END_CARD + PAUSE_BEFORE_DEMO
t3 = t2 + demo_len + HOLD_AFTER_DEMO
print(f"intro 0-{END_CARD:.2f} s | pause to {t2:.2f} | demo {t2:.2f}-{t2 + demo_len:.2f} | hold to {t3:.2f} | end card {t3:.2f}-{t3 + 7.305:.2f}")
print("->", OUT)
