"""Cut the 2:02 live Kannada demo down to the moments with voice or on-screen action (~49 s).
Every cut sits on a pause in the speech; each piece gets a 30 ms audio fade so cuts don't click.
The voice is normalised to -14 LUFS, the same level as the intro video. No paid calls.

  python cut_50s.py  -> nova_live_demo_kannada_50s.mp4
"""
import json, subprocess
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = HERE / "nova_live_demo_kannada.mp4"
OUT = HERE / "nova_live_demo_kannada_50s.mp4"

KEEP = [  # (start, end) seconds in the 2:02 clip
    (3.8, 6.9),      # you: "Onboard Kaveri Handlooms"
    (13.6, 15.8),    # the plan appears
    (18.9, 23.7),    # Call clicked; Nova: "Namaskara! I'm Nova, the Supra AI team's AI assistant."
    (33.6, 38.4),    # Nova asks the name; you: Suman
    (44.8, 48.4),    # name read-back; you: yes
    (51.6, 54.4),    # Nova asks for the number
    (56.1, 60.8),    # you say the number
    (64.7, 70.2),    # number read-back
    (71.0, 72.0),    # you: yes
    (74.8, 79.3),    # Nova: thank you, details saved, summary sent on WhatsApp
    (83.9, 87.0),    # Mark done -> Verification passed -> Ready
    (98.6, 103.5),   # Avinash: "Here are your updates. Kaveri Handlooms is set up, with Suman as the owner."
    (117.2, 121.0),  # Approve go-live -> Live
]

parts, labels = [], []
for i, (a, b) in enumerate(KEEP):
    d = b - a
    parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
    parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={d - 0.03:.3f}:d=0.03[a{i}]")
    labels.append(f"[v{i}][a{i}]")
graph = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(KEEP)}:v=1:a=1[v][a]"
tmp = HERE / "_cut_tmp.mp4"
subprocess.run([FF, "-v", "error", "-y", "-i", str(SRC), "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(tmp)], check=True)

# Two-pass loudness normalisation to -14 LUFS (matches the intro)
m = subprocess.run([FF, "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run([FF, "-v", "error", "-y", "-i", str(tmp), "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart", str(OUT)], check=True)
tmp.unlink()
print(f"kept {len(KEEP)} pieces, {sum(b - a for a, b in KEEP):.1f} s -> {OUT}")
