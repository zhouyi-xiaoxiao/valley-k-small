#!/usr/bin/env python3

from __future__ import annotations

import base64
import csv
import html
import math
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRIMARY_REPO = Path("/Users/ae23069/Library/CloudStorage/OneDrive-UniversityofBristol/Desktop/valley-k-small")
ASSET_DIR = ROOT / "platform" / "web" / "public" / "talk-assets" / "smet-phd"
TMP_DIR = ROOT / "platform" / "web" / ".tmp" / "smet-talk"

W = 1600
H = 900

BG = "#f7f3ea"
CARD = "#fffdf8"
LINE = "#dccfb7"
INK = "#18212a"
SOFT = "#52606d"
TEAL = "#1f7a73"
TEAL_SOFT = "#68a89b"
AMBER = "#d8891f"
AMBER_SOFT = "#e6b266"
BLUE = "#3269d1"
RED = "#d2443d"
GREEN = "#52a57f"
GRID = "#d7d1c2"


def ensure_dirs() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)


def source_path(*parts: str) -> Path:
    candidate = ROOT.joinpath(*parts)
    if candidate.exists():
        return candidate
    fallback = PRIMARY_REPO.joinpath(*parts)
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"Could not locate source asset: {'/'.join(parts)}")


def read_csv_rows(*parts: str) -> list[dict[str, str]]:
    with source_path(*parts).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def asset_data_uri(filename: str) -> str:
    payload = (ASSET_DIR / filename).read_bytes()
    return f"data:image/png;base64,{base64.b64encode(payload).decode('ascii')}"


def convert_pdf_to_png(source: Path, dest: Path, dpi: int = 180) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "gs",
            "-dSAFER",
            "-dBATCH",
            "-dNOPAUSE",
            "-sDEVICE=pngalpha",
            f"-r{dpi}",
            "-o",
            str(dest),
            str(source),
        ],
        check=True,
        cwd=ROOT,
    )


def copy_png(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)


def card(x: int, y: int, w: int, h: int, radius: int = 28, fill: str = CARD) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
        f'fill="{fill}" stroke="{LINE}" stroke-width="2"/>'
    )


def text(x: int, y: int, value: str, size: int, weight: int = 500, fill: str = INK) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(value)}</text>'
    )


def multiline(
    x: int,
    y: int,
    lines: list[str],
    size: int,
    line_gap: int = 1.34,
    weight: int = 400,
    fill: str = SOFT,
) -> str:
    out = [
        f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}">'
    ]
    for idx, line in enumerate(lines):
        dy = 0 if idx == 0 else int(size * line_gap)
        out.append(f'<tspan x="{x}" dy="{dy}">{html.escape(line)}</tspan>')
    out.append("</text>")
    return "".join(out)


def svg_doc(body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" fill="none">'
        f"<rect width=\"{W}\" height=\"{H}\" fill=\"{BG}\"/>"
        f"{body}</svg>"
    )


def grouped_bar_chart(
    x: int,
    y: int,
    w: int,
    h: int,
    windows: list[str],
    series: list[tuple[str, str, list[float]]],
    ymax: float,
    y_label: str,
) -> str:
    left = x + 34
    bottom = y + h - 34
    top = y + 38
    plot_h = bottom - top
    group_w = (w - 52) / len(windows)
    bar_w = min(44, (group_w - 28) / len(series))
    parts = [
        f'<line x1="{left}" y1="{bottom}" x2="{x + w - 16}" y2="{bottom}" stroke="#b9c0bf" stroke-width="2"/>',
        text(x + 8, y + 18, y_label, 16, 500, SOFT),
    ]
    for idx, tick in enumerate([0.0, ymax / 2, ymax]):
        y_tick = bottom - (tick / ymax) * plot_h
        parts.append(
            f'<line x1="{left}" y1="{y_tick:.1f}" x2="{x + w - 18}" y2="{y_tick:.1f}" stroke="#e5dece" stroke-width="1"/>'
        )
        parts.append(text(x + 8, int(y_tick) + 6, f"{tick:.1f}", 15, 400, SOFT))
    legend_x = x + w - 250
    for idx, (label, color, _values) in enumerate(series):
        ly = y + 8 + idx * 22
        parts.append(f'<rect x="{legend_x}" y="{ly}" width="16" height="16" rx="4" fill="{color}"/>')
        parts.append(text(legend_x + 24, ly + 14, label, 15, 500, SOFT))
    for idx, window in enumerate(windows):
        gx = left + idx * group_w + 20
        parts.append(text(int(gx + group_w / 2) - 24, bottom + 26, window, 16, 500, SOFT))
        for j, (_label, color, values) in enumerate(series):
            value = values[idx]
            bh = 0 if ymax <= 0 else (value / ymax) * plot_h
            bx = gx + j * (bar_w + 8)
            by = bottom - bh
            parts.append(
                f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{max(6, bh):.1f}" rx="8" fill="{color}" opacity="0.9"/>'
            )
    return "".join(parts)


