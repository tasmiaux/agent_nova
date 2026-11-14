"""Voice-over lines for the Nova intro, made with the Nova app's own Gnani TTS helper
(backend/tts.py synthesize) and GNANI_API_KEY from nova-ai/.env.local (never printed).

  python voice.py 1        -> generate line 1 only
  python voice.py 2 3 4    -> generate those lines
  python voice.py list     -> show each line, its cache file and duration (no calls)

One paid call per line, no retries, stops on the first error. Each file is cached in vo/ by a
hash of model|voice|language|text, so an unchanged line is never billed twice. Respects DRY_RUN.
"""
import hashlib, sys, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "backend"))
import offline  # noqa: E402  (backend modules)
import tts      # noqa: E402

VO = HERE / "vo"
# Female voice already used in the app's config (Lakshmi, timbre-v3.0), speaking English.
MODEL, VOICE, LANG = "timbre-v3.0", "Lakshmi", "en-IN"
LINES = {
    1: "A new customer signs up. And suddenly, the founder has a dozen things to chase.",
    2: "That's where Nova steps in, calling the owner in their own language.",
    3: "It confirms the owner's name and number, one conversation at a time.",
    4: "Then it checks the setup. One failed check, and the launch is blocked.",
    5: "The founder gets a crisp English report, reviews the results, and gives the green light.",
    6: "Nova. Powered by Gnani's Prisma and Timbre voice models. Onboarding in their language. Reporting in yours.",
}


def path_for(n):
    key = hashlib.sha256(f"{MODEL}|{VOICE}|{LANG}|{LINES[n]}".encode("utf-8")).hexdigest()[:16]
    return VO / f"line{n}_{key}.wav"


def duration(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def main(args):
    if args == ["list"]:
        for n in LINES:
            p = path_for(n)
            print(n, p.name, f"{duration(p):.2f} s" if p.exists() else "not generated")
        return
    if offline.dry_run_flag():
        sys.exit("DRY_RUN is on: no Gnani calls made. Set DRY_RUN=false in .env.local for this step.")
    VO.mkdir(exist_ok=True)
    calls = 0
    for n in [int(a) for a in args]:
        p = path_for(n)
        if p.exists():
            print(f"line {n}: cached, no call -> {p} ({duration(p):.2f} s)")
            continue
        calls += 1
        try:
            audio = tts.synthesize(LINES[n], MODEL, VOICE, language=LANG, retry=False)
        except Exception as e:  # no retries: stop and report
            print(f"line {n}: FAILED, stopping. {e}")
            break
        p.write_bytes(audio)
        print(f"line {n}: {VOICE} ({MODEL}, {LANG}) -> {p} ({duration(p):.2f} s)")
    print("paid Gnani calls made this run:", calls)


if __name__ == "__main__":
    main(sys.argv[1:])
