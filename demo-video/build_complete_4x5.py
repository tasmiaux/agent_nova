"""4:5 (1080x1350) complete Nova video, same order and timing as build_complete.py:
4:5 intro up to the Approve step -> pause -> live demo -> hold -> 4:5 intro end card.

The live demo is a 16:9 screen recording, recomposed (not squashed): the unchanging left sidebar is
cropped off, the rest is scaled to the full 1080 width on the intro's dark background, with a small
"Live demo" heading above it. No speed changes.

  python build_complete_4x5.py  -> nova_complete_demo_4x5.mp4
"""
import json, subprocess
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
INTRO = HERE.parent / "nova-intro" / "out" / "nova_intro_final_4x5.mp4"
DEMO = HERE / "nova_live_demo_kannada_50s.mp4"
OUT = HERE / "nova_complete_demo_4x5.mp4"

beats = json.loads((HERE.parent / "nova-intro" / "beats.json").read_text(encoding="utf-8"))["beats"]
END_CARD = round(sum(b["beat"] for b in beats[:5]), 3)
PAUSE_BEFORE_DEMO = 0.6
HOLD_AFTER_DEMO = 1.2

W, H, BG = 1080, 1350, "0x111318"           # intro background (--ink in the app)
CROP_X = 245                                 # left sidebar edge in the 1920x1080 recording
DEMO_H = round((1080 * W / (1920 - CROP_X)) / 2) * 2     # 696
HEAD_H, GAP = 110, 44
TOP = (H - (HEAD_H + GAP + DEMO_H)) // 2     # centre heading + demo vertically
DEMO_Y = TOP + HEAD_H + GAP
BOLD, REG = "C\\:/Windows/Fonts/segoeuib.ttf", "C\\:/Windows/Fonts/segoeui.ttf"

A = "aformat=sample_rates=48000:channel_layouts=stereo"
V = "fps=30,format=yuv420p,setsar=1"
demo_v = (f"[1:v]crop={1920 - CROP_X}:1080:{CROP_X}:0,scale={W}:{DEMO_H},"
          f"pad={W}:{H}:0:{DEMO_Y}:color={BG},"
          f"drawtext=fontfile='{BOLD}':text='Live demo':fontcolor=white:fontsize=54:x=(w-text_w)/2:y={TOP},"
          f"drawtext=fontfile='{REG}':text='Kannada call · simulated Supra AI platform':fontcolor=0xa3a8b1:fontsize=32:"
          f"x=(w-text_w)/2:y={TOP + 70},"
          f"{V},tpad=stop_mode=clone:stop_duration={HOLD_AFTER_DEMO}[v2]")
graph = ";".join([
    f"[0:v]trim=0:{END_CARD},setpts=PTS-STARTPTS,{V},tpad=stop_mode=add:color={BG}:stop_duration={PAUSE_BEFORE_DEMO}[v1]",
    f"[0:a]atrim=0:{END_CARD},asetpts=PTS-STARTPTS,{A},afade=t=out:st={END_CARD - 0.08}:d=0.08,apad=pad_dur={PAUSE_BEFORE_DEMO}[a1]",
    demo_v,
    f"[1:a]{A},afade=t=in:d=0.03,apad=pad_dur={HOLD_AFTER_DEMO}[a2]",
    f"[0:v]trim=start={END_CARD},setpts=PTS-STARTPTS,{V}[v3]",
    f"[0:a]atrim=start={END_CARD},asetpts=PTS-STARTPTS,{A},afade=t=in:d=0.05[a3]",
    "[v1][a1][v2][a2][v3][a3]concat=n=3:v=1:a=1[v][a]",
])
subprocess.run([FF, "-v", "error", "-y", "-i", str(INTRO), "-i", str(DEMO), "-filter_complex", graph,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(OUT)], check=True)
print(f"demo area {W}x{DEMO_H} at y={DEMO_Y}, heading at y={TOP} -> {OUT}")
