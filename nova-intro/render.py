"""Render intro.html frame by frame (seek(t) + Playwright + ffmpeg). 30 fps, no motion-blur subframes.
The film length comes from the page (window.FILM_T), so changing the beat lengths needs no edit here.

  python render.py stills 0 15.4 16.4 19.0 30.0 -> out/stills/still_XX.png (1920x1080), sheet.png, and a
                                                 360 px wide copy of each (phone readability check)
  python render.py draft                       -> out/draft_960x540.mp4
  python render.py full                        -> out/nova_intro_1920x1080.mp4 (silent master)
  FMT=45 python render.py stills|draft|full -> the 4:5 version (1080x1350), files tagged _4x5 / 1080x1350
  python render.py contact out/<file>.mp4      -> out/contact.png (2 fps overview)
"""
import asyncio, os, shutil, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
FF = imageio_ffmpeg.get_ffmpeg_exe()
# FMT=45 renders the 4:5 LinkedIn version (1080x1350) from the same timeline
F45 = os.environ.get("FMT") == "45"
URL = (HERE / "intro.html").as_uri() + ("?fmt=45" if F45 else "")
W, H = (1080, 1350) if F45 else (1920, 1080)
TAG = "_4x5" if F45 else ""
FPS = 30
# Reuse the Chromium already installed on this machine (set CHROME to override)
CHROME = os.environ.get("CHROME") or str(Path(os.environ["LOCALAPPDATA"]) / "ms-playwright/chromium-1234/chrome-win64/chrome.exe")
FLAGS = ["--force-color-profile=srgb", "--font-render-hinting=none", "--disable-threaded-animation",
         "--run-all-compositor-stages-before-draw", "--hide-scrollbars"]


async def open_page(p, scale):
    b = await p.chromium.launch(executable_path=CHROME, args=FLAGS)
    pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=scale)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    await pg.goto(URL)
    await pg.wait_for_function("window.ready === true", timeout=60000)
    ok = await pg.evaluate("""document.fonts.check('600 60px Inter') && document.fonts.check('500 26px "JetBrains Mono"')
                              && document.fonts.check('500 28px "Noto Sans Devanagari"', 'नमस्ते')""")
    if not ok:
        print("WARNING: web fonts did not load (check the internet connection)")
    return b, pg, errs, await pg.evaluate("window.FILM_T")


async def shot(pg, t, path, fmt="png"):
    await pg.evaluate(f"window.seek({t})")
    await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
    el = await pg.query_selector("#stage")
    await el.screenshot(path=str(path), type=fmt, **({"quality": 95} if fmt == "jpeg" else {}))


async def stills(times):
    d = OUT / ("stills" + TAG); d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.png"): f.unlink()          # clear files (OneDrive can lock the folder itself)
    async with async_playwright() as p:
        b, pg, errs, T = await open_page(p, 1)
        for i, t in enumerate(times):
            await shot(pg, t, d / f"still_{i:02d}.png")
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:5])
    for i in range(len(times)):
        subprocess.run([FF, "-v", "error", "-y", "-i", str(d / f"still_{i:02d}.png"), "-vf", "scale=360:-1:flags=area",
                        str(d / f"phone_{i:02d}.png")], check=True)
    cols = (6 if F45 else 3) if len(times) > 4 else 2
    rows = -(-len(times) // cols)
    subprocess.run([FF, "-v", "error", "-y", "-i", str(d / "still_%02d.png"), "-vf",
                    f"scale={540 if F45 else 960}:-1,tile={cols}x{rows}:padding=8:color=black", "-frames:v", "1", str(d / "sheet.png")], check=True)
    print(f"stills -> {d} (film length {T:.2f} s)")


async def frames(scale, folder):
    shutil.rmtree(folder, ignore_errors=True); folder.mkdir(parents=True)
    async with async_playwright() as p:
        b, pg, errs, T = await open_page(p, scale)
        n = int(round(T * FPS))
        for i in range(n):
            await shot(pg, i / FPS, folder / f"f_{i:04d}.jpg", "jpeg")
            if i % 90 == 0: print(f"frame {i}/{n}", flush=True)
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:5])
    return n


def encode(folder, out, crf, preset):
    subprocess.run([FF, "-v", "error", "-y", "-framerate", str(FPS), "-i", str(folder / "f_%04d.jpg"),
                    "-vf", "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p",
                    "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:v", "libx264", "-crf", str(crf), "-preset", preset, "-an", "-movflags", "+faststart", str(out)], check=True)
    print("video ->", out)


def contact(path):
    out = OUT / "contact.png"
    subprocess.run([FF, "-v", "error", "-y", "-i", str(path), "-vf", "fps=2,scale=320:-1,tile=8x8:padding=4",
                    "-frames:v", "1", str(out)], check=True)
    print("contact ->", out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    OUT.mkdir(exist_ok=True)
    if cmd == "stills":
        asyncio.run(stills([float(x) for x in sys.argv[2:]]))
    elif cmd == "draft":       # 960x540: judge rhythm, not sharpness
        asyncio.run(frames(0.5, HERE / ("frames_draft" + TAG)))
        encode(HERE / ("frames_draft" + TAG), OUT / f"draft{TAG}_{W // 2}x{H // 2}.mp4", 23, "veryfast")
    elif cmd == "full":
        asyncio.run(frames(1, HERE / ("frames_full" + TAG)))
        encode(HERE / ("frames_full" + TAG), OUT / f"nova_intro_{W}x{H}.mp4", 16, "slow")
    elif cmd == "contact":
        contact(Path(sys.argv[2]))
