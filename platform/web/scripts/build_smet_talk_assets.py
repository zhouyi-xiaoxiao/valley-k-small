#!/usr/bin/env python3
"""Build the figures of the 10-minute talk /talk/smet-phd/ (English and Chinese).

Standard library only. Every figure is drawn from data in this repository:

- fig1 (right) and fig4: the lazy ring of report ``ring_lazy_flux`` (N = 100,
  start 1, target 50, shortcut 6 -> 51). f(t) is recomputed here by exact
  time-stepping of the master equation, with the same transition rules as
  ``research/reports/ring_lazy_flux/code/lazy_ring_flux_bimodality.py``; the
  peak times reproduce that report's tables (t = 51 and 1021; t = 27).
- fig5: ``ring_valley_dst`` destination scan (N = 100, K = 6, start = shortcut
  source = 1, target 50), ``second_peak_dst_shortcut_usage/.../scan.csv``.
- fig6 and fig8: ``grid2d_membrane_near_target`` exact f(t) outputs, the
  classifier's peak and valley times (``summary.json``) and the window split.
- fig7: values published in ``grid2d_one_target_valley_peak_budget`` (its raw
  pipeline is not in the repository; the report's own figure script uses the
  same published numbers).

Schematic panels (fig1 left, fig3) are drawn from formulas, say "schematic" on
the figure, and carry no numbers on their axes.

The slide titles, sentences and captions live in
``public/data/v1/talks/smet-phd/manifest.json``; the figures carry only axis
labels, panel headings and short annotations.

Usage (from the repository root): python3 platform/web/scripts/build_smet_talk_assets.py
"""

from __future__ import annotations

import csv
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "research" / "reports"
ASSET_DIR = ROOT / "platform" / "web" / "public" / "talk-assets" / "smet-phd"

W = 1000
FONT = (
    "Inter, 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', "
    "'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif"
)

BG = "#fffdf8"
INK = "#18212a"
SOFT = "#4f5b63"
AXIS = "#9aa3a6"
GRID = "#ece6d8"
TEAL = "#1f7a73"
AMBER = "#c9780f"
AMBER_SOFT = "#e3a94f"
BLUE = "#2f62c9"
GREY = "#8a949a"
RED = "#c2413b"

# Font sizes chosen so that a 1000-px-wide figure stays readable when it is
# scaled to the ~340-px width of a phone screen.
F_HEAD = 32
F_LABEL = 29
F_TICK = 27
F_NOTE = 28


# --------------------------------------------------------------------------
# SVG helpers
# --------------------------------------------------------------------------


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def text(x: float, y: float, value: str, size: int = F_NOTE, weight: int = 500, fill: str = INK,
         anchor: str = "start", italic: bool = False, rotate: float | None = None) -> str:
    extra = ' font-style="italic"' if italic else ""
    if rotate is not None:
        extra += f' transform="rotate({rotate} {x:.1f} {y:.1f})"'
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{esc(FONT)}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(value)}</text>'
    )


def line(x1: float, y1: float, x2: float, y2: float, stroke: str = AXIS, width: float = 2.5,
         dash: str | None = None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
        f'stroke-width="{width}" stroke-linecap="round"{d}/>'
    )


def polyline(points: list[tuple[float, float]], stroke: str, width: float = 5, dash: str | None = None) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (
        f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"{d}/>'
    )


def dot(x: float, y: float, r: float, fill: str, stroke: str | None = None) -> str:
    s = f' stroke="{stroke}" stroke-width="3"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{s}/>'


def rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 0, stroke: str | None = None,
         dash: str | None = None, width: float = 2) -> str:
    s = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
    if dash:
        s += f' stroke-dasharray="{dash}"'
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{s}/>'


def svg_doc(height: int, body: list[str], title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
        f'<rect width="{W}" height="{height}" rx="24" fill="{BG}"/>'
        + "".join(body)
        + "</svg>"
    )


SUPERSCRIPT = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def sci(value: float) -> str:
    """0.0003 -> '3×10⁻⁴'; 0 -> '0'."""
    if value == 0:
        return "0"
    exp = int(math.floor(math.log10(abs(value))))
    mant = value / 10**exp
    mant_s = f"{mant:.0f}" if abs(mant - round(mant)) < 1e-9 else f"{mant:.1f}"
    if exp == 0:
        return mant_s
    if mant_s == "1":
        return "10" + str(exp).translate(SUPERSCRIPT)
    return f"{mant_s}×10" + str(exp).translate(SUPERSCRIPT)


def thousands(value: int) -> str:
    return f"{value:,}"