def stacked_window_chart(
    x: int,
    y: int,
    w: int,
    h: int,
    windows: list[str],
    near_values: list[float],
    far_values: list[float],
) -> str:
    left = x + 34
    bottom = y + h - 30
    top = y + 18
    plot_h = bottom - top
    group_w = (w - 60) / len(windows)
    parts = [
        f'<line x1="{left}" y1="{bottom}" x2="{x + w - 16}" y2="{bottom}" stroke="#b9c0bf" stroke-width="2"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{left}" y2="{top}" stroke="#b9c0bf" stroke-width="2"/>',
        f'<rect x="{x + w - 160}" y="{y + 6}" width="16" height="16" rx="4" fill="{BLUE}"/>',
        text(x + w - 138, y + 20, "near target", 15, 500, SOFT),
        f'<rect x="{x + w - 160}" y="{y + 30}" width="16" height="16" rx="4" fill="{AMBER}"/>',
        text(x + w - 138, y + 44, "far target", 15, 500, SOFT),
    ]
    for idx, window in enumerate(windows):
        bx = left + idx * group_w + 26
        bar_w = min(86, group_w - 34)
        near_h = near_values[idx] * plot_h
        far_h = far_values[idx] * plot_h
        far_y = bottom - far_h
        near_y = far_y - near_h
        parts.append(f'<rect x="{bx:.1f}" y="{near_y:.1f}" width="{bar_w:.1f}" height="{near_h:.1f}" fill="{BLUE}" opacity="0.84"/>')
        parts.append(f'<rect x="{bx:.1f}" y="{far_y:.1f}" width="{bar_w:.1f}" height="{far_h:.1f}" fill="{AMBER}" opacity="0.9"/>')
        parts.append(text(int(bx + bar_w / 2) - 22, bottom + 26, window, 15, 500, SOFT))
    return "".join(parts)


def ring_point(cx: float, cy: float, r: float, degrees: float) -> tuple[float, float]:
    theta = math.radians(degrees)
    return cx + r * math.cos(theta), cy + r * math.sin(theta)


def draw_ring_schematic(cx: int, cy: int, r: int, detailed: bool = False) -> str:
    start = ring_point(cx, cy, r, 206)
    u = ring_point(cx, cy, r, 230)
    v = ring_point(cx, cy, r, 16)
    target = ring_point(cx, cy, r, -4)
    tick_marks = []
    for degrees in range(0, 360, 24):
        p1 = ring_point(cx, cy, r - 6, degrees)
        p2 = ring_point(cx, cy, r + 6, degrees)
        tick_marks.append(
            f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
            f'stroke="#cfd5d0" stroke-width="2.5" stroke-linecap="round"/>'
        )

    fast_segments = [
        f'<path d="M {start[0]:.1f} {start[1]:.1f} A {r} {r} 0 0 1 {u[0]:.1f} {u[1]:.1f}" '
        f'stroke="{TEAL}" stroke-width="10" fill="none" stroke-linecap="round"/>',
        f'<path d="M {u[0]:.1f} {u[1]:.1f} L {v[0]:.1f} {v[1]:.1f}" '
        f'stroke="{TEAL}" stroke-width="10" fill="none" stroke-linecap="round"/>',
        f'<path d="M {v[0]:.1f} {v[1]:.1f} A {r} {r} 0 0 1 {target[0]:.1f} {target[1]:.1f}" '
        f'stroke="{TEAL}" stroke-width="10" fill="none" stroke-linecap="round"/>',
    ]
    slow_arc = (
        f'<path d="M {start[0]:.1f} {start[1]:.1f} A {r} {r} 0 1 0 {target[0]:.1f} {target[1]:.1f}" '
        f'stroke="{AMBER_SOFT}" stroke-width="8" fill="none" stroke-linecap="round" '
        'stroke-dasharray="16 12"/>'
    )
    labels = [
        f'<circle cx="{start[0]:.1f}" cy="{start[1]:.1f}" r="14" fill="#101827"/>',
        f'<circle cx="{u[0]:.1f}" cy="{u[1]:.1f}" r="11" fill="{AMBER}"/>',
        f'<circle cx="{v[0]:.1f}" cy="{v[1]:.1f}" r="11" fill="{AMBER}"/>',
        f'<circle cx="{target[0]:.1f}" cy="{target[1]:.1f}" r="15" fill="{BLUE}"/>',
        text(int(start[0]) - 34, int(start[1]) + 46, "start", 24, 600, INK),
        text(int(u[0]) - 22, int(u[1]) - 20, "u", 22, 700, AMBER),
        text(int(v[0]) - 16, int(v[1]) - 24, "v", 22, 700, AMBER),
        text(int(target[0]) - 30, int(target[1]) - 28, "target", 24, 600, BLUE),
    ]
    return "".join(
        [
            f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="#c7ccc9" stroke-width="10" fill="none"/>',
            *tick_marks,
            slow_arc if detailed else "",
            *fast_segments,
            *labels,
        ]
    )


