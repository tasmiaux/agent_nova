"""Voice-over timing and mix for the Nova intro (no paid calls; works on the files in vo/).

  python mix.py beats   -> measure each line, trim only its leading/trailing silence (speed untouched),
                           set beat length = speech + 0.6 s (beat 4 + 2.5 s more for the flag and fix),
                           write beats.json and the BEATS line in intro.html
  python mix.py mux     -> place each line at the start of its beat, normalise the voice to -14 LUFS
                           (two-pass loudnorm), mux with out/nova_intro_1920x1080.mp4
                           -> out/nova_intro_final.mp4
  python mix.py mux45   -> same voice on out/nova_intro_1080x1350.mp4 -> out/nova_intro_final_4x5.mp4
"""
import json, re, subprocess, sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from voice import LINES, duration, path_for  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
PAD, BEAT4_EXTRA = 0.6, 2.5
SR = 48000


def speech_span(p):
    """(start, end) of speech: silencedetect at -45 dB, only edge silences are cut."""
    out = subprocess.run([FF, "-hide_banner", "-i", str(p), "-af", "silencedetect=noise=-45dB:d=0.08", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = duration(p)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    a, b = 0.0, dur
    for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if s <= 0.001: a = e                  # leading silence
        if e >= dur - 0.001: b = s            # trailing silence
    return round(a, 3), round(b, 3)


def beats():
    rows, lens = [], []
    for n in LINES:
        a, b = speech_span(path_for(n))
        length = (b - a) + PAD + (BEAT4_EXTRA if n == 4 else 0)
        rows.append({"line": n, "file": path_for(n).name, "raw": round(duration(path_for(n)), 3),
                     "speech_start": a, "speech_end": b, "speech": round(b - a, 3), "beat": round(length, 3)})
        lens.append(round(length, 3))
    total = round(sum(lens), 3)
    (HERE / "beats.json").write_text(json.dumps({"beats": rows, "total": total}, indent=2), encoding="utf-8")
    html = HERE / "intro.html"
    s = html.read_text(encoding="utf-8")
    s, k = re.subn(r"const BEATS = \[[^\]]*\];", f"const BEATS = {json.dumps(lens)};", s)
    assert k == 1, "BEATS line not found in intro.html"
    html.write_text(s, encoding="utf-8")
    for r in rows:
        print(f"line {r['line']}: raw {r['raw']:.2f} s, speech {r['speech']:.2f} s -> beat {r['beat']:.2f} s")
    print(f"total {total:.2f} s" + ("  (OVER 35 s)" if total > 35 else ""))


def loudnorm_args(src):
    first = subprocess.run([FF, "-hide_banner", "-i", str(src), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(first[first.rindex("{"):first.rindex("}") + 1])
    return (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


def mux(video_name="nova_intro_1920x1080.mp4", final_name="nova_intro_final.mp4"):
    info = json.loads((HERE / "beats.json").read_text(encoding="utf-8"))
    rows, total = info["beats"], info["total"]
    starts = [sum(r["beat"] for r in rows[:i]) for i in range(len(rows))]
    ins, parts = [], []
    for i, r in enumerate(rows):
        ins += ["-i", str(HERE / "vo" / r["file"])]
        ms = int(round(starts[i] * 1000))
        parts.append(f"[{i}:a]atrim={r['speech_start']}:{r['speech_end']},asetpts=PTS-STARTPTS,"
                     f"aresample={SR},afade=t=in:d=0.01,adelay={ms}|{ms}[a{i}]")
    graph = ";".join(parts) + ";" + "".join(f"[a{i}]" for i in range(len(rows))) + \
        f"amix=inputs={len(rows)}:normalize=0,apad,atrim=0:{total}[vo]"
    raw = HERE / "out" / "vo_track_raw.wav"
    subprocess.run([FF, "-v", "error", "-y", *ins, "-filter_complex", graph, "-map", "[vo]", "-ac", "1", "-ar", str(SR), str(raw)], check=True)
    # Add the small UI sound effects (sfx.py, synthesized) under the voice, then normalise the whole mix
    import numpy as np
    import sfx
    pcm = subprocess.run([FF, "-v", "quiet", "-i", str(raw), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    mixed, n_fx = sfx.mix_in(np.frombuffer(pcm, np.float32).astype(np.float64), starts, total)
    mixed = (mixed / (np.abs(mixed).max() + 1e-9) * .9).astype(np.float32)
    raw_mix = HERE / "out" / "mix_raw.wav"
    subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(raw_mix)],
                   input=mixed.tobytes(), check=True)
    vo = HERE / "out" / "vo_track.wav"     # voice + effects, -14 LUFS
    subprocess.run([FF, "-v", "error", "-y", "-i", str(raw_mix), "-af", loudnorm_args(raw_mix), "-ar", str(SR), str(vo)], check=True)
    print("sound effects placed:", n_fx)
    video = HERE / "out" / video_name
    final = HERE / "out" / final_name
    subprocess.run([FF, "-v", "error", "-y", "-i", str(video), "-i", str(vo), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-movflags", "+faststart", str(final)], check=True)
    print("line starts (s):", [round(x, 2) for x in starts])
    print("final ->", final)


if __name__ == "__main__":
    if sys.argv[1] == "mux45":   # same voice track on the 4:5 render
        mux("nova_intro_1080x1350.mp4", "nova_intro_final_4x5.mp4")
    else:
        {"beats": beats, "mux": mux}[sys.argv[1]]()
