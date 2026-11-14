"""Small UI sound effects for the Nova intro, synthesized in code (no downloads, no paid calls),
placed on the same moments the animation uses in intro.html (design time u x K = seconds).

  whoosh  : soft swept air when a new scene comes in
  tick    : tiny high tap as a row, bullet or chip appears
  pop     : short rising blip when a chat message lands
  click   : button press (Yes, Approve go-live)
  thud    : low soft knock when the failed check is highlighted
  chime   : two-note "done" when the row turns Verified and on Approve

Used by mix.py mux: the effects sit well under the voice, then the whole mix is normalised to -14 LUFS.
"""
import numpy as np

SR = 48000
K = 1.4                     # same slow-down factor as intro.html
RNG = np.random.default_rng(7)   # seeded: the same mix every time


def _env(n, attack, decay):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attack, 0) / decay)


def tick():
    n = int(.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2300 * t) * .8 + np.sin(2 * np.pi * 4600 * t) * .2) * _env(n, .001, .010)


def click():
    n = int(.06 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 1400 * t) * _env(n, .0005, .012)
    snap = RNG.standard_normal(n) * _env(n, .0002, .003) * .5
    return body + snap


def pop():
    n = int(.09 * SR); t = np.arange(n) / SR
    f = 420 + 520 * (t / t[-1])                       # rising blip
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, .003, .028)


def thud():
    n = int(.22 * SR); t = np.arange(n) / SR
    f = 190 - 90 * (t / t[-1])                        # falling, soft knock
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, .004, .06)


def chime():
    n = int(.7 * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for f, d in ((880, 0), (1318.5, .085)):           # A5 then E6
        k = int(d * SR); m = n - k; tt = t[:m]
        out[k:] += (np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * 2 * f * tt)) * _env(m, .004, .16)
    return out * .6


def whoosh():
    n = int(.45 * SR)
    noise = RNG.standard_normal(n)
    out = np.zeros(n); y = 0.0
    cut = np.linspace(.04, .22, n) * np.sin(np.linspace(0, np.pi, n)) + .02   # one-pole low-pass sweeping up and down
    for i in range(n):
        y += cut[i] * (noise[i] - y); out[i] = y
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * env * 2.2


SOUNDS = {"whoosh": (whoosh(), .055, .22), "tick": (tick(), .045, 0), "pop": (pop(), .07, 0),
          "click": (click(), .10, 0), "thud": (thud(), .16, 0), "chime": (chime(), .075, 0)}
# (sound, gain relative to a voice peak of 1.0, seconds before the event where the sound peaks)


def events(starts):
    """(time in seconds, sound) for every effect, from the beat starts in beats.json."""
    s = lambda beat, u: starts[beat] + u * K
    ev = []
    for b in range(1, 6):                              # a new scene comes in (beat 1 is already up at frame 0)
        ev.append((starts[b], "whoosh"))
    ev += [(s(0, 1.05 + i * .22), "tick") for i in range(3)]            # beat 1: to-do rows
    ev += [(s(1, 1.05), "pop"), (s(1, 1.50), "pop")]                    # beat 2: call bubbles
    ev += [(s(2, 1.10), "click"), (s(2, 1.55), "click")]                # beat 3: Yes, Yes
    ev += [(s(3, 1.05 + i * .10), "tick") for i in range(5)]            # beat 4: checks resolve
    ev += [(s(3, 1.75), "thud"), (s(3, 3.0), "pop"), (s(3, 3.57), "pop"), (s(3, 3.93), "chime")]  # fail, flag, fixed, verified
    ev += [(s(4, 1.0 + i * .16), "tick") for i in range(4)]             # beat 5: report bullets
    ev += [(s(4, 2.79), "click"), (s(4, 2.86), "chime")]                # Approve go-live
    ev += [(s(5, u), "tick") for u in (1.0, 1.35, 1.95)]                # end card: chips and tag
    return ev


def mix_in(voice, starts, total):
    """voice: mono float array at SR. Returns voice (peak 1.0) + effects."""
    v = voice / (np.abs(voice).max() + 1e-9)
    out = np.zeros(int(round(total * SR)))
    out[:min(len(v), len(out))] += v[:len(out)]
    for t, name in events(starts):
        snd, gain, lead = SOUNDS[name]
        snd = snd / (np.abs(snd).max() + 1e-9) * gain
        i0 = int(round((t - lead) * SR))
        lo, hi = max(0, i0), min(len(out), i0 + len(snd))
        if hi > lo:
            out[lo:hi] += snd[lo - i0:hi - i0]
    return out, len(events(starts))