def smooth_curve_path(single: bool = False) -> str:
    if single:
        return (
            "M 130 560 C 250 350 420 240 600 250 "
            "C 770 260 950 330 1120 420 C 1240 485 1320 515 1415 528"
        )
    return (
        "M 130 560 C 220 455 290 320 370 300 "
        "C 470 276 545 390 635 435 "
        "C 760 500 930 275 1090 300 "
        "C 1230 318 1320 450 1415 500"
    )


def build_slide1() -> str:
    ring = draw_ring_schematic(430, 604, 198, detailed=True)
    body = [
        text(92, 104, "10-minute research talk", 24, 500, SOFT),
        multiline(
            92,
            166,
            ["Hidden routes in first-passage time"],
            62,
            1.1,
            700,
            INK,
        ),
        multiline(
            94,
            240,
            [
                "A one-target 1D ring can still split into a fast route, a valley,",
                "and a delayed route once one directed shortcut is present.",
            ],
            24,
            1.3,
            400,
            SOFT,
        ),
        '<rect x="68" y="308" width="646" height="534" rx="38" fill="#f8f4ea"/>',
        '<rect x="742" y="308" width="792" height="534" rx="38" fill="#f8f4ea"/>',
        text(112, 360, "Realistic 1D ring geometry", 26, 700, INK),
        text(112, 394, "Periodic ring, absorbing target, and one straight shortcut from u to v.", 18, 400, SOFT),
        ring,
        text(786, 360, "Distribution-level picture", 26, 700, INK),
        multiline(
            786,
            394,
            [
                "The same target can still generate an early peak, a valley,",
                "and a delayed branch once both route families stay visible.",
            ],
            20,
            1.3,
            400,
            SOFT,
        ),
        '<path d="M 798 740 L 1476 740" stroke="#b9c0bf" stroke-width="3"/>',
        '<path d="M 798 740 L 798 478" stroke="#b9c0bf" stroke-width="3"/>',
        f'<path d="{smooth_curve_path(False)}" transform="translate(720,-70)" stroke="{INK}" stroke-width="9" fill="none" stroke-linecap="round"/>',
        f'<circle cx="1085" cy="490" r="8" fill="{TEAL}"/>',
        f'<circle cx="1355" cy="575" r="8" fill="{AMBER}"/>',
        f'<circle cx="1490" cy="475" r="8" fill="{AMBER}"/>',
        text(1046, 474, "peak1", 20, 600, TEAL),
        text(1320, 615, "valley", 20, 600, SOFT),
        text(1452, 458, "peak2", 20, 600, AMBER),
        text(794, 464, "density", 18, 500, SOFT),
        text(1448, 778, "time", 18, 500, SOFT),
    ]
    return svg_doc("".join(body))


