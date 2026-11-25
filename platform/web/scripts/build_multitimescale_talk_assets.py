#!/usr/bin/env python3
"""Build the multitimescale encounter talk data and lightweight SVG assets.

Standard library only. The SVG figures are written to
public/talk-assets/multitimescale-encounter/ (committed); the talk JSON is
written to public/data/v1/talks/multitimescale-encounter/ (generated at
prebuild, not committed).

Every curve drawn here is a schematic and is labelled as such on the figure,
except slide5-budget-vs-membrane, whose bars are the values printed in the
grid2d_one_target_valley_peak_budget report (kappa = 0.0040).
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "public" / "data" / "v1" / "talks" / "multitimescale-encounter"
ASSET_DIR = ROOT / "public" / "talk-assets" / "multitimescale-encounter"
ASSET_URL = "/talk-assets/multitimescale-encounter"
ASSET_VERSION = "20261125b"

W = 800
H = 560
FONT = "Inter, 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC', 'Microsoft YaHei', Arial, sans-serif"
INK = "#25313b"
SOFT = "#5b6670"
LINE = "#d4d8cf"
TEAL = "#0f766e"
AMBER = "#d97706"
RED = "#b91c1c"
PANEL = "#ffffff"
BG = "#f7f7f3"


# ---------------------------------------------------------------- helpers


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def svg_doc(body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" fill="none">'
        f'<rect width="{W}" height="{H}" fill="{BG}"/>{body}</svg>\n'
    )


def text(
    x: float,
    y: float,
    value: str,
    size: int = 24,
    fill: str = INK,
    weight: int = 500,
    anchor: str = "start",
    italic: bool = False,
) -> str:
    style = ' font-style="italic"' if italic else ""
    return (
        f'<text x="{x:.0f}" y="{y:.0f}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{style}>'
        f"{html.escape(value)}</text>"
    )


def lines(x: float, y: float, values: list[str], size: int = 22, fill: str = SOFT, weight: int = 500) -> str:
    gap = int(size * 1.3)
    return "".join(text(x, y + i * gap, v, size, fill, weight) for i, v in enumerate(values))


def panel(x: float, y: float, w: float, h: float) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{PANEL}" stroke="{LINE}" stroke-width="2"/>'


def gamma_pdf(t: float, k: float, theta: float) -> float:
    if t <= 0:
        return 0.0
    return math.exp((k - 1) * math.log(t) - t / theta - math.lgamma(k) - k * math.log(theta))


def sample(fn, t_max: float, n: int = 160) -> list[tuple[float, float]]:
    return [(t_max * i / n, fn(t_max * i / n)) for i in range(n + 1)]


def extrema(values: list[float]) -> tuple[list[int], list[int]]:
    maxima = [i for i in range(1, len(values) - 1) if values[i] > values[i - 1] and values[i] >= values[i + 1]]
    minima = [i for i in range(1, len(values) - 1) if values[i] < values[i - 1] and values[i] <= values[i + 1]]
    return maxima, minima


def to_screen(points, x0: float, y0: float, w: float, h: float, ymax: float | None = None):
    t_max = points[-1][0]
    top = ymax if ymax is not None else max(v for _, v in points)
    return [(x0 + w * t / t_max, y0 - h * v / top) for t, v in points]


def polyline(screen, color: str, width: float = 7, dash: str | None = None, opacity: float = 1.0) -> str:
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(screen))
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<path d="{d}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
        f'stroke-linejoin="round" fill="none" opacity="{opacity}"{extra}/>'
    )


def axes(x0: float, y0: float, w: float, h: float, x_label: str, y_label: str | None, size: int = 22) -> str:
    parts = [
        f'<path d="M {x0} {y0} H {x0 + w + 8}" stroke="{SOFT}" stroke-width="3"/>',
        f'<path d="M {x0} {y0} V {y0 - h - 12}" stroke="{SOFT}" stroke-width="3"/>',
        text(x0 + w + 8, y0 + size + 8, x_label, size, SOFT, 500, "end"),
    ]
    if y_label:
        parts.append(text(x0 + 10, y0 - h - 8, y_label, size, SOFT, 600))
    return "".join(parts)


def schematic_tag(x: float, y: float, lang: str, size: int = 20) -> str:
    return text(x, y, T[lang]["schematic"], size, "#8a6d3b", 600, "end", italic=True)


# Two-time-scale schematic used on slides 1 and 3: f(0) = 0, two complete
# local maxima, and a tail that decays to (almost) zero within the window.
def two_scale(t: float) -> float:
    return 0.45 * gamma_pdf(t, 3, 4.0) + 0.55 * gamma_pdf(t, 12, 4.5)


def double_peak_plot(x0, y0, w, h, lang, early_label, late_label, valley_label) -> str:
    pts = sample(two_scale, 110.0)
    values = [v for _, v in pts]
    maxima, minima = extrema(values)
    assert len(maxima) == 2 and len(minima) == 1, (maxima, minima)
    assert values[0] == 0.0 and values[-1] < 0.02 * max(values)
    scr = to_screen(pts, x0, y0, w, h, 1.18 * max(values))
    parts = [axes(x0, y0, w, h, T[lang]["time_t"], "f(t)"), polyline(scr, INK, 7)]
    (p1x, p1y), (vx, vy), (p2x, p2y) = scr[maxima[0]], scr[minima[0]], scr[maxima[1]]
    parts += [
        f'<circle cx="{p1x:.1f}" cy="{p1y:.1f}" r="8" fill="{TEAL}"/>',
        f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="8" fill="{SOFT}"/>',
        f'<circle cx="{p2x:.1f}" cy="{p2y:.1f}" r="8" fill="{AMBER}"/>',
        text(p1x + 14, p1y - 6, early_label, 22, TEAL, 700),
        text(vx, vy + 34, valley_label, 22, SOFT, 600, "middle"),
        text(p2x, p2y - 18, late_label, 22, AMBER, 700, "middle"),
    ]
    return "".join(parts)


T = {
    "en": {
        "schematic": "schematic",
        "time_t": "time t",
        "peak1": "peak 1",
        "peak2": "peak 2",
        "valley": "valley",
        # slide 1
        "s1_left": "Two routes",
        "s1_fast": "fast route",
        "s1_slow": "delayed route",
        "start": "start",
        "target": "target",
        "s1_note": "same start, same target",
        "s1_right": "Arrival times",
        # slide 2
        "s2_rows": [
            ("1  Mechanism", ["which routes or targets could", "create two time scales?"]),
            ("2  Decomposition", ["split f(t) by source:", "f(t) = fast part + slow part"]),
            ("3  Artifact filter", ["rule out parity combs,", "long tails and weak shoulders"]),
        ],
        # slide 3
        "s3_left": "1D ring, one shortcut",
        "shortcut": "shortcut",
        "s3_early": "via shortcut",
        "s3_late": "round the ring",
        "s3_right": "Arrival times",
        # slide 4 (deck slide 5)
        "s4_left": "One target",
        "s4_right": "Two targets",
        "s4_left_note": ["direct corridor route vs", "excursion outside it"],
        "s4_right_note": ["near target often first,", "far target later"],
        "near": "near",
        "far": "far",
        # slide 5 (deck slide 6)
        "s5_left": "Time outside the corridor",
        "s5_left_sub": "mean steps before the hit",
        "s5_right": "Membrane crossed first",
        "s5_right_sub": "probability, before the hit",
        "s5_valley": "valley",
        "s5_peak2": "2nd peak",
        "s5_note": "κ = 0.004 · values from the one-target budget report",
        # slide 6 (deck slide 7)
        "s6_rows": [
            ("Parity artifact", ["raw f(t) alternates odd/even;", "pair sums F2: one peak"]),
            ("Same-target long tail", ["one peak, then slow decay;", "meeting site does not change"]),
            ("Target-shift shoulder", ["a shoulder, no second maximum;", "meeting site shifts slightly"]),
        ],
        "t": "t",
        # slide 8 (deck slide 9)
        "s8_head": ["Model", "What splits f(t)", "Status"],
        "s8_rows": [
            (["1D ring", "+ shortcut"], ["shortcut route vs", "ring route"], ["supported"], TEAL),
            (["2D lattice,", "1 or 2 targets"], ["time outside;", "near vs far target"], ["supported after", "decomposition"], AMBER),
            (["Two walkers, 1D,", "reflecting,", "no shortcut"], ["parity, tails,", "shoulders"], ["no robust", "double peak"], RED),
        ],
    },
    "cn": {
        "schematic": "示意图",
        "time_t": "时间 t",
        "peak1": "第一峰",
        "peak2": "第二峰",
        "valley": "谷",
        "s1_left": "两条路径",
        "s1_fast": "快路径",
        "s1_slow": "慢路径",
        "start": "起点",
        "target": "目标",
        "s1_note": "同一起点，同一目标",
        "s1_right": "到达时间",
        "s2_rows": [
            ("1  机制", ["哪些路径或目标", "可能造成两个时间尺度？"]),
            ("2  分解", ["把 f(t) 按来源拆开：", "f(t) = 快的部分 + 慢的部分"]),
            ("3  排除伪迹", ["排除奇偶锯齿、", "长尾和弱肩"]),
        ],
        "s3_left": "一维环加一条捷径",
        "shortcut": "捷径",
        "s3_early": "走捷径",
        "s3_late": "绕环",
        "s3_right": "到达时间",
        "s4_left": "单目标",
        "s4_right": "双目标",
        "s4_left_note": ["沿通道直达，", "或先到通道外绕一圈"],
        "s4_right_note": ["近目标常先被击中，", "远目标较晚"],
        "near": "近",
        "far": "远",
        "s5_left": "在通道外停留的时间",
        "s5_left_sub": "击中前的平均步数",
        "s5_right": "先穿过半透膜",
        "s5_right_sub": "击中前穿过的概率",
        "s5_valley": "谷",
        "s5_peak2": "第二峰",
        "s5_note": "κ = 0.004 · 数值取自单目标时间预算报告",
        "s6_rows": [
            ("奇偶伪迹", ["原始 f(t) 奇偶步交替；", "两两相加得 F2：只有一个峰"]),
            ("同一目标的长尾", ["单峰之后缓慢衰减；", "相遇位置不变"]),
            ("目标移位形成的肩", ["只有肩，没有第二个极大值；", "相遇位置略有移动"]),
        ],
        "t": "t",
        "s8_head": ["模型", "f(t) 怎样拆分", "结论"],
        "s8_rows": [
            (["一维环", "+ 捷径"], ["走捷径 vs", "绕环"], ["成立"], TEAL),
            (["二维格点，", "一个或两个目标"], ["通道外停留时间；", "近目标 vs 远目标"], ["分解后", "成立"], AMBER),
            (["两个游走者，一维，", "反射边界，", "无捷径"], ["奇偶、长尾、", "肩"], ["没有稳健", "双峰"], RED),
        ],
    },
}


# ---------------------------------------------------------------- slides


def slide1(lang: str) -> str:
    t = T[lang]
    sx, sy, gx, gy = 90, 300, 320, 300
    body = [
        panel(20, 20, 370, 520),
        panel(410, 20, 370, 520),
        text(44, 70, t["s1_left"], 28, INK, 700),
        f'<path d="M {sx} {sy} C 150 170 260 170 {gx} {gy}" stroke="{TEAL}" stroke-width="10" stroke-linecap="round"/>',
        f'<path d="M {sx} {sy} C 110 490 300 490 {gx} {gy}" stroke="{AMBER}" '
        'stroke-width="9" stroke-linecap="round" stroke-dasharray="16 12"/>',
        f'<circle cx="{sx}" cy="{sy}" r="15" fill="{INK}"/>',
        f'<rect x="{gx - 15}" y="{gy - 15}" width="30" height="30" fill="{RED}"/>',
        text(sx - 4, sy - 30, t["start"], 22, INK, 600, "middle"),
        text(gx + 4, gy - 30, t["target"], 22, RED, 600, "middle"),
        text(205, 168, t["s1_fast"], 24, TEAL, 700, "middle"),
        text(205, 484, t["s1_slow"], 24, AMBER, 700, "middle"),
        text(44, 524, t["s1_note"], 22, SOFT),
        text(434, 70, t["s1_right"], 28, INK, 700),
        schematic_tag(760, 68, lang),
        double_peak_plot(450, 470, 290, 300, lang, t["peak1"], t["peak2"], t["valley"]),
    ]
    return svg_doc("".join(body))


def slide2(lang: str) -> str:
    t = T[lang]
    body = []
    for i, (title, sub) in enumerate(t["s2_rows"]):
        y = 20 + i * 180
        body.append(panel(20, y, 760, 160))
        cx, cy = 140, y + 80
        if i == 0:
            body.append(f'<path d="M {cx - 80} {cy + 10} C {cx - 40} {cy - 60} {cx + 40} {cy - 60} {cx + 80} {cy + 10}" stroke="{TEAL}" stroke-width="8" stroke-linecap="round"/>')
            body.append(f'<path d="M {cx - 80} {cy + 10} C {cx - 40} {cy + 70} {cx + 40} {cy + 70} {cx + 80} {cy + 10}" stroke="{AMBER}" stroke-width="8" stroke-linecap="round" stroke-dasharray="12 9"/>')
            body.append(f'<circle cx="{cx - 80}" cy="{cy + 10}" r="11" fill="{INK}"/>')
            body.append(f'<rect x="{cx + 70}" y="{cy}" width="20" height="20" fill="{RED}"/>')
        elif i == 1:
            pts1 = sample(lambda s: 0.45 * gamma_pdf(s, 3, 4.0), 110.0, 80)
            pts2 = sample(lambda s: 0.55 * gamma_pdf(s, 12, 4.5), 110.0, 80)
            tot = sample(two_scale, 110.0, 80)
            top = max(v for _, v in tot)
            for pts, color in ((pts1, TEAL), (pts2, AMBER)):
                scr = to_screen(pts, cx - 95, cy + 55, 190, 100, top)
                d = " ".join(f"L {x:.1f} {yy:.1f}" for x, yy in scr)
                body.append(f'<path d="M {cx - 95} {cy + 55} {d} L {cx + 95} {cy + 55} Z" fill="{color}" opacity="0.35"/>')
            body.append(polyline(to_screen(tot, cx - 95, cy + 55, 190, 100, top), INK, 4))
            body.append(f'<path d="M {cx - 95} {cy + 55} H {cx + 100}" stroke="{SOFT}" stroke-width="2"/>')
        else:
            # raw f(t) alternates between odd and even steps (0.8 and 0.2 of the
            # local pair sum); the red envelope is F2 = f(2n-1) + f(2n), the sum
            # of each odd/even pair, drawn on the same scale.
            env = sample(lambda s: gamma_pdf(s, 4, 6.0), 100.0, 40)
            top = max(v for _, v in env) * 1.12
            comb = [(s, v * (0.8 if k % 2 == 0 else 0.2)) for k, (s, v) in enumerate(env)]
            body.append(polyline(to_screen(comb, cx - 95, cy + 55, 190, 100, top), INK, 2.5))
            body.append(polyline(to_screen(env, cx - 95, cy + 55, 190, 100, top), RED, 6))
            body.append(text(cx - 10, cy - 34, "F2", 18, RED, 700))
            body.append(text(cx + 30, cy + 2, "f(t)", 18, INK, 600))
            body.append(f'<path d="M {cx - 95} {cy + 55} H {cx + 100}" stroke="{SOFT}" stroke-width="2"/>')
        body.append(text(280, y + 56, title, 30, INK, 700))
        body.append(lines(280, y + 96, sub, 24))
    body.append(schematic_tag(764, 54, lang, 18))
    return svg_doc("".join(body))


def ring_point(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def slide3(lang: str) -> str:
    t = T[lang]
    cx, cy, r = 205, 300, 140
    start = ring_point(cx, cy, r, 200)
    u = ring_point(cx, cy, r, 228)
    target = ring_point(cx, cy, r, -10)
    v = ring_point(cx, cy, r, 8)
    mx, my = (u[0] + v[0]) / 2, (u[1] + v[1]) / 2
    ang = math.atan2(v[1] - u[1], v[0] - u[0])
    head = [
        (mx + 16 * math.cos(ang), my + 16 * math.sin(ang)),
        (mx - 10 * math.cos(ang) + 11 * math.sin(ang), my - 10 * math.sin(ang) - 11 * math.cos(ang)),
        (mx - 10 * math.cos(ang) - 11 * math.sin(ang), my - 10 * math.sin(ang) + 11 * math.cos(ang)),
    ]
    head_d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(head)) + " Z"
    body = [
        panel(20, 20, 370, 520),
        panel(410, 20, 370, 520),
        text(44, 70, t["s3_left"], 28, INK, 700),
        f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="#c7ccc9" stroke-width="8"/>',
        # delayed route: the long way round (counter-clockwise on screen), dashed
        f'<path d="M {start[0]:.1f} {start[1]:.1f} A {r} {r} 0 1 0 {target[0]:.1f} {target[1]:.1f}" '
        f'stroke="{AMBER}" stroke-width="7" stroke-dasharray="14 10" stroke-linecap="round"/>',
        # fast route: start -> u along the ring, shortcut u -> v, v -> target
        f'<path d="M {start[0]:.1f} {start[1]:.1f} A {r} {r} 0 0 1 {u[0]:.1f} {u[1]:.1f}" stroke="{TEAL}" stroke-width="9" stroke-linecap="round"/>',
        f'<path d="M {u[0]:.1f} {u[1]:.1f} L {v[0]:.1f} {v[1]:.1f}" stroke="{TEAL}" stroke-width="9" stroke-linecap="round"/>',
        f'<path d="M {v[0]:.1f} {v[1]:.1f} A {r} {r} 0 0 0 {target[0]:.1f} {target[1]:.1f}" stroke="{TEAL}" stroke-width="9" stroke-linecap="round"/>',
        f'<path d="{head_d}" fill="{TEAL}"/>',
        f'<circle cx="{start[0]:.1f}" cy="{start[1]:.1f}" r="14" fill="{INK}"/>',
        f'<rect x="{target[0] - 14:.1f}" y="{target[1] - 14:.1f}" width="28" height="28" fill="{RED}"/>',
        text(start[0] - 20, start[1] + 44, t["start"], 22, INK, 600, "middle"),
        text(target[0] - 6, target[1] - 26, t["target"], 22, RED, 600, "middle"),
        text(mx + 6, my - 22, t["shortcut"], 22, TEAL, 700, "middle"),
        f'<path d="M 44 470 H 92" stroke="{TEAL}" stroke-width="8" stroke-linecap="round"/>',
        text(102, 478, t["s3_early"], 22, SOFT),
        f'<path d="M 44 508 H 92" stroke="{AMBER}" stroke-width="7" stroke-dasharray="12 8" stroke-linecap="round"/>',
        text(102, 516, t["s3_late"], 22, SOFT),
        text(434, 70, t["s3_right"], 28, INK, 700),
        schematic_tag(760, 68, lang),
        double_peak_plot(450, 470, 290, 300, lang, t["s3_early"], t["s3_late"], t["valley"]),
    ]
    return svg_doc("".join(body))


def grid_lines(x0: float, y0: float, x1: float, y1: float, step: float) -> str:
    out = []
    x = x0
    while x <= x1 + 0.1:
        out.append(f'<path d="M {x:.0f} {y0} V {y1}" stroke="#e3e7e0" stroke-width="2"/>')
        x += step
    y = y0
    while y <= y1 + 0.1:
        out.append(f'<path d="M {x0} {y:.0f} H {x1}" stroke="#e3e7e0" stroke-width="2"/>')
        y += step
    return "".join(out)


def slide4(lang: str) -> str:
    t = T[lang]
    body = [
        panel(20, 20, 370, 520),
        panel(410, 20, 370, 520),
        text(44, 70, t["s4_left"], 28, INK, 700),
        text(434, 70, t["s4_right"], 28, INK, 700),
        schematic_tag(760, 68, lang),
        grid_lines(44, 100, 366, 420, 32),
        grid_lines(434, 100, 756, 420, 32),
        # one target: corridor band with membrane walls
        '<rect x="60" y="236" width="290" height="64" fill="#d7ebe7" opacity="0.9"/>',
        f'<path d="M 60 236 H 350" stroke="{INK}" stroke-width="5" stroke-dasharray="10 7"/>',
        f'<path d="M 60 300 H 350" stroke="{INK}" stroke-width="5" stroke-dasharray="10 7"/>',
        f'<path d="M 86 268 H 318" stroke="{TEAL}" stroke-width="9" stroke-linecap="round"/>',
        f'<path d="M 120 268 C 120 150 250 120 290 170 C 320 210 330 240 330 262" stroke="{AMBER}" '
        'stroke-width="8" stroke-dasharray="14 10" stroke-linecap="round"/>',
        '<circle cx="80" cy="268" r="14" fill="#25313b"/>',
        f'<rect x="318" y="254" width="28" height="28" fill="{RED}"/>',
        lines(44, 470, t["s4_left_note"], 22),
        # two targets
        '<circle cx="470" cy="270" r="14" fill="#25313b"/>',
        f'<rect x="580" y="186" width="28" height="28" fill="{RED}"/>',
        f'<rect x="708" y="338" width="28" height="28" fill="{RED}"/>',
        f'<path d="M 484 262 C 520 220 550 200 576 200" stroke="{TEAL}" stroke-width="9" stroke-linecap="round"/>',
        f'<path d="M 484 280 C 560 380 640 380 704 354" stroke="{AMBER}" stroke-width="8" stroke-dasharray="14 10" stroke-linecap="round"/>',
        text(594, 176, t["near"], 22, TEAL, 700, "middle"),
        text(722, 394, t["far"], 22, AMBER, 700, "middle"),
        lines(434, 470, t["s4_right_note"], 22),
    ]
    return svg_doc("".join(body))


def bar_pair(x0: float, base: float, h: float, values: list[float], vmax: float, labels: list[str], shown: list[str]) -> str:
    parts = [f'<path d="M {x0 - 10} {base} H {x0 + 290}" stroke="{SOFT}" stroke-width="3"/>']
    for i, (val, lab, shw) in enumerate(zip(values, labels, shown)):
        bx = x0 + 30 + i * 140
        bh = h * val / vmax
        color = SOFT if i == 0 else AMBER
        parts.append(f'<rect x="{bx}" y="{base - bh:.1f}" width="90" height="{bh:.1f}" fill="{color}" opacity="0.9"/>')
        parts.append(text(bx + 45, base - bh - 12, shw, 26, INK, 700, "middle"))
        parts.append(text(bx + 45, base + 32, lab, 22, SOFT, 600, "middle"))
    return "".join(parts)


def slide5(lang: str) -> str:
    t = T[lang]
    # grid2d_one_target_valley_peak_budget, kappa = 0.0040: outside budget
    # 705 -> 1288 steps; membrane-crossing probability about 18% -> 20%.
    body = [
        panel(20, 20, 370, 480),
        panel(410, 20, 370, 480),
        text(44, 66, t["s5_left"], 26, INK, 700),
        text(44, 98, t["s5_left_sub"], 22, SOFT),
        text(434, 66, t["s5_right"], 26, INK, 700),
        text(434, 98, t["s5_right_sub"], 22, SOFT),
        bar_pair(60, 430, 270, [705, 1288], 1300, [t["s5_valley"], t["s5_peak2"]], ["705", "1,288"]),
        bar_pair(450, 430, 270, [0.18, 0.20], 1.0, [t["s5_valley"], t["s5_peak2"]], ["18%", "20%"]),
        text(450, 160, "100%", 18, SOFT, 500),
        '<path d="M 440 160 H 740" stroke="#e3e7e0" stroke-width="2" stroke-dasharray="6 6"/>',
        text(20, 536, t["s5_note"], 20, SOFT),
    ]
    return svg_doc("".join(body))


def slide6(lang: str) -> str:
    t = T[lang]
    body = []

    def tail(s: float) -> float:
        return 0.8 * gamma_pdf(s, 3, 4.0) + 0.2 * gamma_pdf(s, 1.6, 30.0)

    def shoulder(s: float) -> float:
        return 0.8 * gamma_pdf(s, 4, 5.0) + 0.2 * gamma_pdf(s, 16, 2.6)

    for i, (title, sub) in enumerate(t["s6_rows"]):
        y = 20 + i * 180
        body.append(panel(20, y, 760, 160))
        x0, base, w, h = 50, y + 128, 290, 92
        body.append(f'<path d="M {x0} {base} H {x0 + w + 8}" stroke="{SOFT}" stroke-width="3"/>')
        body.append(text(x0 + w + 14, base + 8, t["t"], 22, SOFT, 600))
        if i == 0:
            # raw f(t): odd and even steps alternate (0.8 and 0.2 of the pair
            # sum); red: F2 = f(2n-1) + f(2n), the sum of each pair, same scale.
            env = sample(lambda s: gamma_pdf(s, 5, 6.0), 100.0, 44)
            top = max(v for _, v in env) * 1.12
            comb = [(s, v * (0.8 if k % 2 == 0 else 0.2)) for k, (s, v) in enumerate(env)]
            body.append(polyline(to_screen(comb, x0, base, w, h, top), INK, 2.5))
            body.append(polyline(to_screen(env, x0, base, w, h, top), RED, 6))
            body.append(text(x0 + 0.24 * w + 24, base - h + 6, "F2", 18, RED, 700))
            body.append(text(x0 + 0.24 * w + 50, base - 0.55 * h, "f(t)", 18, INK, 600))
        elif i == 1:
            pts = sample(tail, 160.0)
            body.append(polyline(to_screen(pts, x0, base, w, h), TEAL, 6))
        else:
            pts = sample(shoulder, 100.0)
            vals = [v for _, v in pts]
            maxima, _ = extrema(vals)
            assert len(maxima) == 1, maxima  # shoulder only: no second maximum
            body.append(polyline(to_screen(pts, x0, base, w, h), AMBER, 6))
        body.append(schematic_tag(764, y + 34, lang, 18))
        body.append(text(390, y + 56, title, 28, INK, 700))
        body.append(lines(390, y + 94, sub, 22))
    return svg_doc("".join(body))


def slide8(lang: str) -> str:
    t = T[lang]
    cols = [40, 290, 560]
    body = [text(x, 44, head, 22, SOFT, 700) for x, head in zip(cols, t["s8_head"])]
    for i, (model, split, status, color) in enumerate(t["s8_rows"]):
        y = 64 + i * 164
        body.append(panel(20, y, 760, 148))
        body.append(lines(cols[0], y + 46, model, 24, INK, 700))
        body.append(lines(cols[1], y + 46, split, 24, SOFT, 500))
        body.append(f'<rect x="{cols[2] - 8}" y="{y + 24}" width="216" height="{28 + 34 * len(status)}" rx="16" fill="{color}" opacity="0.14" stroke="{color}" stroke-width="2"/>')
        for k, s in enumerate(status):
            body.append(text(cols[2] + 100, y + 60 + 34 * k, s, 24, color, 700, "middle"))
    return svg_doc("".join(body))


SVG_BUILDERS = {
    "slide1-hidden-routes": slide1,
    "slide2-evidence-grammar": slide2,
    "slide3-ring-shortcut": slide3,
    "slide4-grid2d-targets": slide4,
    "slide5-budget-vs-membrane": slide5,
    "slide6-encounter-guardrail": slide6,
    "slide8-evidence-map": slide8,
}


def build_svgs() -> None:
    for name, builder in SVG_BUILDERS.items():
        write(ASSET_DIR / f"{name}.svg", builder("en"))
        write(ASSET_DIR / f"{name}.cn.svg", builder("cn"))


def asset(name: str, lang: str = "en") -> str:
    suffix = ".cn.svg" if lang == "cn" else ".svg"
    return f"{ASSET_URL}/{name}{suffix}?v={ASSET_VERSION}"


def image(name: str, alt_en: str, alt_cn: str) -> dict:
    return {
        "kind": "image",
        "src": asset(name),
        "src_cn": asset(name, "cn"),
        "alt_en": alt_en,
        "alt_cn": alt_cn,
        "caption_en": "",
        "caption_cn": "",
        "show_overlay": True,
        "hide_caption": True,
    }


# ---------------------------------------------------------------- talk data
#
# Scope of the scientific statements (checked against research/reports):
# - ring: final_multitimescale_fpt_encounter manuscript, "1D Shortcut Ring"
#   (lazy ring, reference N = 100, start 1, target 51, shortcut 6 -> 52,
#   beta = 0.01; useful beta window about 0.0005-0.05 at N = 100).
# - one-target 2D budgets: grid2d_one_target_valley_peak_budget manuscript
#   (kappa = 0.0040: outside budget 705 -> 1288 steps, crossing probability
#   about 18% -> 20%, valley vs second-peak window).
# - encounter: final_multitimescale_fpt_encounter
#   artifacts/encounter_search/results/final_report.md (two lazy walkers,
#   finite 1D reflecting lattice, synchronous update, co-location only,
#   no shortcut, exact absorbing chain, N = 15, 21, 31; robust F2 double
#   peaks found: 0). Other encounter models report double peaks: the
#   drifted ring with a shortcut (ring_two_walker_encounter_shortcut,
#   is_bimodal from beta = 0.15) and the 2D lattice with shortcuts
#   (grid2d_two_walker_encounter_shortcut, beta = 0.30-0.60, valley ratio
#   0.80-0.90, i.e. weak).


def slide(
    order: int,
    sid: str,
    start: str,
    end: str,
    kicker: tuple[str, str],
    title: tuple[str, str],
    sentence: tuple[str, str],
    question: tuple[str, str],
    **extra: object,
) -> dict:
    payload = {
        "id": sid,
        "order": order,
        "start": start,
        "end": end,
        "kicker_en": kicker[0],
        "kicker_cn": kicker[1],
        "title": title[0],
        "title_en": title[0],
        "title_cn": title[1],
        "sentence": sentence[0],
        "sentence_en": sentence[0],
        "sentence_cn": sentence[1],
        "question_en": question[0],
        "question_cn": question[1],
    }
    payload.update(extra)
    return payload


def link(label_en: str, label_cn: str, href: str) -> dict:
    return {"label_en": label_en, "label_cn": label_cn, "href": href}


def build_talk_data() -> None:
    slides = [
        slide(
            1, "opening", "0:00", "0:50",
            ("The question", "问题"),
            ("Double peaks are evidence, not decoration", "双峰是证据，不是装饰"),
            (
                "The first-passage distribution f(t), the probability that a random walker first reaches a target at step t, can reveal hidden route families, but only after artifacts are ruled out.",
                "首达时间分布 f(t) 是随机游走者在第 t 步首次到达目标的概率。它能揭示隐藏的路径族，但前提是先排除伪迹。",
            ),
            ("What would make a second peak trustworthy?", "什么条件下第二峰才可信？"),
            evidence=image(
                "slide1-hidden-routes",
                "Schematic: a fast route and a delayed route from the same start to the same target, and a first-passage curve f(t) with two peaks and a valley.",
                "示意图：同一起点到同一目标的快路径和慢路径，以及有两个峰和一个谷的首达时间曲线 f(t)。",
            ),
            links=[link("Read the book chapters", "阅读图谱章节", "/book/")],
        ),
        slide(
            2, "evidence-grammar", "0:50", "1:55",
            ("Evidence rules", "证据规则"),
            ("A peak is a claim that needs a ledger", "每个峰都是一项论断，要拿出证据"),
            (
                "Three checks: a mechanism, a decomposition of f(t) into its sources, and an artifact filter. Shape alone is not enough.",
                "三项检查：提出机制；把 f(t) 按来源分解；排除伪迹。只看形状不够。",
            ),
            ("Can we say what generated the curve?", "能说清这条曲线是怎么来的吗？"),
            evidence=image(
                "slide2-evidence-grammar",
                "Schematic: three checks, namely a mechanism, a decomposition of f(t) into a fast and a slow part, and an artifact filter that rules out parity combs (raw f(t) alternating between odd and even steps; the red line is the pair sum F2), long tails and weak shoulders.",
                "示意图：三项检查，即机制；把 f(t) 分解为快、慢两部分；排除奇偶锯齿（原始 f(t) 在奇、偶步之间交替，红线是两两相加得到的 F2）、长尾和弱肩等伪迹。",
            ),
        ),
        slide(
            3, "ring-shortcut", "1:55", "3:05",
            ("1D ring with a shortcut", "一维环与捷径"),
            ("The ring gives the cleanest positive mechanism", "环模型给出最清楚的正面机制"),
            (
                "On a lazy ring with one target and one directed shortcut (reference case N = 100 sites, start 1, target 51, shortcut 6 → 52, shortcut strength β = 0.01), paths through the shortcut arrive early and paths round the ring arrive late. Too small or too large a β removes one of the two peaks.",
                "环上有一个目标和一条有向捷径，游走者做懒惰随机游走（参考情形：N = 100 个格点，起点 1，目标 51，捷径 6 → 52，捷径强度 β = 0.01），走捷径的路径早到，绕环的路径晚到。β 太小或太大，都会让两个峰中的一个消失。",
            ),
            ("When does a shortcut split rather than smear the arrivals?", "捷径什么时候会把到达时间分成两群，而不是抹平？"),
            evidence=image(
                "slide3-ring-shortcut",
                "Schematic: a ring with start, target and a directed shortcut; the shortcut route gives the early peak of f(t), the route round the ring gives the late peak.",
                "示意图：带起点、目标和一条有向捷径的环；走捷径对应 f(t) 的早峰，绕环对应晚峰。",
            ),
            links=[link("Ring shortcut report", "环上捷径报告", "/reports/ring_lazy_jump_ext_rev2/")],
        ),
        slide(
            4, "grid2d-live-hop", "3:05", "4:05",
            ("The basic process", "基本过程"),
            ("Before the curve, there is a live 2D walk", "曲线之前，先看一次二维游走"),
            (
                "The walker moves one nearest-neighbour step at a time and stops when it first reaches a target; f(t) is the probability that this first arrival happens at step t.",
                "游走者每次走到一个最近邻格点，第一次到达目标就停下；f(t) 是这次首次到达发生在第 t 步的概率。",
            ),
            ("What exactly is being counted when the curve rises?", "曲线升高时，我们到底在数什么？"),
            animation={"kind": "grid-hop-lab"},
        ),
        slide(
            5, "grid2d-competition", "4:05", "5:05",
            ("2D lattice", "二维格点"),
            ("On a 2D lattice, route competition becomes geometry", "在二维格点上，路径竞争变成几何问题"),
            (
                "With one target, a late arrival can come from an excursion outside a corridor; with two targets, it can come from the far target. A second peak has to be traced to a route, a target, or both.",
                "只有一个目标时，晚到可能来自先离开通道、在外面绕一圈；有两个目标时，晚到可能来自远处的目标。第二峰必须追溯到某条路径、某个目标，或两者兼有。",
            ),
            ("Is the second peak a route, a target, or both?", "第二峰来自路径、目标，还是两者都有？"),
            evidence=image(
                "slide4-grid2d-targets",
                "Schematic: left, one target with a corridor, a direct route along it and an excursion outside it; right, two targets, a near one reached early and a far one reached later.",
                "示意图：左为单目标，沿通道直达或先到通道外绕行；右为双目标，近目标较早到达，远目标较晚。",
            ),
            links=[
                link("2D lattice: corridor membranes and two targets", "二维格点：通道半透膜与双目标", "/reports/grid2d_membrane_near_target/"),
                link("2D lattice: two targets", "二维格点：双目标", "/reports/grid2d_two_target_double_peak/"),
            ],
        ),
        slide(
            6, "budget-vs-membrane", "5:05", "6:10",
            ("One-target mechanism", "单目标机制"),
            ("Time spent outside the corridor separates the valley from the second peak", "在通道外停留的时间把谷和第二峰分开"),
            (
                "In the one-target 2D lattice with a permeable membrane (permeability κ = 0.004), paths that hit in the second-peak window spent on average about 1,290 steps outside the central corridor, against about 705 for the valley window; the probability of having crossed the membrane was close (20% against 18%).",
                "在带半透膜的单目标二维格点上（渗透率 κ = 0.004），在第二峰时间窗内击中的路径，平均在中央通道外停留约 1,290 步，谷时间窗内约 705 步；而先穿过半透膜的概率相差不大（20% 对 18%）。",
            ),
            ("What are the late paths doing between the peaks?", "两个峰之间，晚到的路径在做什么？"),
            evidence=image(
                "slide5-budget-vs-membrane",
                "Bar charts at κ = 0.004: mean steps outside the corridor before the hit, 705 in the valley window and 1,288 in the second-peak window; probability of crossing the membrane first, 18% and 20%.",
                "κ = 0.004 时的柱状图：击中前在通道外的平均步数，谷时间窗 705，第二峰时间窗 1,288；先穿过半透膜的概率分别为 18% 和 20%。",
            ),
            links=[link("One-target budget report", "单目标时间预算报告", "/reports/grid2d_one_target_valley_peak_budget/")],
        ),
        slide(
            7, "encounter-guardrail", "6:10", "7:30",
            ("Negative result", "负结果"),
            ("The encounter model is the guardrail", "相遇模型是一道护栏"),
            (
                "In an exact (no Monte Carlo) model of two lazy walkers on a finite 1D reflecting lattice with no shortcut (synchronous steps, meeting means sharing a site, N = 15, 21, 31), no scanned case gave a robust double peak in F2, the first-encounter distribution with odd and even steps paired. Apparent second bumps were parity artifacts, long tails or weak shoulders. Other encounter models do report double peaks: two walkers drifting in opposite directions on a ring with a shortcut (a clear double peak from shortcut strength β ≈ 0.15), and on a 2D lattice with shortcuts (a weak one: the valley is 80–90% of the peak). The negative result is specific to the model above.",
                "在一个精确计算（不用蒙特卡洛）的模型里：两个懒惰游走者在有限长、反射边界、无捷径的一维格点上同步行走，走到同一格点即算相遇，N = 15、21、31。所有扫描情形中，F2（把奇、偶步两两合并后的首次相遇分布）都没有出现稳健的双峰；看上去像第二峰的凸起，其实是奇偶伪迹、长尾或弱肩。其他相遇模型确实报告了双峰：环上两个漂移方向相反的游走者，加一条捷径（捷径强度 β 约 0.15 起出现清晰的双峰）；以及带捷径的二维格点（双峰很弱：谷是峰高的 80%–90%）。这个负结果只针对上面这个模型。",
            ),
            ("Which apparent late features should be rejected?", "哪些看似晚峰的特征应该被否定？"),
            evidence=image(
                "slide6-encounter-guardrail",
                "Schematic of three rejected shapes: a parity comb (raw f(t) alternating between odd and even steps) whose pair sums F2 = f(2n−1) + f(2n), the red line, have one peak; a single peak with a long tail; a shoulder with no second maximum.",
                "示意图，三种被否定的形状：奇偶锯齿（原始 f(t) 在奇、偶步之间交替），两两相加得到的 F2 = f(2n−1) + f(2n)（红线）只有一个峰；单峰加长尾；只有肩、没有第二个极大值。",
            ),
            links=[
                link("Exact encounter report", "精确相遇报告", "/reports/final_multitimescale_fpt_encounter/"),
                link("Ring encounter with a shortcut", "环上相遇（带捷径）", "/reports/ring_two_walker_encounter_shortcut/"),
                link("2D encounter with shortcuts", "二维格点相遇（带捷径）", "/reports/grid2d_two_walker_encounter_shortcut/"),
            ],
        ),
        slide(
            8, "mechanism-lab", "7:30", "8:50",
            ("Schematic explorer", "交互示意"),
            ("Try the evidence rules", "试一试这套证据规则"),
            (
                "Switch among the ring, 2D lattice and encounter cases to see which evidence each one needs before a second peak counts.",
                "在环、二维格点和相遇三种情形之间切换，看每种情形要拿出什么证据，第二峰才算数。",
            ),
            ("What evidence does each case need?", "每种情形需要什么证据？"),
            animation={"kind": "mechanism-lab"},
        ),
        slide(
            9, "final-map", "8:50", "10:00",
            ("Summary", "总结"),
            ("The output is a set of evidence rules", "最终产出是一套证据规则"),
            (
                "The question is no longer only where double peaks appear, but when a peak deserves a mechanism claim, when it needs more decomposition, and when it should be rejected.",
                "问题不再只是双峰出现在哪里，而是一个峰什么时候值得作为机制来陈述，什么时候还需要进一步分解，什么时候应当否定。",
            ),
            ("What should the next experiment show before it claims a double peak?", "下一组计算在宣称双峰之前，需要先证明什么？"),
            evidence=image(
                "slide8-evidence-map",
                "Summary table: 1D ring with a shortcut, mechanism supported; 2D lattice with one or two targets, supported after decomposition; two walkers on a 1D reflecting lattice without a shortcut, no robust double peak.",
                "总结表：一维环加捷径，机制成立；一个或两个目标的二维格点，分解后成立；无捷径、反射边界一维格点上的两个游走者，没有稳健双峰。",
            ),
            links=[
                link("Book chapters", "图谱章节", "/book/"),
                link("All reports", "全部报告", "/reports/"),
                link(
                    "Atlas home · paper submitted to Physical Review E, Jul 2026",
                    "图谱首页 · 2026 年 7 月投稿《物理评论 E》的论文",
                    "/",
                ),
            ],
        ),
    ]

    manifest = {
        "talk_id": "multitimescale-encounter",
        "title_en": "Hidden Routes, Real Peaks",
        "title_cn": "隐藏路径与真实双峰",
        "subtitle_en": "When a double peak in a first-passage-time distribution counts as evidence: ring shortcuts, 2D lattices and exact encounter checks",
        "subtitle_cn": "首达时间分布里的双峰什么时候算证据：环上捷径、二维格点与精确相遇核对",
        "audience_en": "Research audience across disciplines",
        "audience_cn": "面向不同方向的研究者",
        "occasion_en": "Interactive 10-minute talk · Xiaoxiao Zhouyi · web slides prepared in May 2026",
        "occasion_cn": "十分钟交互式报告 · 周易潇潇 · 网页幻灯 2026 年 5 月制作",
        "duration_minutes": 10,
        "theme_en": "Mechanism evidence, not shape-chasing",
        "theme_cn": "讲机制证据，不追逐形状",
        "slides": slides,
    }

    en_blocks = [
        (
            "I want to make one claim precise. The first-passage distribution f(t) is the probability that a random walker first reaches a target at step t. A double peak in f(t) can be evidence for hidden route families, but it is not evidence by itself. The rest of the talk is about what has to hold before I trust the shape.",
            "Frame: positive mechanisms, then controls.",
            "Define f(t) and state the evidence-not-decoration frame.",
        ),
        (
            "I use three checks. First, propose a mechanism. Second, decompose the curve so that each part of the probability has a source. Third, run an artifact filter. Without all three, a second peak is only a visual clue.",
            "The three checks are the scoring rule for the rest of the talk.",
            "Define mechanism, decomposition, artifact filter.",
        ),
        (
            "On the ring the mechanism is clean. A shortcut creates a fast branch, while the ordinary route round the ring still carries delayed probability. The question is not whether a shortcut exists, but whether the two route families stay separated in time and both carry enough weight to be visible. If the shortcut is almost never used there is no early peak; if it is used too often the late peak fades into a shoulder.",
            "This is the positive example before the cautionary part.",
            "Use the ring as the simplest positive case.",
        ),
        (
            "Before one target, two targets or time budgets, here is the basic process: a walker on a two-dimensional lattice, making one nearest-neighbour jump at a time and stopping when it first reaches a target. f(t) is the probability that this first arrival happens at step t. Repeating the walk many times estimates it; the curves in the reports are computed directly from the transition probabilities.",
            "Let the animation run for a few seconds, then switch the target count or the drift once.",
            "Show the lattice walk and what f(t) counts.",
        ),
        (
            "Once the local process is clear, the double-peak language gets richer. A second feature can come from a route, from a target, or from a route-target pair, so the 2D work keeps geometry and target count in view instead of reading everything off one curve.",
            "Move from the live process to spatial mechanisms.",
            "Explain route versus target competition.",
        ),
        (
            "The one-target lattice sharpened the mechanism test. At membrane permeability 0.004, paths that hit in the second-peak window spent on average about 1,290 steps outside the central corridor, against about 705 for the valley window, while the chance of having crossed the membrane was 20% against 18%. The delayed paths are not just crossing a boundary; they spend longer in a different part of the lattice.",
            "Two numbers carry the slide: about 705 against 1,290 steps outside, and 18% against 20% crossing.",
            "Compare time outside the corridor with membrane crossing.",
        ),
        (
            "The exact encounter model matters because its answer is no. For two lazy walkers on a finite one-dimensional reflecting lattice without a shortcut, moving synchronously and meeting only by sharing a site, with N = 15, 21 or 31, none of the scanned cases gives a robust double peak in F2, the distribution with odd and even steps paired. The unusual shapes are parity artifacts, same-target long tails or weak target-shift shoulders. This is limited to that model; other encounter models, a drifted ring with a shortcut and a 2D lattice with shortcuts, do give double peaks, clear on the ring and weak in 2D.",
            "State the negative result with its scope: no shortcut, 1D reflecting, synchronous, co-location, N = 15, 21, 31.",
            "State the negative result and its scope.",
        ),
        (
            "This panel is a schematic summary, not computed data. The ring case is a supported mechanism. The 2D case needs a decomposition before the second peak counts. The encounter case is the guardrail: after pairing odd and even steps (F2), what remains is one peak with a long tail or a weak shoulder, never a robust second peak.",
            "Switch between the three cases once while speaking.",
            "Demonstrate the case selector.",
        ),
        (
            "So the work has a different output. It is not simply a list of double peaks. It is a set of rules for when a double peak deserves a mechanism claim, when it needs more decomposition, and when it should be rejected.",
            "Close: the deliverable is a rule for when a peak earns a mechanism claim.",
            "Close on the evidence rules.",
        ),
    ]
    cn_blocks = [
        (
            "我想把一件事说准确。首达时间分布 f(t) 是随机游走者在第 t 步首次到达目标的概率。f(t) 里的双峰可以成为隐藏路径族的证据，但它本身不是证据。接下来要讲的，就是一个形状要满足哪些条件，我才相信它。",
            "先讲正面机制，再讲对照检验。",
            "定义 f(t)，点明「证据而非装饰」。",
        ),
        (
            "我用三项检查。第一，提出机制。第二，把曲线分解，让每一部分概率都有来源。第三，排除伪迹。三项缺一项，第二峰就只是一个视觉线索。",
            "这三项检查是后面每一页的评判标准。",
            "说明机制、分解、排除伪迹。",
        ),
        (
            "环上的机制最清楚。捷径产生一支快分支，而沿环绕行的普通路径仍然带着晚到的概率。关键不在于有没有捷径，而在于两类路径族在时间上是否分得开、各自的权重是否大到看得见。捷径几乎不用，就没有早峰；用得太多，晚峰就退化成肩。",
            "这是进入警示部分之前的正面例子。",
            "用环作为最简单的正面情形。",
        ),
        (
            "在讲单目标、双目标或时间预算之前，先看最基本的过程：一个游走者在二维格点上，每次跳到一个最近邻格点，第一次到达目标就停下。f(t) 是这次首次到达发生在第 t 步的概率。重复走很多次可以估计它；报告里的曲线则是直接由转移概率算出来的。",
            "先让动画跑几秒，再切换一次目标数量或漂移方向。",
            "展示格点游走，以及 f(t) 数的是什么。",
        ),
        (
            "局部过程讲清楚以后，双峰的含义就更丰富了。第二个特征可能来自某条路径，也可能来自某个目标，或者来自某个「路径—目标」组合。所以二维工作始终同时看几何和目标数量，而不是只从一条曲线下结论。",
            "从实时过程过渡到空间机制。",
            "讲清路径竞争与目标竞争。",
        ),
        (
            "单目标格点让机制检验更明确。渗透率为 0.004 时，在第二峰时间窗内击中的路径，平均在中央通道外停留约 1,290 步，谷时间窗内约 705 步；而先穿过半透膜的概率是 20% 对 18%。晚到的路径不只是穿过了一道边界，而是在格点的另一部分停留得更久。",
            "这一页靠两组数字：通道外约 705 对 1,290 步，穿膜概率 18% 对 20%。",
            "比较通道外停留时间与穿膜概率。",
        ),
        (
            "精确相遇模型之所以重要，是因为它给出的答案是否定的。两个懒惰游走者在有限长、反射边界、无捷径的一维格点上同步行走，只有走到同一格点才算相遇，N 取 15、21 或 31。所有扫描情形里，F2（把奇、偶步两两合并后的分布）都没有稳健的双峰。那些反常的形状是奇偶伪迹、同一目标的长尾，或目标移位形成的弱肩。这个结论只适用于这个模型；其他相遇模型，比如带漂移和捷径的环、带捷径的二维格点，确实给出双峰：环上清晰，二维较弱。",
            "讲负结果时同时讲清范围：无捷径、一维反射边界、同步更新、同格相遇、N = 15、21、31。",
            "讲负结果及其适用范围。",
        ),
        (
            "这个面板是示意性的总结，不是计算数据。环的情形是成立的机制；二维情形要先做分解，第二峰才算数；相遇情形是护栏：把奇偶步两两合并（F2）以后，剩下的是一个峰加长尾或弱肩，没有稳健的第二峰。",
            "边讲边把三种情形各切换一次。",
            "演示情形切换。",
        ),
        (
            "所以这项工作的产出变了。它不只是一份双峰清单，而是一套规则：什么时候双峰值得作为机制来陈述，什么时候还需要进一步分解，什么时候应当否定。",
            "收尾：产出是一条判断标准，说明一个峰什么时候够格作为机制。",
            "以证据规则收尾。",
        ),
    ]

    def blocks(lang: str, rows: list[tuple[str, str, str]]) -> list[dict]:
        out = []
        for item, (spoken, notes, prompt) in zip(slides, rows):
            out.append(
                {
                    "slide_id": item["id"],
                    "start": item["start"],
                    "end": item["end"],
                    "title": item["title_cn"] if lang == "cn" else item["title_en"],
                    "spoken_text": spoken,
                    "speaker_notes": notes,
                    "timing_prompt": prompt,
                }
            )
        return out

    script_en = {"talk_id": "multitimescale-encounter", "lang": "en", "blocks": blocks("en", en_blocks)}
    script_cn = {"talk_id": "multitimescale-encounter", "lang": "cn", "blocks": blocks("cn", cn_blocks)}

    basic_demo = {
        "grid_width": 7,
        "grid_height": 5,
        "source": {"x": 0, "y": 2},
        "target": {"x": 6, "y": 2},
        "walks": [
            {
                "id": "fast",
                "hit_step": 6,
                "steps": [{"x": x, "y": 2} for x in range(7)],
            },
            {
                "id": "delayed",
                "hit_step": 10,
                "steps": [
                    {"x": 0, "y": 2},
                    {"x": 1, "y": 2},
                    {"x": 1, "y": 1},
                    {"x": 2, "y": 1},
                    {"x": 3, "y": 1},
                    {"x": 3, "y": 2},
                    {"x": 3, "y": 3},
                    {"x": 4, "y": 3},
                    {"x": 5, "y": 3},
                    {"x": 5, "y": 2},
                    {"x": 6, "y": 2},
                ],
            },
        ],
    }

    write_json(DATA_DIR / "manifest.json", manifest)
    write_json(DATA_DIR / "script.en.json", script_en)
    write_json(DATA_DIR / "script.cn.json", script_cn)
    write_json(DATA_DIR / "basic_demo.json", basic_demo)


def main() -> None:
    build_svgs()
    build_talk_data()
    print(f"Wrote talk data to {DATA_DIR}")
    print(f"Wrote talk assets to {ASSET_DIR}")


if __name__ == "__main__":
    main()