class Axes:
    """A plot box with linear y and linear or log10 x."""

    def __init__(self, x0: float, y0: float, x1: float, y1: float, xmin: float, xmax: float,
                 ymin: float, ymax: float, xlog: bool = False, ylog: bool = False):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.xlog, self.ylog = xlog, ylog

    def px(self, x: float) -> float:
        if self.xlog:
            a, b, v = math.log10(self.xmin), math.log10(self.xmax), math.log10(max(x, self.xmin))
        else:
            a, b, v = self.xmin, self.xmax, x
        return self.x0 + (v - a) / (b - a) * (self.x1 - self.x0)

    def py(self, y: float) -> float:
        if self.ylog:
            a, b, v = math.log10(self.ymin), math.log10(self.ymax), math.log10(max(y, self.ymin))
        else:
            a, b, v = self.ymin, self.ymax, y
        return self.y1 - (v - a) / (b - a) * (self.y1 - self.y0)

    def frame(self, xticks: list[tuple[float, str]], yticks: list[tuple[float, str]],
              xlabel: str, ylabel: str, ylabel_x: float | None = None) -> list[str]:
        out = []
        for v, _ in yticks:
            out.append(line(self.x0, self.py(v), self.x1, self.py(v), GRID, 1.5))
        out.append(line(self.x0, self.y1, self.x1, self.y1, AXIS, 2.5))
        out.append(line(self.x0, self.y0, self.x0, self.y1, AXIS, 2.5))
        for v, lab in xticks:
            out.append(line(self.px(v), self.y1, self.px(v), self.y1 + 8, AXIS, 2))
            out.append(text(self.px(v), self.y1 + 36, lab, F_TICK, 400, SOFT, "middle"))
        for v, lab in yticks:
            out.append(text(self.x0 - 12, self.py(v) + 9, lab, F_TICK, 400, SOFT, "end"))
        out.append(text((self.x0 + self.x1) / 2, self.y1 + 74, xlabel, F_LABEL, 500, SOFT, "middle"))
        lx = ylabel_x if ylabel_x is not None else self.x0 - 12
        out.append(text(lx, self.y0 - 18, ylabel, F_LABEL, 500, SOFT, "start" if ylabel_x is not None else "end"))
        return out


LOG_TICKS = [(1, "1"), (10, "10"), (100, "100"), (1000, "1,000"), (10000, "10,000")]


def log_samples(n: int, tmax: int, keep: list[int]) -> list[int]:
    """All t <= 150, then ~250 log-spaced points up to tmax, plus `keep`."""
    ts = set(range(1, min(n, 150) + 1))
    t = 150.0
    while t < min(n, tmax):
        t *= 10 ** 0.006
        ts.add(int(round(t)))
    ts.update(k for k in keep if 1 <= k <= n)
    return sorted(x for x in ts if x <= min(n, tmax))


def curve_points(ax: Axes, f: list[float], ts: list[int]) -> list[tuple[float, float]]:
    return [(ax.px(t), ax.py(f[t - 1])) for t in ts]


def badge(x: float, y: float, label: str) -> str:
    w = 26 + 15.5 * len(label) if label.isascii() else 30 + 26 * len(label)
    return rect(x, y - 30, w, 42, "#f3ede0", 21) + text(x + w / 2, y, label, 25, 600, "#7c5d24", "middle", True)


def marker(ax: Axes, t: int, f: float, label: str, color: str, dx: float = 0, dy: float = -22,
           anchor: str = "middle") -> list[str]:
    x, y = ax.px(t), ax.py(f)
    return [dot(x, y, 9, color, "#ffffff"), text(x + dx, y + dy, label, F_NOTE, 700, color, anchor)]


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------


def lazy_ring_fpt(model: str, p: float = 0.0, n: int = 100, q: float = 2.0 / 3.0, start: int = 0,
                  target: int = 49, u: int = 5, v: int = 50, tmax: int = 60000,
                  eps: float = 1e-12) -> tuple[list[float], list[float]]:
    """Exact f(t) on the lazy ring of report ring_lazy_flux (0-based sites).

    Every site: stay 1-q, left q/2, right q/2. At u ("selfloop"): probability p
    moves from staying to the shortcut u -> v; ("equal4"): stay, left, right
    and shortcut 1/4 each. The target absorbs. Returns f(t) for t = 1, 2, ...
    and the part of f(t) carried by walkers that have used the shortcut.
    """
    stay, half = 1.0 - q, 0.5 * q
    fresh = [0.0] * n  # shortcut not yet used
    used = [0.0] * n
    fresh[start] = 1.0
    f_all: list[float] = []
    f_used: list[float] = []
    for _ in range(tmax):
        nf, nu = [0.0] * n, [0.0] * n
        for src, dst, is_fresh in ((fresh, nf, True), (used, nu, False)):
            for i, m in enumerate(src):
                if m == 0.0:
                    continue
                if i == u and model == "selfloop":
                    moves = [(i, stay - p, False), ((i + 1) % n, half, False), ((i - 1) % n, half, False), (v, p, True)]
                elif i == u and model == "equal4":
                    moves = [(i, 0.25, False), ((i + 1) % n, 0.25, False), ((i - 1) % n, 0.25, False), (v, 0.25, True)]
                else:
                    moves = [(i, stay, False), ((i + 1) % n, half, False), ((i - 1) % n, half, False)]
                for j, w, shortcut in moves:
                    if is_fresh and shortcut:
                        nu[j] += m * w
                    else:
                        dst[j] += m * w
        f_all.append(nf[target] + nu[target])
        f_used.append(nu[target])
        nf[target] = nu[target] = 0.0
        fresh, used = nf, nu
        if sum(fresh) + sum(used) < eps:
            break
    return f_all, f_used


def strict_peaks(f: list[float], thresh: float = 1e-7, second_frac: float = 0.01) -> list[int]:
    """Report criterion: strict local maxima above thresh, at least second_frac of the highest."""
    peaks = []
    for i, value in enumerate(f):
        left = f[i - 1] if i > 0 else 0.0
        right = f[i + 1] if i + 1 < len(f) else 0.0
        if value > left and value > right and value > thresh:
            peaks.append(i + 1)
    if not peaks:
        return []
    hmax = max(f[t - 1] for t in peaks)
    return [t for t in peaks if f[t - 1] >= second_frac * hmax]


def valley_between(f: list[float], t1: int, t2: int) -> int:
    seg = f[t1: t2 - 1]
    return t1 + seg.index(min(seg)) + 1


