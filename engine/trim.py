"""Cut dead silence from the voice track to the pacing table, with 15 ms micro-fades at every cut.
Flow: align (word times on the original) -> cut -> re-align on the trimmed voice.

Pacing rules (kept pauses):
  within a sentence        <= 0.45 s keep; 0.45-0.75 -> 0.16 s
  between sentences        <= 0.45 s keep; 0.45-0.75 -> 0.30 s
  paragraph / scene break  <= 0.45 s keep; 0.45-0.75 -> 0.55 s (join gaps of 0.45 s are untouched)
  dramatic pauses          0.75-1.25 s are always kept (dramatic allowance)
  anything longer than 1.25 s -> cut to the target above
  head of the voice -> 0.25 s, tail -> 0.40 s
Only silence is ever removed: no word is cut, and the voice itself is never processed."""
import json, os
import numpy as np, soundfile as sf
from .timing import sentences, load_audio, speech_mask

SR = 48000
KEEP = 0.45
DRAM_LO, DRAM_HI = 0.75, 1.25
TGT = dict(sent=0.16, break_=0.30, para=0.55)
FADE = 0.015


def _paragraphs(script_text):
    """sentence index -> paragraph (script line) index; skips blank and '#' lines like sentences()."""
    pidx, p = [], 0
    for line in script_text.replace("\r", "").split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pidx += [p] * len(sentences(line))
        p += 1
    return pidx


def _runs(on, hop):
    idx = np.where(~on)[0]
    if not len(idx):
        return []
    splits = np.where(np.diff(idx) > 1)[0]
    bounds = np.concatenate(([0], splits + 1, [len(idx)]))
    return [(idx[a] * hop, (idx[b - 1] + 1) * hop) for a, b in zip(bounds[:-1], bounds[1:])]


def trim(P):
    from .render import voice_path
    T = json.load(open(os.path.join(P, "timing.json"), encoding="utf-8"))
    pidx = _paragraphs(open(os.path.join(P, "script.txt"), encoding="utf-8").read())
    flat = [(w["t"], s["i"]) for s in T["sentences"] for w in s["words"]]
    if not flat:
        raise SystemExit("timing.json has no words; run align first")
    vp = voice_path(P)
    x = load_audio(vp, SR)
    x16 = load_audio(vp, 16000)
    on, hop = speech_mask(x16, 16000)
    L = len(x16) / 16000
    cuts = []
    for s, e in _runs(on, hop):
        gap = e - s
        if s < 0.25:                                   # head
            if gap > 0.45: cuts.append((s, e, 0.25))
            continue
        if e > L - 0.35:                               # tail
            if gap > 0.60: cuts.append((s, e, 0.40))
            continue
        if gap <= KEEP or DRAM_LO <= gap <= DRAM_HI:
            continue                                   # natural or dramatic: keep
        prev = max((k for k, (t, _) in enumerate(flat) if t <= s + 0.02), default=None)
        nxt = min((k for k, (t, _) in enumerate(flat) if t >= e - 0.06), default=None)
        if prev is None or nxt is None:
            tgt = TGT["break_"]
        elif flat[prev][1] == flat[nxt][1]:
            tgt = TGT["sent"]
        elif pidx[flat[prev][1]] == pidx[flat[nxt][1]]:
            tgt = TGT["break_"]
        else:
            tgt = TGT["para"]
        cuts.append((s, e, tgt))
    if not cuts:
        print("trim: no dead silence found (voice already tight)"); return
    f = int(SR * FADE)
    out, cursor, after = [], 0, False
    for s, e, tgt in sorted(cuts):
        a, b = int(round(s * SR)), int(round(e * SR))
        if a <= cursor:
            continue
        pre = x[cursor:a].copy()
        if after and len(pre) > 2 * f:
            pre[:f] *= np.linspace(0, 1, f, dtype=np.float32)
        pre[-f:] *= np.linspace(1, 0, f, dtype=np.float32) if len(pre) > 2 * f else 1
        out.append(pre)
        out.append(np.zeros(int(round(tgt * SR)), dtype=np.float32))
        cursor, after = b, True
    tail = x[cursor:].copy()
    if after and len(tail) > f:
        tail[:f] *= np.linspace(0, 1, f, dtype=np.float32)
    out.append(tail)
    y = np.concatenate(out)
    os.makedirs(os.path.join(P, "work"), exist_ok=True)
    backup = os.path.join(P, "work", "voice_before_trim.wav")
    if not os.path.exists(backup):
        sf.write(backup, x, SR)                        # keep the untouched master
    for stale in ("mouth.json",):                      # mouth track is built from the old voice
        p = os.path.join(P, "work", stale)
        if os.path.exists(p):
            os.remove(p)
    sf.write(vp, y, SR)
    print(f"trim: {len(x) / SR:.1f}s -> {len(y) / SR:.1f}s, {len(cuts)} pauses cut, "
          f"{(len(x) - len(y)) / SR:.1f}s removed (backup: work/voice_before_trim.wav)")