def build_slide3() -> str:
    body = [
        text(96, 110, "Shape already hints at mechanism", 28, 500, SOFT),
        multiline(96, 184, ["Why a double peak matters"], 62, 1.1, 700, INK),
        multiline(
            98,
            258,
            [
                "A single peak usually means one dominant arrival scale.",
                "A double peak means two route families stay visible in the statistics.",
            ],
            26,
            1.32,
            400,
            SOFT,
        ),
        '<rect x="88" y="330" width="670" height="486" rx="34" fill="#f8f4ea"/>',
        '<rect x="844" y="330" width="670" height="486" rx="34" fill="#f8f4ea"/>',
        text(132, 388, "single peak", 32, 700, INK),
        text(132, 426, "one dominant timescale", 22, 400, SOFT),
        '<path d="M 160 706 L 666 706" stroke="#b9c0bf" stroke-width="3"/>',
        '<path d="M 160 706 L 160 448" stroke="#b9c0bf" stroke-width="3"/>',
        f'<path d="M 184 678 C 256 550 362 492 470 520 C 552 542 616 612 654 650" stroke="{TEAL}" '
        'stroke-width="8" fill="none" stroke-linecap="round"/>',
        f'<circle cx="416" cy="553" r="8" fill="{TEAL}"/>',
        text(380, 538, "one peak", 22, 600, TEAL),
        text(888, 388, "double peak", 32, 700, INK),
        text(888, 426, "two route families stay visible", 22, 400, SOFT),
        '<path d="M 918 706 L 1424 706" stroke="#b9c0bf" stroke-width="3"/>',
        '<path d="M 918 706 L 918 448" stroke="#b9c0bf" stroke-width="3"/>',
        f'<path d="M 944 676 C 1002 564 1058 522 1116 564 C 1162 598 1204 666 1264 648 C 1310 634 1358 532 1412 548" stroke="{INK}" '
        'stroke-width="8" fill="none" stroke-linecap="round"/>',
        f'<circle cx="1030" cy="562" r="8" fill="{TEAL}"/>',
        f'<circle cx="1200" cy="648" r="8" fill="{AMBER}"/>',
        f'<circle cx="1360" cy="548" r="8" fill="{AMBER}"/>',
        text(996, 548, "peak1", 20, 600, TEAL),
        text(1168, 686, "valley", 20, 600, SOFT),
        text(1328, 534, "peak2", 20, 600, AMBER),
    ]
    return svg_doc("".join(body))


def build_slide4() -> str:
    ring_compare = asset_data_uri("lazy_geom_compare.png")
    body = [
        text(94, 110, "A realistic single-target ring", 28, 500, SOFT),
        multiline(94, 174, ["One ring, one shortcut,", "one broad case and one split case"], 48, 1.08, 700, INK),
        text(96, 282, "The geometry stays fixed; the real ring figure shows one broad regime and one clearly split regime.", 21, 400, SOFT),
        card(84, 332, 470, 494),
        card(580, 332, 936, 494),
        text(118, 384, "geometry", 28, 700, INK),
        text(118, 420, "Absorbing target and one straight shortcut from u to v.", 20, 400, SOFT),
        draw_ring_schematic(320, 612, 146, detailed=True),
        text(632, 384, "real ring comparison", 28, 700, INK),
        f'<image href="{ring_compare}" x="604" y="404" width="896" height="412" preserveAspectRatio="xMidYMid meet"/>',
        card(612, 778, 884, 88, 18, "#f5efe4"),
        multiline(640, 816, ["One regime stays broad; another keeps both an early branch", "and a delayed branch visible."], 18, 1.18, 500, SOFT),
    ]
    return svg_doc("".join(body))


def build_slide5() -> str:
    peak2_scan = asset_data_uri("peak2_vs_dst.png")
    peak_times = asset_data_uri("peak_times_vs_dst.png")
    body = [
        text(96, 110, "Recent single-target result", 28, 500, SOFT),
        multiline(96, 172, ["Retuning the shortcut destination", "moves the late branch"], 46, 1.08, 700, INK),
        text(98, 286, "Real scans show that both late-branch weight and timing change with shortcut destination.", 21, 400, SOFT),
        card(84, 314, 744, 500),
        card(848, 314, 668, 500),
        text(124, 364, "late-branch weight", 28, 700, INK),
        text(888, 364, "peak timings", 28, 700, INK),
        f'<image href="{peak2_scan}" x="114" y="394" width="690" height="364" preserveAspectRatio="xMidYMid meet"/>',
        f'<image href="{peak_times}" x="874" y="398" width="616" height="350" preserveAspectRatio="xMidYMid meet"/>',
        card(114, 776, 690, 80, 18, "#f5efe4"),
        card(874, 764, 616, 92, 18, "#f5efe4"),
        multiline(142, 812, ["Some destinations strengthen the late branch;", "others almost erase it."], 20, 1.2, 500, SOFT),
        multiline(904, 804, ["The late branch also moves in time,", "so the destination scan is not monotone."], 20, 1.2, 500, SOFT),
    ]
    return svg_doc("".join(body))