def read_fpt_csv(path: Path) -> tuple[list[float], list[float], list[float]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    rows = [r for r in rows if int(r["t"]) >= 1]
    return ([float(r["f_total"]) for r in rows], [float(r["f_a"]) for r in rows], [float(r["f_b"]) for r in rows])


# --------------------------------------------------------------------------
# Labels
# --------------------------------------------------------------------------

L = {
    "schematic": ("Schematic, not to scale", "示意图，未按比例"),
    "schematic_shape": ("Schematic: illustrative shapes, not computed", "示意图：仅示意形状，非计算结果"),
    "time": ("time t (steps)", "时间 t（步）"),
    "time_log": ("time t (steps, log scale)", "时间 t（步，对数刻度）"),
    "time_plain": ("time t", "时间 t"),
    "ft": ("f(t) = P(T = t)", "f(t) = P(T = t)"),
    "ft_short": ("f(t)", "f(t)"),
    "peak1": ("peak 1", "峰 1"),
    "peak2": ("peak 2", "峰 2"),
    "valley": ("valley", "谷"),
    "start": ("start", "起点"),
    "target": ("target", "目标"),
    "ring_head": ("Ring with one shortcut", "带一条捷径的环"),
    "ring_fast": ("via the shortcut", "走捷径"),
    "ring_slow": ("around the ring", "沿环绕行"),
    "hero_curve_head": ("Computed f(t)", "计算所得的 f(t)"),
    "hero_curve_sub": ("same ring, shortcut taken rarely", "同一个环，捷径很少被走"),
    "single": ("Single peak", "单峰"),
    "single_sub": ("one dominant arrival time", "一个主导的到达时间"),
    "double": ("Double peak", "双峰"),
    "double_sub": ("two groups of arrival times", "两组到达时间"),
    "one_peak": ("peak", "峰"),
}


def tr(key: str, lang: str) -> str:
    en, cn = L[key]
    return cn if lang == "cn" else en


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------


def ring_point(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def ring_schematic(lang: str, cx: float, cy: float, r: float) -> list[str]:
    # Angles follow the ring of the computed example: target 49 sites from the
    # start, u 5 sites from the start, v one site beyond the target (3.6° per
    # site); the gap target-v is widened so that the two dots can be told apart.
    a_start, a_u, a_target, a_v = 180.0, 180.0 - 18.0, 180.0 - 176.4, 180.0 - 176.4 - 12.0
    s, u, t, v = (ring_point(cx, cy, r, a) for a in (a_start, a_u, a_target, a_v))
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#d5d9d6" stroke-width="10"/>']
    # around the ring: start -> target the other way (through the bottom)
    out.append(
        f'<path d="M {s[0]:.1f} {s[1]:.1f} A {r} {r} 0 0 0 {t[0]:.1f} {t[1]:.1f}" fill="none" '
        f'stroke="{AMBER_SOFT}" stroke-width="8" stroke-dasharray="18 12" stroke-linecap="round"/>'
    )
    # via the shortcut: start -> u along the ring, chord u -> v, one step back to the target
    out.append(
        f'<path d="M {s[0]:.1f} {s[1]:.1f} A {r} {r} 0 0 1 {u[0]:.1f} {u[1]:.1f}" fill="none" '
        f'stroke="{TEAL}" stroke-width="9" stroke-linecap="round"/>'
    )
    out.append(line(u[0], u[1], v[0], v[1], TEAL, 9))
    out.append(
        f'<path d="M {v[0]:.1f} {v[1]:.1f} A {r} {r} 0 0 0 {t[0]:.1f} {t[1]:.1f}" fill="none" '
        f'stroke="{TEAL}" stroke-width="9" stroke-linecap="round"/>'
    )
    out += [dot(s[0], s[1], 13, INK), dot(u[0], u[1], 10, AMBER), dot(v[0], v[1], 10, AMBER), dot(t[0], t[1], 14, BLUE)]
    out.append(text(s[0] - 20, s[1] + 10, tr("start", lang), F_NOTE, 700, INK, "end"))
    out.append(text(u[0] - 12, u[1] - 18, "u", F_NOTE, 700, AMBER, "end"))
    out.append(text(v[0] + 18, v[1] + 26, "v", F_NOTE, 700, AMBER))
    out.append(text(t[0] + 18, t[1] - 18, tr("target", lang), F_NOTE, 700, BLUE))
    return out


def build_fig1(lang: str, f: list[float], peaks: tuple[int, int, int]) -> str:
    t1, tv, t2 = peaks
    H = 600
    body: list[str] = []
    # left: schematic ring
    body.append(text(34, 58, tr("ring_head", lang), F_HEAD, 700))
    body.append(badge(34, 112, tr("schematic", lang)))
    body += ring_schematic(lang, 250, 330, 132)
    body.append(polyline([(40, 520), (110, 520)], TEAL, 9))
    body.append(text(124, 530, tr("ring_fast", lang), F_NOTE, 500, SOFT))
    body.append(polyline([(40, 566), (110, 566)], AMBER_SOFT, 8, "18 12"))
    body.append(text(124, 576, tr("ring_slow", lang), F_NOTE, 500, SOFT))
    # right: computed curve
    body.append(text(500, 58, tr("hero_curve_head", lang), F_HEAD, 700))
    body.append(text(500, 100, tr("hero_curve_sub", lang), F_NOTE, 400, SOFT))
    ymax = 3.5e-4
    ax = Axes(560, 175, 975, 470, 1, 20000, 0, ymax, xlog=True)
    body += ax.frame([(1, "1"), (100, "100"), (10000, "10,000")], [(0, "0"), (3e-4, sci(3e-4))],
                     tr("time_log", lang), tr("ft_short", lang), ylabel_x=500)
    ts = log_samples(len(f), 20000, [t1, tv, t2])
    body.append(polyline(curve_points(ax, f, ts), INK, 5))
    body += marker(ax, t1, f[t1 - 1], f"{tr('peak1', lang)} · t={t1}", TEAL, 0, -24)
    body += marker(ax, tv, f[tv - 1], f"{tr('valley', lang)} · t={tv}", SOFT, 0, 48)
    body += marker(ax, t2, f[t2 - 1], f"{tr('peak2', lang)} · t={thousands(t2)}", AMBER, 0, -24)
    title = ("Schematic ring with one shortcut, and the computed first-passage distribution with two peaks"
             if lang == "en" else "带一条捷径的环（示意）与计算所得的双峰首达时间分布")
    return svg_doc(H, body, title)


def gamma_shape(t: float, k: float, theta: float) -> float:
    if t <= 0:
        return 0.0
    return t ** (k - 1) * math.exp(-t / theta) / (math.gamma(k) * theta**k)


def build_fig3(lang: str) -> str:
    H = 600
    body: list[str] = [badge(34, 60, tr("schematic_shape", lang))]
    n = 400
    ts = [i * 0.25 for i in range(n + 1)]  # schematic time 0..100
    single = [gamma_shape(t, 4.0, 6.0) for t in ts]
    double = [0.45 * gamma_shape(t, 5.0, 2.6) + 0.55 * gamma_shape(t, 14.0, 4.2) for t in ts]
    panels = [
        (40, single, TEAL, tr("single", lang), tr("single_sub", lang)),
        (530, double, INK, tr("double", lang), tr("double_sub", lang)),
    ]
    for x0, ys, color, head, sub in panels:
        body.append(text(x0 + 8, 140, head, F_HEAD, 700))
        body.append(text(x0 + 8, 182, sub, F_NOTE, 400, SOFT))
        ymax = max(ys) * 1.25
        ax = Axes(x0 + 50, 230, x0 + 440, 520, 0, 100, 0, ymax)
        body.append(line(ax.x0, ax.y1, ax.x1, ax.y1, AXIS, 2.5))
        body.append(line(ax.x0, ax.y0, ax.x0, ax.y1, AXIS, 2.5))
        body.append(text(ax.x1, ax.y1 + 40, tr("time_plain", lang), F_LABEL, 500, SOFT, "end"))
        body.append(text(ax.x0 - 10, ax.y0 + 22, tr("ft_short", lang), F_LABEL, 500, SOFT, "end"))
        body.append(polyline([(ax.px(t), ax.py(y)) for t, y in zip(ts, ys)], color, 6))
        # markers at the computed extrema of the drawn curve
        maxima = [i for i in range(1, n) if ys[i] > ys[i - 1] and ys[i] >= ys[i + 1]]
        minima = [i for i in range(1, n) if ys[i] < ys[i - 1] and ys[i] <= ys[i + 1]]
        if len(maxima) == 1:
            i = maxima[0]
            body += [dot(ax.px(ts[i]), ax.py(ys[i]), 9, TEAL, "#ffffff"),
                     text(ax.px(ts[i]), ax.py(ys[i]) - 24, tr("one_peak", lang), F_NOTE, 700, TEAL, "middle")]
        else:
            i1, i2 = maxima[0], maxima[1]
            iv = [i for i in minima if i1 < i < i2][0]
            body += [dot(ax.px(ts[i1]), ax.py(ys[i1]), 9, TEAL, "#ffffff"),
                     text(ax.px(ts[i1]), ax.py(ys[i1]) - 24, tr("peak1", lang), F_NOTE, 700, TEAL, "middle"),
                     dot(ax.px(ts[iv]), ax.py(ys[iv]), 9, SOFT, "#ffffff"),
                     text(ax.px(ts[iv]), ax.py(ys[iv]) + 48, tr("valley", lang), F_NOTE, 700, SOFT, "middle"),
                     dot(ax.px(ts[i2]), ax.py(ys[i2]), 9, AMBER, "#ffffff"),
                     text(ax.px(ts[i2]), ax.py(ys[i2]) - 24, tr("peak2", lang), F_NOTE, 700, AMBER, "middle")]
    title = "Schematic: a single-peaked and a double-peaked first-passage distribution" if lang == "en" else "示意图：单峰与双峰的首达时间分布"
    return svg_doc(H, body, title)


def build_fig4(lang: str, eq: list[float], eq_used: list[float], sl: list[float], sl_used: list[float]) -> str:
    H = 880
    body: list[str] = []
    t_eq = strict_peaks(eq)
    assert t_eq == [27], t_eq
    late_eq = sum(eq[1000:]) / sum(eq)
    t1, t2 = strict_peaks(sl)
    tv = valley_between(sl, t1, t2)
    early_mass = sum(sl[:tv]) / sum(sl)
    early_via = sum(sl_used[:tv]) / sum(sl[:tv])
    never_at_t2 = 1.0 - sl_used[t2 - 1] / sl[t2 - 1]

    def pct(x: float) -> str:
        return f"{100 * x:.0f}%"

    if lang == "en":
        head_top = "Shortcut taken often: probability 1/4 at site 6"
        head_bot = "Shortcut taken rarely: probability 0.0067 at site 6"
        note_top = [f"one sharp peak at t = {t_eq[0]}; long tail: {pct(late_eq)} of hits come after t = 1,000"]
        note_bot = [f"before the valley (t ≤ {tv}): {pct(early_mass)} of hits, {pct(early_via)} of them via the shortcut",
                    f"at the late peak (t = {thousands(t2)}): {pct(never_at_t2)} of hits never used the shortcut"]
    else:
        head_top = "捷径常被走：第 6 格走捷径的概率为 1/4"
        head_bot = "捷径很少被走：第 6 格走捷径的概率为 0.0067"
        note_top = [f"t = {t_eq[0]} 处一个尖峰；长尾：{pct(late_eq)} 的到达发生在 t = 1,000 之后"]
        note_bot = [f"谷之前（t ≤ {tv}）：占全部到达的 {pct(early_mass)}，其中 {pct(early_via)} 走了捷径",
                    f"晚峰处（t = {thousands(t2)}）：{pct(never_at_t2)} 的到达从未走过捷径"]
    # top panel
    body.append(text(34, 50, head_top, F_HEAD, 700))
    for i, line_s in enumerate(note_top):
        body.append(text(34, 92 + 32 * i, line_s, 24, 500, SOFT))
    ax = Axes(150, 170, 960, 340, 1, 20000, 0, 0.006, xlog=True)
    body += ax.frame(LOG_TICKS, [(0, "0"), (0.005, sci(0.005))], tr("time_log", lang), tr("ft_short", lang), ylabel_x=40)
    body.append(polyline(curve_points(ax, eq, log_samples(len(eq), 20000, [27])), TEAL, 5))
    body += marker(ax, 27, eq[26], f"t={t_eq[0]}", TEAL, 18, -6, "start")
    # bottom panel
    body.append(text(34, 486, head_bot, F_HEAD, 700))
    for i, line_s in enumerate(note_bot):
        body.append(text(34, 528 + 32 * i, line_s, 24, 500, SOFT))
    ax2 = Axes(150, 640, 960, 790, 1, 20000, 0, 3.5e-4, xlog=True)
    body += ax2.frame(LOG_TICKS, [(0, "0"), (3e-4, sci(3e-4))], tr("time_log", lang), tr("ft_short", lang), ylabel_x=40)
    body.append(polyline(curve_points(ax2, sl, log_samples(len(sl), 20000, [t1, tv, t2])), INK, 5))
    body += marker(ax2, t1, sl[t1 - 1], f"t={t1}", TEAL, 0, -22)
    body += marker(ax2, tv, sl[tv - 1], f"t={tv}", SOFT, 0, 44)
    body += marker(ax2, t2, sl[t2 - 1], f"t={thousands(t2)}", AMBER, 0, -22)
    title = ("Computed first-passage distributions on the same ring for two shortcut rules: one sharp peak, or two peaks"
             if lang == "en" else "同一个环在两种捷径规则下计算所得的首达时间分布：一个尖峰，或两个峰")
    return svg_doc(H, body, title)


def build_fig5(lang: str, rows: list[dict[str, str]]) -> str:
    H = 860
    body: list[str] = []
    valid = [r for r in rows if r["valid"] == "True"]
    bim = [r for r in valid if r["bimodal"] == "True"]
    close = [r for r in bim if int(r["t2"]) - int(r["t1"]) <= 10]
    apart = [r for r in bim if int(r["t2"]) - int(r["t1"]) > 10]
    none = [r for r in valid if r["bimodal"] != "True"]
    rng = lambda rs, k: (min(int(r[k]) for r in rs), max(int(r[k]) for r in rs))  # noqa: E731
    if lang == "en":
        head_top = "Height of the second peak, by landing site"
        head_bot = "Times of the two peaks"
        ylab_top = "A(t₂)"
        xlab = "landing site of the shortcut (site number)"
        ylab_bot = "t (steps, log scale)"
        leg = [("well separated", TEAL), ("a few steps apart", GREY), ("no second peak", None)]
        tgt = "target (50)"
        n_close = f"t₁ = {rng(close, 't1')[0]}–{rng(close, 't1')[1]}, t₂ = {rng(close, 't2')[0]}–{rng(close, 't2')[1]}"
        n_apart = f"t₁ = {rng(apart, 't1')[0]}–{rng(apart, 't1')[1]}, t₂ = {rng(apart, 't2')[0]}–{rng(apart, 't2')[1]}"
        legend_bot = [("○ t₁ (first peak)", SOFT), ("● t₂ (second peak)", SOFT)]
    else:
        head_top = "第二峰的高度，按落点"
        head_bot = "两个峰出现的时间"
        ylab_top = "A(t₂)"
        xlab = "捷径的落点（格点编号）"
        ylab_bot = "t（步，对数刻度）"
        leg = [("两峰分得开", TEAL), ("两峰只差几步", GREY), ("没有第二峰", None)]
        tgt = "目标（50）"
        n_close = f"t₁ = {rng(close, 't1')[0]}–{rng(close, 't1')[1]}，t₂ = {rng(close, 't2')[0]}–{rng(close, 't2')[1]}"
        n_apart = f"t₁ = {rng(apart, 't1')[0]}–{rng(apart, 't1')[1]}，t₂ = {rng(apart, 't2')[0]}–{rng(apart, 't2')[1]}"
        legend_bot = [("○ t₁（第一峰）", SOFT), ("● t₂（第二峰）", SOFT)]
    # top
    body.append(text(34, 54, head_top, F_HEAD, 700))
    ax = Axes(150, 120, 960, 330, 1, 100, 0, 0.015)
    body += ax.frame([(1, "1"), (25, "25"), (50, "50"), (75, "75"), (100, "100")],
                     [(0, "0"), (0.01, "0.01")], xlab, ylab_top, ylabel_x=40)
    body.append(line(ax.px(50), ax.y0, ax.px(50), ax.y1, BLUE, 2.5, "8 8"))
    body.append(text(ax.px(50) + 10, ax.y0 + 6, tgt, 25, 600, BLUE))
    for r in none:
        body.append(dot(ax.px(int(r["dst"])), ax.py(0), 4.5, "#ffffff", AXIS))
    for r in close:
        body.append(dot(ax.px(int(r["dst"])), ax.py(float(r["h2"])), 8, GREY))
    for r in apart:
        body.append(dot(ax.px(int(r["dst"])), ax.py(float(r["h2"])), 8, TEAL))
    lx = 160
    for i, (lab, color) in enumerate(leg):
        y = 168 + 36 * i
        body.append(dot(lx + 8, y - 9, 8 if color else 4.5, color or "#ffffff", None if color else AXIS))
        body.append(text(lx + 26, y, lab, 25, 500, SOFT))
    # bottom
    body.append(text(34, 494, head_bot, F_HEAD, 700))
    ax2 = Axes(150, 560, 960, 760, 1, 100, 1, 200, ylog=True)
    body += ax2.frame([(1, "1"), (25, "25"), (50, "50"), (75, "75"), (100, "100")],
                      [(1, "1"), (10, "10"), (100, "100")], xlab, ylab_bot, ylabel_x=40)
    for group, color in ((close, GREY), (apart, TEAL)):
        for r in group:
            x = ax2.px(int(r["dst"]))
            body.append(line(x, ax2.py(int(r["t1"])), x, ax2.py(int(r["t2"])), color, 2))
            body.append(dot(x, ax2.py(int(r["t1"])), 7, "#ffffff", color))
            body.append(dot(x, ax2.py(int(r["t2"])), 7, color))
    body.append(text(ax2.px(59.5), ax2.py(4) + 8, n_close, 24, 600, GREY, "start"))
    body.append(text(ax2.px(50), ax2.py(170) , n_apart, 24, 600, TEAL, "middle"))
    for i, (lab, color) in enumerate(legend_bot):
        body.append(text(ax2.x1 - 4, 506 + 32 * i - 12, lab, 24, 500, color, "end"))
    title = ("Destination scan on a K = 6 ring: second-peak height and peak times against the shortcut's landing site"
             if lang == "en" else "K = 6 环上的落点扫描：第二峰高度与两峰时间随捷径落点的变化")
    return svg_doc(H, body, title)


def lattice_schematic(lang: str, x: float, y: float, two_targets: bool) -> list[str]:
    # 60 x 16 rectangle drawn at 4 px per site
    s = 4.0
    out = [rect(x, y, 60 * s, 16 * s, "#f4f1e8", 6, AXIS, None, 2)]
    mid = y + 8 * s
    if not two_targets:
        out.append(rect(x + 5 * s, mid - 2.5 * s, 50 * s, 5 * s, "#e6efe9", 0))
        out.append(line(x + 5 * s, mid - 2.5 * s, x + 55 * s, mid - 2.5 * s, TEAL, 2.5, "6 5"))
        out.append(line(x + 5 * s, mid + 2.5 * s, x + 55 * s, mid + 2.5 * s, TEAL, 2.5, "6 5"))
        out.append(dot(x + 7 * s, mid, 6, RED))
        out.append(dot(x + 58 * s, mid, 7, BLUE))
    else:
        out.append(dot(x + 7 * s, mid, 6, RED))
        out.append(dot(x + 9 * s, mid - 3 * s, 7, BLUE))
        out.append(dot(x + 58 * s, mid, 7, AMBER))
    return out


def build_fig6(lang: str, sym: list[float], sym_peaks: tuple[int, int, int], two: list[float],
               two_peaks: tuple[int, int, int], sym_mass: float, p_near: float) -> str:
    H = 860
    body: list[str] = []
    if lang == "en":
        head_top = "One target, corridor with leaky walls"
        head_bot = "Two targets, no corridor"
        sub_top = [f"wall crossing accepted with κ = 0.002; valley at t = {thousands(sym_peaks[1])}",
                   f"{sym_mass:.0%} of hits by t = 5,000 (end of the computed range)"]
        sub_bot = [f"valley at t = {two_peaks[1]}", f"near target {p_near:.0%} of hits, far target {1 - p_near:.0%}"]
    else:
        head_top = "一个目标，通道壁可渗漏"
        head_bot = "两个目标，没有通道"
        sub_top = [f"穿壁被接受的概率 κ = 0.002；谷在 t = {thousands(sym_peaks[1])}",
                   f"t = 5,000（计算范围终点）前完成 {sym_mass:.0%} 的到达"]
        sub_bot = [f"谷在 t = {two_peaks[1]}", f"近目标占 {p_near:.0%} 的到达，远目标占 {1 - p_near:.0%}"]
    for k, (head, sub, f, (t1, tv, t2), y0, two_t) in enumerate((
        (head_top, sub_top, sym, sym_peaks, 0, False),
        (head_bot, sub_bot, two, two_peaks, 430, True),
    )):
        body.append(text(34, y0 + 54, head, F_HEAD, 700))
        body += lattice_schematic(lang, 700, y0 + 18, two_t)
        body.append(text(940, y0 + 112, "schematic" if lang == "en" else "示意", 22, 600, "#7c5d24", "end", True))
        ymax = max(f) * 1.3
        ax = Axes(150, y0 + 172, 960, y0 + 336, 1, 5000, 0, ymax, xlog=True)
        ytick = 1e-3 if ymax < 0.003 else 5e-3
        body += ax.frame([(1, "1"), (10, "10"), (100, "100"), (1000, "1,000")], [(0, "0"), (ytick, sci(ytick))],
                         tr("time_log", lang), tr("ft_short", lang), ylabel_x=40)
        body.append(polyline(curve_points(ax, f, log_samples(len(f), 5000, [t1, tv, t2])), INK, 5))
        body += marker(ax, t1, f[t1 - 1], f"t={t1}", TEAL, 0, -22)
        body.append(dot(ax.px(tv), ax.py(f[tv - 1]), 9, SOFT, "#ffffff"))
        body += marker(ax, t2, f[t2 - 1], f"t={thousands(t2)}", AMBER, 0, -22)
        for i, s in enumerate(sub):
            body.append(text(34, y0 + 96 + 30 * i, s, 24, 500, SOFT))
    title = ("Computed first-passage distributions for two 2D layouts, each with two clear peaks"
             if lang == "en" else "两种二维布局计算所得的首达时间分布，各有两个清楚的峰")
    return svg_doc(H, body, title)


# Published values, report grid2d_one_target_valley_peak_budget
# (manuscript text and code/build_budget_bar_figures.py).
KAPPAS = ["0", "0.004", "0.0152"]
OUTSIDE_BUDGET = {"valley": [718, 705, 815], "peak2": [1311, 1288, 1080]}  # expected steps outside the corridor
CROSSING_PCT = {"valley": [0.0, 18.3, 49.3], "peak2": [0.0, 19.7, 53.2]}  # P(wall crossed before the hit), %


def grouped_bars(ax: Axes, groups: list[str], series: list[tuple[str, list[float]]], fmt) -> list[str]:
    out = []
    n = len(series)
    gw = (ax.x1 - ax.x0) / len(groups)
    bw = min(92, gw * 0.7 / n)
    for g, label in enumerate(groups):
        cx = ax.x0 + gw * (g + 0.5)
        out.append(text(cx, ax.y1 + 36, label, F_TICK, 500, SOFT, "middle"))
        for j, (color, values) in enumerate(series):
            v = values[g]
            x = cx - n * bw / 2 + j * bw + 4
            h = ax.y1 - ax.py(v)
            if h > 0.5:
                out.append(rect(x, ax.y1 - h, bw - 8, h, color, 4))
            out.append(text(x + (bw - 8) / 2, ax.y1 - h - 10, fmt(v), 24, 600, color, "middle"))
    return out


def build_fig7(lang: str) -> str:
    H = 860
    body: list[str] = []
    if lang == "en":
        head_top = "Steps spent outside the corridor before the hit"
        head_bot = "Probability of crossing a corridor wall before the hit"
        ylab_top = "mean steps"
        ylab_bot = "%"
        xlab = "wall permeability κ"
        legend = [("valley window", BLUE), ("late window (peak 2)", AMBER)]
    else:
        head_top = "到达前在通道外停留的步数"
        head_bot = "到达前穿过通道壁的概率"
        ylab_top = "平均步数"
        ylab_bot = "%"
        xlab = "通道壁渗透率 κ"
        legend = [("谷所在时间窗", BLUE), ("晚峰时间窗（峰 2）", AMBER)]
    lx = 600
    for i, (lab, color) in enumerate(legend):
        body.append(rect(lx, 84 + 38 * i - 22, 24, 24, color, 4))
        body.append(text(lx + 34, 84 + 38 * i, lab, 25, 500, SOFT))
    body.append(text(34, 54, head_top, F_HEAD, 700))
    ax = Axes(150, 170, 960, 340, 0, 1, 0, 1500)
    body += ax.frame([], [(0, "0"), (500, "500"), (1000, "1,000"), (1500, "1,500")], xlab, ylab_top, ylabel_x=40)
    body += grouped_bars(ax, [f"κ = {k}" for k in KAPPAS],
                         [(BLUE, OUTSIDE_BUDGET["valley"]), (AMBER, OUTSIDE_BUDGET["peak2"])],
                         lambda v: thousands(int(v)))
    body.append(text(34, 500, head_bot, F_HEAD, 700))
    ax2 = Axes(150, 590, 960, 760, 0, 1, 0, 60)
    body += ax2.frame([], [(0, "0"), (20, "20"), (40, "40"), (60, "60")], xlab, ylab_bot, ylabel_x=40)
    body += grouped_bars(ax2, [f"κ = {k}" for k in KAPPAS],
                         [(BLUE, CROSSING_PCT["valley"]), (AMBER, CROSSING_PCT["peak2"])],
                         lambda v: "0" if v == 0 else f"{v:.1f}%")
    title = ("Valley versus late window in a one-target corridor: steps outside the corridor and wall-crossing probability"
             if lang == "en" else "单目标通道中谷与晚峰时间窗的对比：通道外停留步数与穿壁概率")
    return svg_doc(H, body, title)


def build_fig8(lang: str, f: list[float], f_near: list[float], f_far: list[float], peaks: tuple[int, int, int],
               windows: list[dict[str, str]]) -> str:
    H = 860
    body: list[str] = []
    t1, tv, t2 = peaks
    if lang == "en":
        head_top = "Two targets: f(t) split by which target is hit"
        head_bot = "Share of hits in each time window"
        leg = [("all hits", INK), ("near target", BLUE), ("far target", AMBER)]
        wnames = {"peak1": "peak 1", "valley": "valley", "peak2": "peak 2"}
        near_l, far_l = "near", "far"
    else:
        head_top = "两个目标：按到达哪个目标拆分 f(t)"
        head_bot = "各时间窗内的到达占比"
        leg = [("全部到达", INK), ("近目标", BLUE), ("远目标", AMBER)]
        wnames = {"peak1": "峰 1", "valley": "谷", "peak2": "峰 2"}
        near_l, far_l = "近", "远"
    body.append(text(34, 54, head_top, F_HEAD, 700))
    for (lab, color), lx in zip(leg, (400, 570, 770)):
        body.append(polyline([(lx, 98), (lx + 36, 98)], color, 6, "10 8" if color == INK else None))
        body.append(text(lx + 46, 107, lab, 24, 500, SOFT))
    ymax = max(f) * 1.2
    ax = Axes(150, 150, 960, 340, 1, 5000, 0, ymax, xlog=True)
    body += ax.frame([(1, "1"), (10, "10"), (100, "100"), (1000, "1,000")], [(0, "0"), (5e-3, sci(5e-3))],
                     tr("time_log", lang), tr("ft_short", lang), ylabel_x=40)
    ts = log_samples(len(f), 5000, [t1, tv, t2])
    body.append(polyline(curve_points(ax, f_far, ts), AMBER, 4))
    body.append(polyline(curve_points(ax, f_near, ts), BLUE, 4))
    body.append(polyline(curve_points(ax, f, ts), INK, 3, "10 8"))
    # bottom: stacked shares
    body.append(text(34, 500, head_bot, F_HEAD, 700))
    bx0, bw = 260, 680
    for i, w in enumerate(windows):
        y = 560 + 78 * i
        near, far = float(w["near_fraction"]), float(w["far_fraction"])
        label = f"{wnames[w['window']]} (t {w['t_lo']}–{w['t_hi']})" if lang == "en" else f"{wnames[w['window']]}（t {w['t_lo']}–{w['t_hi']}）"
        body.append(text(bx0 - 14, y + 34, label, 24, 600, INK, "end"))
        body.append(rect(bx0, y, bw * near, 46, BLUE))
        body.append(rect(bx0 + bw * near, y, bw * far, 46, AMBER))
        if near >= 0.2:
            body.append(text(bx0 + 12, y + 33, f"{near_l} {100 * near:.0f}%", 24, 700, "#ffffff"))
        if far >= 0.2:
            body.append(text(bx0 + bw - 12, y + 33, f"{far_l} {100 * far:.1f}%" if far > 0.99 else f"{far_l} {100 * far:.0f}%", 24, 700, "#ffffff", "end"))
    title = ("Two targets: the early peak is near-target hits and the late peak far-target hits"
             if lang == "en" else "两个目标：早峰来自近目标，晚峰来自远目标")
    return svg_doc(H, body, title)


# --------------------------------------------------------------------------


def write(name: str, content: str) -> None:
    (ASSET_DIR / name).write_text(content, encoding="utf-8")


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    eq, eq_used = lazy_ring_fpt("equal4")
    sl, sl_used = lazy_ring_fpt("selfloop", p=0.02 * (1.0 - 2.0 / 3.0))
    t1, t2 = strict_peaks(sl)
    assert (t1, t2) == (51, 1021), (t1, t2)  # ring_lazy_flux table, beta = 0.02
    tv = valley_between(sl, t1, t2)

    scan = list(csv.DictReader((REPORTS / "ring_valley_dst" / "artifacts" / "data" / "second_peak_dst_shortcut_usage"
                                / "N100K6_n0_1_target_50_src_1" / "latest" / "scan.csv").open(encoding="utf-8")))

    mem = REPORTS / "grid2d_membrane_near_target" / "artifacts"
    summary = json.loads((mem / "data" / "summary.json").read_text(encoding="utf-8"))
    sym, _, _ = read_fpt_csv(mem / "outputs" / "membrane_rep_sym_fpt.csv")
    two, two_near, two_far = read_fpt_csv(mem / "outputs" / "two_target_rep_fpt.csv")
    rs = summary["symmetric"]["rep"]
    rt = summary["two_target_no_corridor"]["rep"]
    assert rs["phase"] == 2 and rt["phase"] == 2  # classifier: clear double peak
    sym_peaks = (rs["t_peak1"], rs["t_valley"], rs["t_peak2"])
    two_peaks = (rt["t_peak1"], rt["t_valley"], rt["t_peak2"])
    windows = list(csv.DictReader((mem / "data" / "two_target_rep_window_split.csv").open(encoding="utf-8")))

    for lang in ("en", "cn"):
        write(f"fig1-ring-hero.{lang}.svg", build_fig1(lang, sl, (t1, tv, t2)))
        write(f"fig3-single-vs-double.{lang}.svg", build_fig3(lang))
        write(f"fig4-ring-two-rules.{lang}.svg", build_fig4(lang, eq, eq_used, sl, sl_used))
        write(f"fig5-destination-scan.{lang}.svg", build_fig5(lang, scan))
        write(f"fig6-2d-layouts.{lang}.svg", build_fig6(lang, sym, sym_peaks, two, two_peaks, sum(sym), rt["p_near"]))
        write(f"fig7-outside-vs-wall.{lang}.svg", build_fig7(lang))
        write(f"fig8-two-targets.{lang}.svg", build_fig8(lang, two, two_near, two_far, two_peaks, windows))

    print(f"ring: peaks {t1}, {t2}, valley {tv}; equal4 peak {strict_peaks(eq)}")


if __name__ == "__main__":
    main()
