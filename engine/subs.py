"""Word-by-word motion subtitles (karaoke captions) drawn on every frame, on the output clock.
On by default; story.json {"subs": false} turns them off. Words pop in as they are spoken,
the current word is lime and overshoots, previous words stay cream. Never overlaps silent cards
(no words -> no captions)."""
import bisect
from .kit import W, H, VW, VY1, KALAM, LIME, CREAM, label, text_w, ease_out, K

SIZE = 62          # caption font size (design space)
Y = VY1 - 74       # baseline, bottom of the visible frame (design coords)
STROKE = 9         # ink stroke width
MAXW = 4           # words per caption chunk
BREAK_GAP = 0.55   # a word-start gap longer than this starts a new chunk
HOLD = 1.15        # how long the last chunk lingers into a pause
ALPHA = 0.97
FIT = VW - 60      # captions never wider than the visible frame


class Subs:
    def __init__(self, story, tl):
        self.on = bool(story.get("subs", True))
        self.chunks, self.t0s, self.t1s = [], [], []
        if not self.on:
            return
        words = [(w["w"], tl.out(w["t"]), s["i"]) for s in tl.T["sentences"] for w in s["words"]]
        cur = []
        for txt, t, si in words:
            if cur and (len(cur) >= MAXW or t - cur[-1][1] > BREAK_GAP or si != cur[-1][2]):
                self.chunks.append(cur); cur = []
            cur.append((txt, t, si))
        if cur:
            self.chunks.append(cur)
        for i, ch in enumerate(self.chunks):
            self.t0s.append(ch[0][1] - 0.05)
            nxt = self.chunks[i + 1][0][1] - 0.05 if i + 1 < len(self.chunks) else ch[-1][1] + HOLD
            self.t1s.append(min(nxt, ch[-1][1] + HOLD))

    def draw(self, c, t):
        if not self.chunks:
            return
        i = bisect.bisect_right(self.t0s, t) - 1
        if i < 0 or t >= self.t1s[i]:
            return
        vis = [w for w in self.chunks[i] if w[1] <= t + 1e-6]
        if not vis:
            return
        active = len(vis) - 1
        size = SIZE
        widths = [text_w(w[0], size, KALAM) for w in vis]
        gap = text_w(" ", size, KALAM)
        total = sum(widths) + gap * (len(vis) - 1)
        if total > FIT:  # shrink to fit the visible frame (portrait band)
            size *= FIT / total
            widths = [text_w(w[0], size, KALAM) for w in vis]
            gap = text_w(" ", size, KALAM)
        x = (W - (sum(widths) + gap * (len(vis) - 1))) / 2
        for j, ((txt, tw0, _), wd) in enumerate(zip(vis, widths)):
            cx = x + wd / 2
            if j == active:
                s = 1.0 + 0.15 * (1 - ease_out(K(t, tw0, 0.16)))   # pop 1.15 -> 1
                label(c, txt, cx, Y, SIZE * s, LIME, font=KALAM, align="center",
                      stroke=STROKE, skew=-0.1, alpha=ALPHA)
            else:
                label(c, txt, cx, Y, SIZE, CREAM, font=KALAM, align="center",
                      stroke=STROKE, skew=-0.1, alpha=ALPHA)
            x += wd + gap