def build_slide6() -> str:
    partition = asset_data_uri("fig1_partition.png")
    left_panel = "".join(
        [
            card(100, 392, 668, 352, 22, "#f8f4ea"),
            f'<image href="{partition}" x="118" y="410" width="632" height="316" preserveAspectRatio="xMidYMid meet"/>',
        ]
    )
    right_panel = "".join(
        [
            card(832, 392, 684, 352, 24, "#f8f4ea"),
            *[
                f'<line x1="{850 + i*24}" y1="422" x2="{850 + i*24}" y2="714" stroke="{GRID}" stroke-width="1"/>'
                for i in range(0, 28)
            ],
            *[
                f'<line x1="850" y1="{422 + j*24}" x2="1498" y2="{422 + j*24}" stroke="{GRID}" stroke-width="1"/>'
                for j in range(0, 13)
            ],
            '<rect x="850" y="438" width="88" height="244" fill="#ef6d24" opacity="0.96"/>',
            '<rect x="938" y="438" width="560" height="244" fill="#43bea0" opacity="0.96"/>',
            '<rect x="938" y="514" width="504" height="92" fill="#a7a4a4" opacity="0.98"/>',
            '<line x1="938" y1="514" x2="1442" y2="514" stroke="#5d6866" stroke-width="5" stroke-dasharray="18 12"/>',
            '<line x1="938" y1="606" x2="1442" y2="606" stroke="#5d6866" stroke-width="5" stroke-dasharray="18 12"/>',
            text(872, 466, "Left side", 18, 700, CARD),
            text(1124, 466, "Outer / right side", 18, 700, CARD),
            text(1118, 568, "Corridor", 24, 700, INK),
            f'<rect x="962" y="552" width="18" height="18" fill="{RED}"/>',
            text(946, 598, "start", 20, 600, RED),
            f'<polygon points="1102,542 1120,560 1102,578 1084,560" fill="{BLUE}"/>',
            text(1056, 506, "near target", 18, 600, BLUE),
            f'<circle cx="1438" cy="484" r="14" fill="{AMBER}"/>',
            text(1388, 446, "far target", 18, 600, AMBER),
            f'<path d="M 980 560 C 1026 560 1054 560 1084 560" stroke="{BLUE}" stroke-width="5" fill="none" stroke-linecap="round"/>',
            f'<path d="M 980 560 C 1090 482 1260 456 1422 484" stroke="{AMBER}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="18 10"/>',
        ]
    )
    body = [
        text(96, 110, "From one target to two targets in 2D", 28, 500, SOFT),
        multiline(96, 172, ["What 2D layouts can", "keep two timescales visible?"], 46, 1.08, 700, INK),
        text(98, 284, "One target shows the partition clearly. Two targets reuse the same geometry grammar, but add target competition.", 20, 400, SOFT),
        card(84, 332, 706, 462),
        card(810, 332, 706, 462),
        text(126, 380, "one-target partition", 28, 700, INK),
        left_panel,
        text(852, 380, "two-target geometry", 28, 700, INK),
        right_panel,
        card(120, 810, 1368, 54, 18, "#f5efe4"),
        text(146, 844, "The same spatial grammar can keep two route families visible; two targets add the question of which target wins first.", 18, 500, SOFT),
    ]
    return svg_doc("".join(body))


def build_slide7() -> str:
    summary_rows = read_csv_rows(
        "research",
        "reports",
        "grid2d_one_target_valley_peak_budget",
        "artifacts",
        "data",
        "window_budget_summary.csv",
    )
    windows = ["peak1", "valley", "peak2"]
    kappas = [("κ=0", "#444444", "0.0"), ("κ=0.004", AMBER, "0.004"), ("κ=0.0152", BLUE, "0.0152")]
    outside_series = []
    membrane_series = []
    for label, color, kappa in kappas:
        matching = {row["window"]: row for row in summary_rows if row["kappa"] == kappa}
        outside_series.append((label, color, [float(matching[w]["outside_share"]) for w in windows]))
        membrane_series.append((label, color, [float(matching[w]["tau_mem_prob"]) if matching[w]["tau_mem_prob"] != "nan" else 0.0 for w in windows]))

    membrane_geom = asset_data_uri("membrane_rep_sym_geometry.png")
    body = [
        text(96, 110, "One-target corridor mechanism", 28, 500, SOFT),
        multiline(96, 172, ["Is peak2 mainly outside time,", "or mainly the membrane crossing?"], 44, 1.08, 700, INK),
        text(98, 286, "The geometry is upper/lower symmetric, so the mechanism test is between outside-budget evidence and membrane-linked evidence.", 20, 400, SOFT),
        '<defs><clipPath id="slide7-geom-clip"><rect x="104" y="380" width="1366" height="120" rx="16"/></clipPath></defs>',
        card(84, 322, 1406, 208),
        card(84, 548, 682, 282),
        card(808, 548, 682, 282),
        text(118, 378, "symmetric corridor geometry", 28, 700, INK),
        f'<image href="{membrane_geom}" x="104" y="342" width="1366" height="214" preserveAspectRatio="xMidYMid slice" clip-path="url(#slide7-geom-clip)"/>',
        text(118, 604, "outside-budget evidence", 24, 700, INK),
        text(842, 604, "membrane-linked evidence", 24, 700, INK),
        grouped_bar_chart(112, 620, 630, 180, windows, outside_series, 0.65, "share"),
        grouped_bar_chart(836, 620, 630, 180, windows, membrane_series, 0.6, "prob."),
        card(108, 794, 1380, 70, 18, "#f5efe4"),
        text(132, 836, "Peak2 separates from the valley more clearly through outside-time budget than through membrane probability alone.", 19, 600, SOFT),
    ]
    return svg_doc("".join(body))


def build_slide8() -> str:
    split = asset_data_uri("two_target_rep_window_split.png")
    two_target_companion = "".join(
        [
            *[
                f'<line x1="{112 + i*22}" y1="416" x2="{112 + i*22}" y2="594" stroke="{GRID}" stroke-width="1"/>'
                for i in range(0, 29)
            ],
            *[
                f'<line x1="112" y1="{416 + j*22}" x2="744" y2="{416 + j*22}" stroke="{GRID}" stroke-width="1"/>'
                for j in range(0, 9)
            ],
            '<rect x="112" y="430" width="88" height="152" fill="#ef6d24" opacity="0.96"/>',
            '<rect x="200" y="430" width="544" height="152" fill="#43bea0" opacity="0.96"/>',
            '<rect x="200" y="476" width="486" height="60" fill="#a7a4a4" opacity="0.98"/>',
            '<line x1="200" y1="476" x2="686" y2="476" stroke="#5d6866" stroke-width="4" stroke-dasharray="16 10"/>',
            '<line x1="200" y1="536" x2="686" y2="536" stroke="#5d6866" stroke-width="4" stroke-dasharray="16 10"/>',
            text(132, 456, "left side", 16, 700, CARD),
            text(398, 456, "outer / right side", 16, 700, CARD),
            text(402, 516, "corridor", 22, 700, INK),
            f'<rect x="220" y="500" width="16" height="16" fill="{RED}"/>',
            text(204, 548, "start", 18, 600, RED),
            f'<polygon points="340,490 356,506 340,522 324,506" fill="{BLUE}"/>',
            text(294, 466, "near target", 16, 600, BLUE),
            f'<circle cx="680" cy="458" r="13" fill="{AMBER}"/>',
            text(630, 430, "far target", 16, 600, AMBER),
            f'<path d="M 238 508 C 274 508 294 508 324 506" stroke="{BLUE}" stroke-width="5" fill="none" stroke-linecap="round"/>',
            f'<path d="M 238 508 C 330 452 490 432 664 458" stroke="{AMBER}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="16 10"/>',
        ]
    )
    many_targets = "".join(
        [
            *[
                f'<circle cx="{948 + (i%4)*108}" cy="{456 + (i//4)*84}" r="12" fill="{AMBER if i % 3 == 0 else BLUE}" opacity="{0.92 - (i % 4)*0.08}"/>'
                for i in range(8)
            ],
            f'<rect x="892" y="584" width="18" height="18" fill="{RED}"/>',
            text(876, 624, "start", 22, 600, RED),
            f'<path d="M 910 592 C 984 572 1016 536 1048 492" stroke="{TEAL}" stroke-width="5" fill="none" stroke-linecap="round"/>',
            f'<path d="M 910 592 C 1046 626 1166 620 1278 574" stroke="{AMBER}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="16 12"/>',
        ]
    )
    body = [
        text(96, 110, "Open questions beyond one target", 28, 500, SOFT),
        multiline(96, 170, ["Next step:", "from two targets to many"], 42, 1.08, 700, INK),
        text(98, 276, "Beyond one target, the distribution can encode both route competition and target competition.", 19, 400, SOFT),
        card(84, 332, 688, 492),
        card(828, 332, 688, 492),
        text(122, 382, "two-target mechanism", 28, 700, INK),
        text(866, 382, "many-target outlook", 28, 700, INK),
        two_target_companion,
        f'<image href="{split}" x="142" y="570" width="572" height="258" preserveAspectRatio="xMidYMid meet"/>',
        many_targets,
        card(874, 648, 598, 150, 18, "#f5efe4"),
        text(906, 696, "Two targets: which route wins, and which target wins first?", 18, 500, SOFT),
        text(906, 728, "Many targets: screening, crowding, and rare late winners.", 18, 500, SOFT),
        text(906, 760, "Can one late peak correspond to a distant target class?", 18, 500, SOFT),
    ]
    return svg_doc("".join(body))


def copy_and_convert_sources() -> None:
    sources = [
        (
            source_path("research", "reports", "ring_lazy_flux", "artifacts", "figures", "lazy_ring_flux_bimodality", "lazy_K2_paper_geometry_selfloop_vs_equal4_N100.pdf"),
            ASSET_DIR / "lazy_geom_compare.png",
            "pdf",
        ),
        (
            source_path("research", "reports", "ring_valley_dst", "artifacts", "figures", "second_peak_dst_shortcut_usage", "latest", "peak2_vs_dst.pdf"),
            ASSET_DIR / "peak2_vs_dst.png",
            "pdf",
        ),
        (
            source_path("research", "reports", "ring_valley_dst", "artifacts", "figures", "second_peak_dst_shortcut_usage", "latest", "peak_times_vs_dst.pdf"),
            ASSET_DIR / "peak_times_vs_dst.png",
            "pdf",
        ),
        (
            source_path("research", "reports", "grid2d_one_target_valley_peak_budget", "artifacts", "figures", "fig1_partition_schematic.pdf"),
            ASSET_DIR / "fig1_partition.png",
            "pdf",
        ),
        (
            source_path("research", "reports", "grid2d_membrane_near_target", "artifacts", "figures", "membrane_rep_sym_geometry.png"),
            ASSET_DIR / "membrane_rep_sym_geometry.png",
            "png",
        ),
        (
            source_path("research", "reports", "grid2d_membrane_near_target", "artifacts", "figures", "two_target_rep_geometry.png"),
            ASSET_DIR / "two_target_rep_geometry.png",
            "png",
        ),
        (
            source_path("research", "reports", "grid2d_membrane_near_target", "artifacts", "figures", "two_target_clear_geometry.png"),
            ASSET_DIR / "two_target_clear_geometry.png",
            "png",
        ),
        (
            source_path("research", "reports", "grid2d_membrane_near_target", "artifacts", "figures", "two_target_rep_window_split.png"),
            ASSET_DIR / "two_target_rep_window_split.png",
            "png",
        ),
        (
            source_path("research", "reports", "grid2d_one_target_valley_peak_budget", "artifacts", "figures", "fig2_tau_out_budget.pdf"),
            ASSET_DIR / "fig2_tau_out_budget.png",
            "pdf",
        ),
        (
            source_path("research", "reports", "grid2d_one_target_valley_peak_budget", "artifacts", "figures", "fig3_tau_mem_budget.pdf"),
            ASSET_DIR / "fig3_tau_mem_budget.png",
            "pdf",
        ),
    ]
    for source, dest, kind in sources:
        if kind == "pdf":
            convert_pdf_to_png(source, dest)
        else:
            copy_png(source, dest)


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    copy_and_convert_sources()
    write_file(ASSET_DIR / "slide1-hero.svg", build_slide1())
    write_file(ASSET_DIR / "slide3-single-vs-double.svg", build_slide3())
    write_file(ASSET_DIR / "slide4-ring-cases.svg", build_slide4())
    write_file(ASSET_DIR / "slide5-route-config.svg", build_slide5())
    write_file(ASSET_DIR / "slide6-2d-targets.svg", build_slide6())
    write_file(ASSET_DIR / "slide7-membrane-plateau.svg", build_slide7())
    write_file(ASSET_DIR / "slide8-target-mechanisms.svg", build_slide8())


if __name__ == "__main__":
    main()
