"""Reader-facing text for the report pages and the reports index.

Hand-written against each report's manuscript, data and code (numbers are
taken from the CSV/JSON files under research/reports/<id>/). build_web_data.py
uses these strings verbatim. Rules:

- state the model, its parameters and the conditions under which a result holds;
- "two peaks" always refers to the report's own peak rule, which the method
  text spells out;
- no person's name for a method, no internal labels (equal4, selfloop, AW
  without expansion), no self-assessment ("publication-ready", "robust");
- English and Chinese say the same thing; key_findings have the same count.

Entries with only title/summary keep the narrative and findings extracted from
the manuscript.
"""

from __future__ import annotations

from typing import Any

REPORT_TEXT_OVERRIDES: dict[str, dict[str, dict[str, Any]]] = {
    "ring_lazy_jump": {
        "en": {
            "teaser": 'Lazy ring with one directed shortcut: at N = 100, two arrival peaks for 0.0005 ≤ β ≤ 0.05 (K = 2) and 0.001 ≤ β ≤ 0.15 (K = 4); Monte Carlo route classes show which paths make each peak.',
            "title": "Lazy Ring Jump-Over Mechanism (K = 2 vs K = 4)",
            "summary": (
                "A lazy walk on a ring of N sites (it stays put with probability 1/3, otherwise steps to one of its K "
                "nearest neighbours) with one directed shortcut that takes a fraction β of the stay-put probability at "
                "its source. At N = 100, by the report's peak rule, f(t) has two peaks for 0.0005 ≤ β ≤ 0.05 with K = 2 "
                "and for 0.001 ≤ β ≤ 0.15 with K = 4; Monte Carlo route classes show which paths make each peak."
            ),
            "narrative": {
                "model_overview": (
                    "Periodic ring of N sites. Each step stays put with probability 1 − q (q = 2/3) or moves to one of "
                    "the K nearest neighbours (±1 to ±K/2) with probability q/K; K = 2 or 4. Start at site 1, target at "
                    "site 1 + N/2, absorbed on first arrival. One directed shortcut from site 6 to the site just past the "
                    "target, with probability β(1 − q) taken from the stay-put probability of site 6."
                ),
                "method_overview": (
                    "Exact f(t) by numerical inversion of the generating function (Abate–Whitt, with a rank-one "
                    "Sherman–Morrison update for the shortcut) and by stepping the master equation forward. A peak is a "
                    "strict local maximum with f ≥ 10⁻⁷ and at least 1% of the highest peak. Monte Carlo with 200 000 "
                    "walkers sorts arrivals by whether they used the shortcut and whether they jumped over the target; "
                    "a control run makes a jump-over absorbing."
                ),
                "result_overview": (
                    "Two peaks need a shortcut of intermediate strength: at N = 100 they appear for 0.0005 ≤ β ≤ 0.05 "
                    "(K = 2) and 0.001 ≤ β ≤ 0.15 (K = 4). At β = 0.02 every first-peak arrival used the shortcut; with "
                    "K = 4, walkers that jumped over the target without using the shortcut make up 23% of the "
                    "second-peak window."
                ),
            },
            "key_findings": [
                "First peak = shortcut route: at N = 100 and β = 0.02, every walker arriving in the first peak used the shortcut, for both K = 2 and K = 4.",
                "Second peak = mostly the slow way round: 26% (K = 2) and 13% (K = 4) of second-peak arrivals used the shortcut (N = 100, β = 0.02).",
                "A jump-over (a ±2 step across the target without landing on it) exists only for K = 4; walkers that jumped over without using the shortcut make up 23% of the K = 4 second-peak window.",
                "Two peaks exist only at intermediate shortcut strength: at N = 100 there are none at β = 0, nor from β = 0.07 (K = 2) or β = 0.2 (K = 4) upwards.",
            ],
        },
        "cn": {
            "teaser": '带一条有向捷径的懒惰环：N = 100 时，K = 2 在 0.0005 ≤ β ≤ 0.05、K = 4 在 0.001 ≤ β ≤ 0.15 范围内出现两个到达峰；蒙特卡洛路径分类说明每个峰由哪些路径构成。',
            "title": "懒惰环上的越过目标机制（K = 2 与 K = 4）",
            "summary": (
                "N 个格点的环上的懒惰游走（以 1/3 的概率原地不动，否则跳到最近的 K 个邻居之一），加一条有向捷径，"
                "其概率取自捷径起点停留概率的 β 倍。N = 100 时，按报告的判峰规则，K = 2 在 0.0005 ≤ β ≤ 0.05、"
                "K = 4 在 0.001 ≤ β ≤ 0.15 范围内 f(t) 有两个峰；蒙特卡洛路径分类说明每个峰由哪些路径构成。"
            ),
            "narrative": {
                "model_overview": (
                    "N 个格点的周期环。每一步以 1 − q（q = 2/3）的概率原地不动，否则以 q/K 的概率跳到最近的 K 个邻居之一"
                    "（±1 到 ±K/2）；K = 2 或 4。从格点 1 出发，目标为格点 1 + N/2，首次到达即被吸收。一条有向捷径从格点 6 "
                    "指向目标的下一个格点，其概率 β(1 − q) 取自格点 6 的停留概率。"
                ),
                "method_overview": (
                    "f(t) 用两种方法精确计算：生成函数的数值反演（Abate–Whitt 方法，捷径用 Sherman–Morrison 秩一修正处理），"
                    "以及逐步推进主方程。峰指 f ≥ 10⁻⁷、且不低于最高峰 1% 的严格局部极大值。蒙特卡洛模拟 20 万条轨迹，"
                    "按是否走过捷径、是否越过目标给到达分类；对照计算中把越过目标视为吸收。"
                ),
                "result_overview": (
                    "两个峰只在捷径强度适中时出现：N = 100 时，K = 2 为 0.0005 ≤ β ≤ 0.05，K = 4 为 0.001 ≤ β ≤ 0.15。"
                    "β = 0.02 时第一个峰的到达全部走过捷径；K = 4 时，越过目标而没有走捷径的轨迹占第二峰时间窗的 23%。"
                ),
            },
            "key_findings": [
                "第一个峰来自捷径：N = 100、β = 0.02 时，无论 K = 2 还是 K = 4，第一个峰中到达的游走者全部走过捷径。",
                "第二个峰主要来自绕远路：第二个峰的到达中走过捷径的比例，K = 2 为 26%，K = 4 为 13%（N = 100，β = 0.02）。",
                "越过目标（一步 ±2 跨过目标而不落在目标上）只在 K = 4 时可能；越过目标而没有走捷径的轨迹占 K = 4 第二峰时间窗的 23%。",
                "两个峰只在捷径强度适中时存在：N = 100 时，β = 0 没有，K = 2 从 β = 0.07 起、K = 4 从 β = 0.2 起也没有。",
            ],
        },
    },
    "ring_lazy_jump_ext": {
        "en": {
            "teaser": 'First version of the shortcut-strength scan (N = 100): two peaks for 0.0005 ≤ β ≤ 0.05 (K = 2) and 0.001 ≤ β ≤ 0.15 (K = 4), one at β = 0 and 0.2; both peak times fall as β grows.',
            "title": "Lazy Ring Shortcut: β Scan (First Version)",
            "summary": (
                "On a lazy ring of N = 100 sites with one directed shortcut, this first version of the study scans the "
                "shortcut strength β for K = 2 and K = 4 neighbours. By the report's peak rule, f(t) has two peaks for "
                "0.0005 ≤ β ≤ 0.05 (K = 2) and 0.001 ≤ β ≤ 0.15 (K = 4) on the scanned grid, and one peak at β = 0 and "
                "β = 0.2; inside these windows both peak times fall as β grows."
            ),
            "narrative": {
                "model_overview": (
                    "Discrete-time walk on a periodic ring of N sites. At each step the walker stays put with probability "
                    "1 − q (q = 2/3) or moves to one of its K nearest neighbours (±1 to ±K/2), each with probability q/K; "
                    "K = 2 or K = 4. One directed shortcut from site 6 to the site just past the target takes probability "
                    "p = β(1 − q) out of the stay-put probability of site 6 only. The walker starts at site 1; T is the "
                    "first step at which it reaches the target, site 1 + N/2 (site 51 for N = 100)."
                ),
                "method_overview": (
                    "f(t) = Pr[T = t] is computed exactly by stepping the probability distribution forward until less "
                    "than 10⁻¹⁴ is left; the sweep of peak heights and tail rates uses Abate–Whitt numerical inversion of "
                    "the generating function. Peak rule: a peak is a strict local maximum of f(t) with f ≥ 10⁻⁷ and at "
                    "least 1% of the highest peak; f(t) counts as bimodal when two such peaks remain. Monte Carlo "
                    "(200 000 trajectories per case) sorts arrivals by route: shortcut used or not, target jumped over or not."
                ),
                "result_overview": (
                    "At N = 100, two peaks for 0.0005 ≤ β ≤ 0.05 (K = 2) and 0.001 ≤ β ≤ 0.15 (K = 4) on the scanned grid; "
                    "a finer sweep in steps of 0.01 puts the upper edges at β = 0.06 and 0.17. Inside these windows both "
                    "peak times decrease as β grows, and the tail decay rate γ rises over the whole range β = 0 to 0.2. "
                    "Which K keeps two peaks longer depends on β and N."
                ),
            },
            "key_findings": [
                "With no shortcut (β = 0), and again at β = 0.2, f(t) has a single peak for both K = 2 and K = 4 (N = 100).",
                "Inside the two-peak windows both peak times fall as β grows: K = 2, t₁ 54 → 48 and t₂ 1243 → 780 steps (β = 0.0005 → 0.05); K = 4, t₁ 32 → 27 and t₂ 515 → 295 steps (β = 0.001 → 0.15).",
                "K = 4 is not more robust everywhere: at β = 0.0005 only K = 2 has two peaks, and in the ring-size scan at β = 0.02 two peaks appear from N = 58 for K = 2 but only from N = 72 for K = 4.",
                "Route classes (Monte Carlo, 200 000 trajectories, N = 100, β = 0.01): every first-peak arrival used the shortcut; with K = 4 about 30% of them had also jumped over the target (a ±2 step across it) first, which is impossible with K = 2.",
                "Valley depth, measured as f(t_v)/max(f(t₁), f(t₂)) (smaller is deeper): at β = 0.01 it is 0.15 for K = 4 and 0.34 for K = 2; from β ≈ 0.05 the order reverses (0.56 for K = 4, 0.52 for K = 2).",
                "The tail decay rate γ = −ln λ_max rises with β from 0 to 0.2: from 3.3 × 10⁻⁴ to 8.5 × 10⁻⁴ per step for K = 2 and from 7.9 × 10⁻⁴ to 1.6 × 10⁻³ for K = 4.",
                "For the ring-size scan β is fixed at β* = 0.01, the smallest scanned value meeting the report's selection rule (t₂/t₁ ≥ 10, valley ratio ≤ 0.6, second peak at least 5% of the first) for both K; two peaks then appear from N = 60 (K = 2) and N = 74 (K = 4), N = 50 to 300.",
            ],
        },
        "cn": {
            "teaser": '捷径强度扫描的第一版（N = 100）：K = 2 在 0.0005 ≤ β ≤ 0.05、K = 4 在 0.001 ≤ β ≤ 0.15 范围内有两个峰，β = 0 与 0.2 时只有一个；两个峰的时间都随 β 增大而提前。',
            "title": "懒惰环捷径：β 扫描（第一版）",
            "summary": (
                "在 N = 100 个格点、带一条有向捷径的懒惰环上，这份第一版研究扫描了 K = 2 与 K = 4 两种近邻数下的捷径强度 β。"
                "按报告的判峰规则，在所扫描的 β 网格上，K = 2 在 0.0005 ≤ β ≤ 0.05、K = 4 在 0.001 ≤ β ≤ 0.15 范围内 f(t) "
                "有两个峰，β = 0 和 β = 0.2 时只有一个峰；在这些区间内，两个峰的时间都随 β 增大而提前。"
            ),
            "narrative": {
                "model_overview": (
                    "N 个格点周期环上的离散时间游走。每一步以 1 − q（q = 2/3）的概率原地不动，否则以 q/K 的概率跳到最近的 "
                    "K 个邻居之一（±1 到 ±K/2）；K = 2 或 K = 4。一条有向捷径从格点 6 指向目标的下一个格点，其概率 "
                    "p = β(1 − q) 只从格点 6 的停留概率中取出。游走者从格点 1 出发；T 是它第一次到达目标格点 1 + N/2 "
                    "（N = 100 时为格点 51）的步数。"
                ),
                "method_overview": (
                    "f(t) = Pr[T = t] 通过逐步推进概率分布精确计算，直到剩余概率小于 10⁻¹⁴；峰高与尾部衰减率的扫描用 "
                    "Abate–Whitt 方法对生成函数做数值反演。判峰规则：峰指 f ≥ 10⁻⁷、且不低于最高峰 1% 的严格局部极大值；"
                    "剩下两个这样的峰即算双峰。蒙特卡洛模拟（每种情形 20 万条轨迹）按路径给到达分类：是否走过捷径、是否越过目标。"
                ),
                "result_overview": (
                    "N = 100 时，在所扫描的网格上，K = 2 在 0.0005 ≤ β ≤ 0.05、K = 4 在 0.001 ≤ β ≤ 0.15 范围内有两个峰；"
                    "以 0.01 为步长的细扫描把上边界定在 β = 0.06 和 0.17。在这些区间内，两个峰的时间都随 β 增大而减小，"
                    "尾部衰减率 γ 在 β = 0 到 0.2 的整个范围内上升。哪个 K 的双峰保持得更久，取决于 β 和 N。"
                ),
            },
            "key_findings": [
                "没有捷径（β = 0）时，以及 β = 0.2 时，K = 2 和 K = 4 的 f(t) 都只有一个峰（N = 100）。",
                "在双峰区间内，两个峰的时间都随 β 增大而提前：K = 2 时 t₁ 从 54 步到 48 步、t₂ 从 1243 步到 780 步（β 从 0.0005 到 0.05）；K = 4 时 t₁ 从 32 步到 27 步、t₂ 从 515 步到 295 步（β 从 0.001 到 0.15）。",
                "K = 4 并非处处更稳健：β = 0.0005 时只有 K = 2 有两个峰；在 β = 0.02 的环长扫描中，K = 2 从 N = 58 起出现两个峰，K = 4 要到 N = 72 才出现。",
                "路径分类（蒙特卡洛，20 万条轨迹，N = 100，β = 0.01）：第一个峰的到达全部走过捷径；K = 4 时其中约 30% 还先越过了目标（一步 ±2 跨过目标），K = 2 不可能出现这种情况。",
                "谷深用 f(t_v)/max(f(t₁), f(t₂)) 衡量（越小越深）：β = 0.01 时 K = 4 为 0.15、K = 2 为 0.34；β 约为 0.05 起顺序反过来（K = 4 为 0.56，K = 2 为 0.52）。",
                "尾部衰减率 γ = −ln λ_max 随 β 从 0 增大到 0.2 而上升：K = 2 从每步 3.3 × 10⁻⁴ 升到 8.5 × 10⁻⁴，K = 4 从 7.9 × 10⁻⁴ 升到 1.6 × 10⁻³。",
                "环长扫描固定 β* = 0.01，这是所扫描的 β 中同时让两种 K 满足报告选取规则（t₂/t₁ ≥ 10、谷比 ≤ 0.6、第二峰不低于第一峰的 5%）的最小值；此时 N 取 50 到 300，K = 2 从 N = 60 起、K = 4 从 N = 74 起出现两个峰。",
            ],
        },
    },
    "ring_lazy_jump_ext_rev2": {
        "en": {
            "teaser": 'Revision at N = 100, β = 0.01: f(t) drawn with the route classes of each peak, and checks against the peak thresholds, the choice of time windows (class shares move by under 0.6 points) and Monte Carlo error.',
            "title": "Lazy Ring Shortcut: Robustness Checks",
            "summary": (
                "Revision of the β-scan study at N = 100 and β = 0.01. It plots f(t) together with the route classes of "
                "the arrivals in each peak, and checks how the conclusions depend on the peak-detection thresholds, on the "
                "time windows (shifting or resizing them by 1 to 5 steps changes every class share by less than 0.6 "
                "percentage points) and on Monte Carlo sampling error (95% intervals)."
            ),
            "narrative": {
                "model_overview": (
                    "The lazy ring of the first version: N = 100, K = 2 or 4, q = 2/3 (stay-put probability 1/3), start at "
                    "site 1, target site 51, directed shortcut 6 → 52 with strength β = 0.01."
                ),
                "method_overview": (
                    "Exact f(t) and Monte Carlo route classes (200 000 walkers) in three time windows around the first peak, "
                    "the valley and the second peak (half-width 5% of t₂ − t₁). Three checks: a grid of peak-detection "
                    "thresholds, shifting or resizing the windows by 1 to 5 steps, and 95% confidence intervals for the "
                    "class shares."
                ),
                "result_overview": (
                    "Peak and valley times: K = 2, 53, 247 and 1124 steps; K = 4, 32, 84 and 495 steps. Moving or resizing "
                    "the windows changes any class share by less than 0.6 percentage points; on the threshold grid the "
                    "two-peak test passes about 33% of combinations for K = 2 and 60% for K = 4, the valley-depth threshold "
                    "mattering most."
                ),
            },
            "key_findings": [
                "Peak, valley and second-peak times at N = 100, β = 0.01: K = 2, 53, 247 and 1124 steps; K = 4, 32, 84 and 495 steps.",
                "Shifting or resizing the three time windows by 1 to 5 steps changes every route-class share by less than 0.6 percentage points (at most 0.45 for K = 2 and 0.58 for K = 4).",
                "Over 81 threshold settings and five β values between 0.001 and 0.03, the two-peak test passes about 33% of the time for K = 2 and 60% for K = 4; the valley-depth threshold is the most sensitive.",
                "The 95% confidence intervals of the Monte Carlo class shares are narrow (mean width about 0.01 for K = 2 and 0.03 for K = 4) and smaller than the differences between classes.",
            ],
        },
        "cn": {
            "teaser": '修订版（N = 100，β = 0.01）：把 f(t) 与各峰的路径类别画在一起，并检验判峰阈值、时间窗选择（类别占比变化不到 0.6 个百分点）和蒙特卡洛误差的影响。',
            "title": "懒惰环捷径：稳健性检验",
            "summary": (
                "β 扫描研究的修订版，固定 N = 100、β = 0.01。它把 f(t) 与各峰中到达轨迹的路径类别画在一起，并检验结论对"
                "判峰阈值、时间窗（平移或改变宽度 1 到 5 步时，各类别占比的变化都小于 0.6 个百分点）和蒙特卡洛抽样误差"
                "（95% 置信区间）的敏感程度。"
            ),
            "narrative": {
                "model_overview": (
                    "与第一版相同的懒惰环：N = 100，K = 2 或 4，q = 2/3（停留概率 1/3），从格点 1 出发，目标为格点 51，"
                    "有向捷径 6 → 52，强度 β = 0.01。"
                ),
                "method_overview": (
                    "精确计算 f(t)，并用蒙特卡洛（20 万条轨迹）统计第一个峰、谷和第二个峰附近三个时间窗内的路径类别"
                    "（半宽为 t₂ − t₁ 的 5%）。三项检验：判峰阈值网格、把时间窗平移或改变宽度 1 到 5 步、类别占比的 95% 置信区间。"
                ),
                "result_overview": (
                    "峰、谷与第二峰的时间：K = 2 为 53、247、1124 步；K = 4 为 32、84、495 步。平移或改变时间窗宽度时，"
                    "任一类别占比的变化都小于 0.6 个百分点；在阈值网格上，双峰判定对 K = 2 约有 33% 的组合通过，对 K = 4 约 60%，"
                    "影响最大的是谷深阈值。"
                ),
            },
            "key_findings": [
                "N = 100、β = 0.01 时峰、谷与第二峰的时间：K = 2 为 53、247、1124 步；K = 4 为 32、84、495 步。",
                "把三个时间窗平移或改变宽度 1 到 5 步，各路径类别占比的变化都小于 0.6 个百分点（K = 2 最多 0.45，K = 4 最多 0.58）。",
                "在 81 组阈值设置和 0.001 到 0.03 之间的 5 个 β 值上，双峰判定对 K = 2 约有 33% 通过，对 K = 4 约 60%；最敏感的是谷深阈值。",
                "蒙特卡洛类别占比的 95% 置信区间较窄（平均宽度 K = 2 约 0.01，K = 4 约 0.03），小于类别之间的差异。",
            ],
        },
    },
    "ring_lazy_flux": {
        "en": {
            "teaser": 'Nearest-neighbour lazy ring with a shortcut drawn from the stay-put probability: a closed-form generating function checked by a flux recursion; the smallest ring with two well-separated peaks has N = 10.',
            "title": "Lazy Ring Flux Baseline",
            "summary": (
                "A lazy nearest-neighbour ring (stay, left and right each with probability 1/3) with one directed shortcut "
                "whose probability is taken from the stay-put probability at its source. The generating function is "
                "derived in closed form, inverted numerically (Abate–Whitt) and checked against a step-by-step flux "
                "recursion. The smallest ring with two well-separated peaks has N = 10; giving the shortcut source four "
                "equal options instead removes the second peak for every N from 10 to 200 tested."
            ),
            "narrative": {
                "model_overview": (
                    "Ring of N sites with nearest-neighbour steps (K = 2): stay with probability 1 − q, move ±1 with q/2 "
                    "each; q = 2/3 gives 1/3 for each. One directed shortcut u → v, given probability in one of two ways: "
                    "taken from the stay-put probability at u (0 ≤ p ≤ 1 − q; in scans p = β(1 − q)), or by giving u four "
                    "equal options (stay, left, right, shortcut, 1/4 each)."
                ),
                "method_overview": (
                    "Closed-form generating function (Chebyshev form), numerical inversion by Abate–Whitt, and an "
                    "independent time-domain flux recursion; the four-equal-options rule uses a rank-one Sherman–Morrison "
                    "update. A peak is a strict local maximum with f ≥ 10⁻⁷, the second at least 1% of the highest; well "
                    "separated means t₂/t₁ ≥ 10."
                ),
                "result_overview": (
                    "With the shortcut taken from the stay-put probability, the smallest example with two well-separated "
                    "peaks is N = 10 (peaks at t = 1 and t = 10). With four equal options at the source, no ring with "
                    "N = 10 to 200 has two peaks in the scanned geometry."
                ),
            },
            "key_findings": [
                "Minimal example: N = 10, start at site 1, target site 5, shortcut 1 → 5 with p = 0.02/3; f(t) has exactly two peaks, at t = 1 and t = 10.",
                "The closed-form generating function is checked against an independent step-by-step flux recursion.",
                "Scanning N = 3 to 60 over all target positions (shortcut from the start to the target, β = 0.02), well-separated peaks first appear at N = 10, and for N ≥ 37 only when the target is 5 to 12 sites from the start.",
                "With four equal options at the shortcut source, none of the rings with N = 10 to 200 has two peaks (start at site 1, target at N/2, shortcut from site 6 to the site after the target).",
            ],
        },
        "cn": {
            "teaser": '捷径概率取自停留概率的最近邻懒惰环：生成函数闭式与通量递推相互核对；出现两个分得很开的峰的最小环是 N = 10。',
            "title": "懒惰环通量基线",
            "summary": (
                "最近邻懒惰环（停留、左移、右移的概率各为 1/3）加一条有向捷径，其概率取自捷径起点的停留概率。"
                "报告推导出生成函数的闭式，用 Abate–Whitt 方法做数值反演，并与逐步计算的通量递推核对。"
                "出现两个分得很开的峰的最小环是 N = 10；若改为让捷径起点的四个去向概率相等，则在所测试的 N = 10 到 200 中第二个峰都不出现。"
            ),
            "narrative": {
                "model_overview": (
                    "N 个格点的最近邻环（K = 2）：以 1 − q 的概率停留，以各 q/2 的概率移动 ±1；q = 2/3 时三者各为 1/3。"
                    "一条有向捷径 u → v，其概率有两种给法：从 u 的停留概率中取出（0 ≤ p ≤ 1 − q；扫描中 p = β(1 − q)），"
                    "或让 u 的四个去向（停留、左、右、捷径）各占 1/4。"
                ),
                "method_overview": (
                    "生成函数的闭式（切比雪夫形式），用 Abate–Whitt 方法数值反演，再用独立的时域通量递推核对；四去向等概率的"
                    "规则用 Sherman–Morrison 秩一修正处理。峰指 f ≥ 10⁻⁷ 的严格局部极大值，第二个峰不低于最高峰的 1%；"
                    "t₂/t₁ ≥ 10 称为分得很开。"
                ),
                "result_overview": (
                    "捷径概率取自停留概率时，出现两个分得很开的峰的最小例子是 N = 10（峰在 t = 1 和 t = 10）。"
                    "起点四个去向等概率时，在所扫描的几何构型中，N = 10 到 200 的环都没有两个峰。"
                ),
            },
            "key_findings": [
                "最小例子：N = 10，从格点 1 出发，目标为格点 5，捷径 1 → 5，p = 0.02/3；f(t) 恰好有两个峰，在 t = 1 和 t = 10。",
                "生成函数的闭式与独立的逐步通量递推相互核对。",
                "对 N = 3 到 60、所有目标位置扫描（捷径从起点指向目标，β = 0.02）：分得很开的两个峰从 N = 10 开始出现；N ≥ 37 时只在目标距起点 5 到 12 个格点时出现。",
                "捷径起点四个去向等概率时，N = 10 到 200 的环都没有两个峰（从格点 1 出发，目标在 N/2，捷径从格点 6 指向目标的下一个格点）。",
            ],
        },
    },
    "ring_valley": {
        "en": {
            "teaser": 'Non-lazy ring with a one-way shortcut past the target: over even N = 10–160, no two peaks for K = 2; two peaks for N = 48–52 (K = 4), 68–104 (K = 6), and 14 and 88–160 (K = 8).',
            "title": "Ring Valley Regime Map",
            "summary": (
                "A non-lazy ring with K neighbours, start at site 1, target at site N/2 and a one-way shortcut from site 6 "
                "to site N/2 + 1, computed by Abate–Whitt generating-function inversion and checked by Monte Carlo. Over "
                "even N from 10 to 160, two peaks never appear for K = 2, and appear for N = 48–52 (K = 4), 68–104 (K = 6), "
                "and N = 14 and 88–160 (K = 8)."
            ),
            "narrative": {
                "model_overview": (
                    "Non-lazy ring of N sites (N even): each step goes to one of the K nearest neighbours (±1 to ±K/2) with "
                    "probability 1/K. Start at site 1, absorbing target at site N/2; a one-way shortcut from site 6 to site "
                    "N/2 + 1, one site past the target; at site 6 the K + 1 options each have probability 1/(K + 1)."
                ),
                "method_overview": (
                    "Generating-function inversion by Abate–Whitt (up to t = 2000), checked against the master equation; "
                    "Monte Carlo (2 million walkers in total) for the route classes. Two peaks means two local maxima above "
                    "10⁻⁷, the smaller at least 1% of the larger; for K = 2, pairs of consecutive steps are summed first to "
                    "remove the odd/even oscillation of a non-lazy walk."
                ),
                "result_overview": (
                    "Over even N from 10 to 160: K = 2 never has two peaks; K = 4 has them for N = 48–52, K = 6 for "
                    "N = 68–104, K = 8 for N = 14 and N = 88–160. In the case N = 100, K = 6 the peaks are at t = 14 and "
                    "t = 101, with the valley at t = 74."
                ),
            },
            "key_findings": [
                "K = 2: no two-peak case for even N from 10 to 160, nor in an extra check over other shortcut positions with N from 6 to 80.",
                "Ranges of N with two peaks: 48–52 for K = 4, 68–104 for K = 6, and N = 14 and 88–160 for K = 8.",
                "N = 100, K = 6: first peak at t = 14, valley at t = 74, second peak at t = 101.",
                "Route classes (Monte Carlo): about 96% of the early, direct arrivals used the shortcut once, against about 47% of the late, indirect arrivals that used it at least once.",
            ],
        },
        "cn": {
            "teaser": '单向捷径越过目标的非懒惰环：N 取 10 到 160 的偶数时，K = 2 没有双峰；K = 4 在 N = 48–52、K = 6 在 68–104、K = 8 在 14 和 88–160 时有两个峰。',
            "title": "环上的谷与双峰区间图",
            "summary": (
                "非懒惰环，每步跳到最近的 K 个邻居之一；从格点 1 出发，目标在格点 N/2，一条单向捷径从格点 6 指向格点 "
                "N/2 + 1。用 Abate–Whitt 方法反演生成函数计算，并用蒙特卡洛核对。在 N 取 10 到 160 的偶数时，K = 2 "
                "从不出现两个峰；K = 4 在 N = 48–52、K = 6 在 N = 68–104、K = 8 在 N = 14 和 88–160 时出现两个峰。"
            ),
            "narrative": {
                "model_overview": (
                    "N 个格点（N 为偶数）的非懒惰环：每一步以 1/K 的概率跳到最近的 K 个邻居之一（±1 到 ±K/2）。从格点 1 "
                    "出发，吸收目标在格点 N/2；一条单向捷径从格点 6 指向格点 N/2 + 1，即目标的下一个格点；在格点 6，"
                    "K + 1 个去向的概率各为 1/(K + 1)。"
                ),
                "method_overview": (
                    "用 Abate–Whitt 方法反演生成函数（算到 t = 2000），并用主方程核对；路径类别用蒙特卡洛统计（共 200 万条轨迹）。"
                    "两个峰指两个高于 10⁻⁷ 的局部极大值，较小者不低于较大者的 1%；K = 2 时先把相邻两步合并，以消除非懒惰游走的奇偶振荡。"
                ),
                "result_overview": (
                    "N 取 10 到 160 的偶数时：K = 2 从不出现两个峰；K = 4 在 N = 48–52、K = 6 在 N = 68–104、K = 8 在 N = 14 "
                    "和 N = 88–160 时出现两个峰。N = 100、K = 6 时两个峰在 t = 14 和 t = 101，谷在 t = 74。"
                ),
            },
            "key_findings": [
                "K = 2：N 取 10 到 160 的偶数时没有双峰；改变捷径位置、N 取 6 到 80 的补充检查中也没有。",
                "出现两个峰的 N 范围：K = 4 为 48–52，K = 6 为 68–104，K = 8 为 N = 14 和 88–160。",
                "N = 100、K = 6：第一个峰在 t = 14，谷在 t = 74，第二个峰在 t = 101。",
                "路径分类（蒙特卡洛）：早到的直达轨迹约 96% 走过一次捷径，晚到的间接轨迹中约 47% 至少走过一次。",
            ],
        },
    },
    "ring_valley_dst": {
        "en": {
            "teaser": "Ring with N = 100 and K = 6 in which only the shortcut's landing site changes: landing sites 43–57 give two peaks when the shortcut leaves site 6, and 18 landing sites do when it leaves the start.",
            "title": "Destination-Scan Valley Control (N = 100, K = 6)",
            "summary": (
                "A non-lazy ring with N = 100, K = 6 and the target at site 50, in which only the landing site of the "
                "shortcut is varied. With the shortcut leaving site 6, landing sites 43 to 57 give two peaks; with it "
                "leaving the start site, 18 landing sites do. Flux recursion and Abate–Whitt inversion agree to about "
                "10⁻¹³, and Monte Carlo counts of shortcut use are compared with the peak heights."
            ),
            "narrative": {
                "model_overview": (
                    "Non-lazy ring, N = 100, K = 6 (steps ±1, ±2, ±3), start at site 1, target at site 50. One directed "
                    "shortcut with probability 1/7 at its source: site 6 in case A, the start site in case B; every landing "
                    "site from 1 to 100 is tried."
                ),
                "method_overview": (
                    "Abate–Whitt inversion cross-checked with a deterministic flux recursion (largest difference about "
                    "10⁻¹³); Monte Carlo (500 000 walkers) with Wilson confidence intervals for shortcut use. A peak is a "
                    "local maximum above 10⁻⁷, the second at least 1% of the highest; a stricter filter also requires the "
                    "peaks to be at least 12 steps apart."
                ),
                "result_overview": (
                    "Case A: two peaks for landing sites 43 to 57 (14 sites after the separation filter). Case B: 18 landing "
                    "sites, 7 of them with a late second peak after the filter (sites 36–39 and 62–64). In case A the ratio "
                    "of the peak heights tracks shortcut use closely (Pearson r = −0.97)."
                ),
            },
            "key_findings": [
                "Case A (shortcut from site 6): landing sites 43 to 57 give two peaks; 14 remain when the peaks must be at least 12 steps apart.",
                "Case B (shortcut from the start site): 18 landing sites give two peaks; 7 have a late second peak after the separation filter (sites 36–39 and 62–64).",
                "In case A the ratio of the two peak heights correlates with shortcut use across landing sites (Pearson r = −0.97).",
                "In case B a smaller second peak goes with less shortcut use, the opposite of the hypothesis the report set out to test.",
            ],
        },
        "cn": {
            "teaser": 'N = 100、K = 6 的环上只改变捷径落点：捷径从格点 6 出发时，落点 43 到 57 出现两个峰；从起点出发时有 18 个落点出现两个峰。',
            "title": "捷径落点扫描与谷的调控（N = 100，K = 6）",
            "summary": (
                "N = 100、K = 6、目标在格点 50 的非懒惰环，只改变捷径的落点。捷径从格点 6 出发时，落点在 43 到 57 之间"
                "会出现两个峰；从起点出发时，有 18 个落点出现两个峰。通量递推与 Abate–Whitt 反演的结果相差约 10⁻¹³，"
                "并用蒙特卡洛统计的捷径使用次数与峰高对照。"
            ),
            "narrative": {
                "model_overview": (
                    "非懒惰环，N = 100，K = 6（步长 ±1、±2、±3），从格点 1 出发，目标在格点 50。一条有向捷径，在起点处的概率为 "
                    "1/7：情形 A 从格点 6 出发，情形 B 从起点出发；落点逐一取遍 1 到 100。"
                ),
                "method_overview": (
                    "Abate–Whitt 反演与确定性通量递推相互核对（最大差约 10⁻¹³）；蒙特卡洛（50 万条轨迹）给出捷径使用比例及其 "
                    "Wilson 置信区间。峰指高于 10⁻⁷ 的局部极大值，第二个峰不低于最高峰的 1%；更严格的筛选还要求两峰相隔至少 12 步。"
                ),
                "result_overview": (
                    "情形 A：落点 43 到 57 有两个峰（加间隔筛选后剩 14 个）。情形 B：18 个落点有两个峰，筛选后其中 7 个第二峰较晚"
                    "（落点 36–39 和 62–64）。情形 A 中两峰高度之比与捷径使用比例高度相关（Pearson r = −0.97）。"
                ),
            },
            "key_findings": [
                "情形 A（捷径从格点 6 出发）：落点 43 到 57 有两个峰；要求两峰相隔至少 12 步时剩 14 个。",
                "情形 B（捷径从起点出发）：18 个落点有两个峰；间隔筛选后其中 7 个第二峰较晚（落点 36–39 和 62–64）。",
                "情形 A 中，不同落点下两峰高度之比与捷径使用比例相关（Pearson r = −0.97）。",
                "情形 B 中，第二峰越小，捷径用得越少，与报告原本要检验的假设相反。",
            ],
        },
    },
    "ring_deriv_k2": {
        "en": {
            "teaser": 'Exact propagators and first-passage generating function for a lazy nearest-neighbour ring with one directed link, checked against direct matrix inversion to within 3.11 × 10⁻¹⁵.',
            "title": "Ring Derivation Backbone (K = 2)",
            "summary": (
                "Exact derivation for a lazy nearest-neighbour ring with one directed shortcut: the propagator without the "
                "shortcut in Chebyshev form, the propagator with it (by a rank-one Sherman–Morrison update and by a "
                "determinant formula) for two ways of adding the shortcut, and the first-passage generating function. "
                "Checked against direct matrix inversion: largest error 3.11 × 10⁻¹⁵ over 200 random cases."
            ),
            "narrative": {
                "model_overview": (
                    "Lazy nearest-neighbour walk on a periodic ring of N sites (K = 2) with one directed long-range link. "
                    "The link either takes its probability from the stay-put probability (0 ≤ p ≤ 1 − q) or is rewired "
                    "from one neighbour step (0 ≤ p ≤ q/2)."
                ),
                "method_overview": (
                    "Propagator of the ring without the link in Chebyshev form; propagator with the link by a rank-one "
                    "Sherman–Morrison update and, independently, by a determinant formula for local defects; first-passage "
                    "generating function as a ratio of two propagators."
                ),
                "result_overview": (
                    "Closed forms for both constructions, an explicit Chebyshev form of the first-passage generating "
                    "function when the link takes probability from staying put, and a comparison with Watts–Strogatz "
                    "rewiring; 200 random cases with N ≤ 40 agree with matrix inversion to within 3.11 × 10⁻¹⁵."
                ),
            },
            "key_findings": [
                "The propagator of the ring without the link has a closed Chebyshev form.",
                "Adding one directed link is a rank-one change: the Sherman–Morrison update and the determinant formula give the same propagator.",
                "The first-passage generating function is a ratio of two propagators, with an explicit closed form when the link takes probability from staying put.",
                "200 random test cases with N ≤ 40 agree with direct matrix inversion to within 3.11 × 10⁻¹⁵.",
            ],
        },
        "cn": {
            "teaser": '带一条有向连边的最近邻懒惰环：传播子与首达生成函数的精确推导，与直接矩阵求逆的结果相差不超过 3.11 × 10⁻¹⁵。',
            "title": "环模型推导主干（K = 2）",
            "summary": (
                "对带一条有向捷径的最近邻懒惰环做精确推导：无捷径时的传播子（切比雪夫形式），两种加捷径方式下的传播子"
                "（分别用 Sherman–Morrison 秩一修正和行列式公式求得），以及首达生成函数。与直接矩阵求逆核对：200 个随机情形的最大误差为 3.11 × 10⁻¹⁵。"
            ),
            "narrative": {
                "model_overview": (
                    "N 个格点周期环上的最近邻懒惰游走（K = 2），加一条有向长程连边。连边的概率或取自停留概率"
                    "（0 ≤ p ≤ 1 − q），或由一个邻居方向的跳跃改接而来（0 ≤ p ≤ q/2）。"
                ),
                "method_overview": (
                    "先求无连边时环的传播子（切比雪夫形式）；再分别用 Sherman–Morrison 秩一修正和局部缺陷的行列式公式求有连边时的"
                    "传播子；首达生成函数等于两个传播子之比。"
                ),
                "result_overview": (
                    "两种构造都有闭式结果；连边概率取自停留概率时，首达生成函数有显式的切比雪夫形式；并与 Watts–Strogatz 改接作比较。"
                    "N ≤ 40 的 200 个随机情形与矩阵求逆的结果相差不超过 3.11 × 10⁻¹⁵。"
                ),
            },
            "key_findings": [
                "无连边时，环的传播子有切比雪夫形式的闭式。",
                "加一条有向连边是秩一改变：Sherman–Morrison 修正与行列式公式给出相同的传播子。",
                "首达生成函数是两个传播子之比；连边概率取自停留概率时有显式闭式。",
                "N ≤ 40 的 200 个随机测试情形与直接矩阵求逆的结果相差不超过 3.11 × 10⁻¹⁵。",
            ],
        },
    },
    "ring_two_target": {
        "en": {
            "teaser": 'Lazy ring with two targets, computed exactly: drift alone can give two peaks; with a shortcut, two peaks from N ≥ 45 (K = 2) or N ≥ 50 (K = 4); three peaks in one hand-built case.',
            "title": "Two-Target Lazy Ring Mechanics",
            "summary": (
                "A lazy ring with two absorbing targets and an optional drift, computed exactly step by step. Drift alone "
                "can produce two arrival peaks. With a directed shortcut that takes a fraction β of the stay-put "
                "probability at its source, two peaks appear for N ≥ 45 (K = 2) or N ≥ 50 (K = 4) in the scanned range and "
                "never at β = 0; three peaks were found in one hand-built case without a shortcut."
            ),
            "narrative": {
                "model_overview": (
                    "Lazy ring with the start at site 0 and two absorbing targets; K = 2 or 4. Each step moves with "
                    "probability q, forward with weight (1 + g)/2 and backward with weight (1 − g)/2 (drift g between −1 "
                    "and 1), and otherwise stays. Optional shortcut: at its source, probability β(1 − q) moves from staying "
                    "put to the shortcut."
                ),
                "method_overview": (
                    "Exact time-domain recursion for the absorbing chain, with f(t) = f₁(t) + f₂(t) split by target; scans "
                    "over N and β. Peaks are strict local maxima above 10⁻¹², kept if at least 1% of the highest; two peaks "
                    "with t₂/t₁ ≥ 10 count as well separated."
                ),
                "result_overview": (
                    "Without a shortcut, drift alone gives two peaks in the two drift cases. In the (N, β) scan with the "
                    "targets at site ⌊N/2⌋ and the next site, two peaks need β > 0 and appear for N ≥ 45 (K = 2) and N ≥ 50 "
                    "(K = 4). Three peaks (t = 1, 17 and 43) occur in one case: K = 4, N = 30, q = 0.9, drift 0.8, no shortcut."
                ),
            },
            "key_findings": [
                "Example with a shortcut (N = 60, targets at sites 30 and 31, shortcut 5 → 31, β = 0.02): peaks at t = 36 and 387 for K = 2, and at t = 15 and 169 for K = 4.",
                "In the scan with targets at site ⌊N/2⌋ and the next site there is no two-peak case at β = 0; two peaks appear for N ≥ 45 (K = 2) and N ≥ 50 (K = 4).",
                "Three peaks appear in a single hand-built case without a shortcut (K = 4, N = 30, q = 0.9, drift 0.8), at t = 1, 17 and 43.",
                "A small scan of 240 cases gives 34 double peaks, 26 shoulders, 10 local bumps and 170 single peaks.",
            ],
        },
        "cn": {
            "teaser": '双目标懒惰环的精确计算：仅靠漂移就可能出现两个峰；加捷径后 K = 2 从 N ≥ 45、K = 4 从 N ≥ 50 起出现两个峰；三个峰只出现在一个人为构造的情形中。',
            "title": "双目标懒惰环的机制",
            "summary": (
                "带两个吸收目标、可加漂移的懒惰环，逐步精确计算。仅靠漂移就可能出现两个到达峰。加一条有向捷径"
                "（其概率取自起点停留概率的 β 倍）后，在所扫描范围内 K = 2 从 N ≥ 45、K = 4 从 N ≥ 50 起出现两个峰，"
                "β = 0 时从不出现；三个峰只在一个人为构造、没有捷径的情形中出现。"
            ),
            "narrative": {
                "model_overview": (
                    "懒惰环，从格点 0 出发，有两个吸收目标；K = 2 或 4。每一步以概率 q 移动，向前的权重为 (1 + g)/2，"
                    "向后为 (1 − g)/2（漂移 g 在 −1 与 1 之间），否则停留。可选的捷径：在捷径起点，把 β(1 − q) 的概率从停留移给捷径。"
                ),
                "method_overview": (
                    "对吸收链做精确的时域递推，按目标分解 f(t) = f₁(t) + f₂(t)；对 N 和 β 扫描。峰指高于 10⁻¹² 的严格局部极大值，"
                    "且不低于最高峰的 1%；两个峰满足 t₂/t₁ ≥ 10 时称为分得很开。"
                ),
                "result_overview": (
                    "没有捷径时，两个漂移情形仅靠漂移就有两个峰。在目标位于格点 ⌊N/2⌋ 及其下一个格点的 (N, β) 扫描中，"
                    "两个峰需要 β > 0，K = 2 从 N ≥ 45、K = 4 从 N ≥ 50 起出现。三个峰（t = 1、17、43）只出现在一个情形中："
                    "K = 4，N = 30，q = 0.9，漂移 0.8，没有捷径。"
                ),
            },
            "key_findings": [
                "带捷径的例子（N = 60，目标在格点 30 和 31，捷径 5 → 31，β = 0.02）：K = 2 的峰在 t = 36 和 387，K = 4 的峰在 t = 15 和 169。",
                "目标位于格点 ⌊N/2⌋ 及其下一个格点的扫描中，β = 0 时没有双峰；K = 2 从 N ≥ 45、K = 4 从 N ≥ 50 起出现两个峰。",
                "三个峰只出现在一个人为构造、没有捷径的情形中（K = 4，N = 30，q = 0.9，漂移 0.8），在 t = 1、17、43。",
                "240 个情形的小规模扫描中：34 个双峰，26 个肩，10 个局部隆起，170 个单峰。",
            ],
        },
    },
    "ring_two_walker_encounter_shortcut": {
        "en": {
            "teaser": 'Two lazy walkers on a ring of 101 sites, one with a shortcut: the exact first-encounter time has a clear second peak from shortcut strength β ≈ 0.15, and earlier on larger rings.',
            "summary": (
                "Two independent lazy walkers with opposite drifts on a ring of 101 sites, one of them with a directed "
                "shortcut; their first-encounter distribution is computed exactly. A second encounter peak at least 20% as "
                "high as the first appears from shortcut strength β ≈ 0.15, and earlier on larger rings (β ≈ 0.04 at "
                "N = 141). The appendix generating-function formula is checked against its mode sum (relative error "
                "≤ 1.4 × 10⁻¹⁶)."
            ),
        },
        "cn": {
            "teaser": '101 个格点的环上两个懒惰游走者，其中一个有捷径：精确计算的首次相遇时间从捷径强度 β 约 0.15 起出现明显的第二个峰，环越大出现得越早。',
            "summary": (
                "环上（101 个格点）两个漂移方向相反、相互独立的懒惰游走者，其中一个有一条有向捷径；精确计算二者的首次相遇时间分布。"
                "捷径强度 β 约为 0.15 起，出现高度不低于第一个峰 20% 的第二个相遇峰；环越大出现得越早（N = 141 时 β 约为 0.04）。"
                "附录中的生成函数公式与其模式求和相互核对（相对误差不超过 1.4 × 10⁻¹⁶）。"
            ),
        },
    },
    "grid2d_bimodality": {
        "en": {
            "teaser": 'Three hand-built geometries on a 60 × 60 lattice (wrap-around drift, an edge corridor, a wall with one door) each give a fast and a slow route and two arrival peaks.',
            "title": "Grid2D Bimodality Baseline",
            "summary": (
                "On a 60 × 60 lattice (lazy walk with drift; periodic in x, reflecting in y), three hand-built geometries — "
                "a drift that wraps around, an edge corridor with a local bias, and a wall with one door — each give a fast "
                "and a slow route to one target and two arrival peaks, with the valley at most 7% of the smaller peak. "
                "f(t) is computed exactly and by Abate–Whitt inversion (L¹ difference below 10⁻¹²) and checked by Monte Carlo."
            ),
            "narrative": {
                "model_overview": (
                    "60 × 60 lattice, one absorbing target, periodic boundary in x and reflecting in y. Lazy walk: move with "
                    "probability 0.8, stay with 0.2; global drift (g_x, g_y) tilts the four step probabilities. Local "
                    "defects — biased sites, walls with doors, sticky sites — change individual transitions."
                ),
                "method_overview": (
                    "Exact recursion f(t) = rᵀQ^(t−1)p₀ as the baseline; generating function built from the defect-free "
                    "propagator plus a correction for each local defect, inverted by Abate–Whitt; Monte Carlo with 30 000 "
                    "walkers. Two peaks are found on f smoothed over 9 steps; valley ratio = f(t_v)/min(h₁, h₂), required to "
                    "be at most 0.07."
                ),
                "result_overview": (
                    "Case A (drift with wrap-around): peaks at t = 6 and 232. Case B (edge corridor with local bias): t = 33 "
                    "and 473, needing a corridor at least 6 sites long. Case C (wall with one door, no local bias): t = 88 and "
                    "500. An interior corridor instead of an edge corridor reduces the early peak to a shoulder."
                ),
            },
            "key_findings": [
                "All three constructions have two arrival peaks with valley ratio at most 0.07: case A at t = 6 and 232, case B at t = 33 and 473, case C at t = 88 and 500.",
                "Each peak corresponds to one route: f(t) splits into a fast part and a slow part (no wrap-around, staying in the corridor, or crossing the door early).",
                "Exact recursion and Abate–Whitt inversion agree to an L¹ error between 1.1 × 10⁻¹³ and 5.0 × 10⁻¹³.",
                "Moving the corridor away from the edge lowers the fast-route probability to about 1%, and the early peak becomes a shoulder.",
            ],
        },
        "cn": {
            "teaser": '60 × 60 格点上的三种人为构造（绕一圈的漂移、边缘走廊、有一扇门的墙）都给出一快一慢两条路径和两个到达峰。',
            "title": "二维格点双峰基线",
            "summary": (
                "在 60 × 60 的格点上（带漂移的懒惰游走；x 方向周期、y 方向反射），三种人为构造的几何——绕一圈的漂移、带局部偏置的"
                "边缘走廊、有一扇门的墙——都给出通往同一目标的一快一慢两条路径和两个到达峰，谷不超过较小峰的 7%。"
                "f(t) 用精确递推和 Abate–Whitt 反演两种方法计算（L¹ 差小于 10⁻¹²），并用蒙特卡洛核对。"
            ),
            "narrative": {
                "model_overview": (
                    "60 × 60 格点，一个吸收目标，x 方向周期边界、y 方向反射边界。懒惰游走：以 0.8 的概率移动、0.2 的概率停留；"
                    "整体漂移 (g_x, g_y) 改变四个方向的概率。局部缺陷——偏置格点、带门的墙、黏滞格点——改变个别转移概率。"
                ),
                "method_overview": (
                    "以精确递推 f(t) = rᵀQ^(t−1)p₀ 为基准；生成函数由无缺陷传播子加上每个局部缺陷的修正构成，用 Abate–Whitt "
                    "方法反演；蒙特卡洛 3 万条轨迹。在 9 步平滑后的 f 上找两个峰；谷比 = f(t_v)/min(h₁, h₂)，要求不超过 0.07。"
                ),
                "result_overview": (
                    "情形 A（绕一圈的漂移）：峰在 t = 6 和 232。情形 B（带局部偏置的边缘走廊）：t = 33 和 473，走廊至少要 6 个格点长。"
                    "情形 C（有一扇门的墙，无局部偏置）：t = 88 和 500。把边缘走廊换成内部走廊，早峰就退化成肩。"
                ),
            },
            "key_findings": [
                "三种构造都有两个到达峰，谷比不超过 0.07：情形 A 在 t = 6 和 232，情形 B 在 t = 33 和 473，情形 C 在 t = 88 和 500。",
                "每个峰对应一条路径：f(t) 可分成快、慢两部分（是否绕圈、是否留在走廊内、是否早早穿过门）。",
                "精确递推与 Abate–Whitt 反演的 L¹ 误差在 1.1 × 10⁻¹³ 到 5.0 × 10⁻¹³ 之间。",
                "把走廊从边缘移到内部，快路径的概率降到约 1%，早峰变成肩。",
            ],
        },
    },
    "grid2d_reflecting_bimodality": {
        "en": {
            "teaser": 'With all walls reflecting (60 × 60 lattice), eight representative geometries keep two arrival peaks, each with the valley at most 7% of the smaller peak.',
            "title": "Grid2D Reflecting-Boundary Bimodality",
            "summary": (
                "With all four walls reflecting (60 × 60 lattice, lazy walk), eight representative geometries — detours, a "
                "semi-permeable pore, a biased transport track, door arrays, a biased sticky belt along the walls and soft "
                "two-track layouts — each keep two arrival peaks, with the valley at most 7% of the smaller peak. Exact "
                "recursion and Abate–Whitt inversion agree, and Monte Carlo is overlaid."
            ),
            "narrative": {
                "model_overview": (
                    "60 × 60 lattice with all four boundaries reflecting, lazy walk (move with probability 0.8), one "
                    "absorbing target; local structures — detours, doors with crossing probability, biased tracks, sticky "
                    "sites — create a fast and a slow route."
                ),
                "method_overview": (
                    "Exact recursion as the baseline, Abate–Whitt inversion (L¹ difference at most 3.1 × 10⁻¹⁴) and Monte "
                    "Carlo with 30 000 to 60 000 walkers. Valley ratio = f(t_v)/min(h₁, h₂) on f smoothed over 9 steps."
                ),
                "result_overview": (
                    "All eight representative cases keep two peaks under fully reflecting walls, with valley ratios from "
                    "0.009 to 0.066. The fast-route probability ranges from 2% to 50% depending on the geometry."
                ),
            },
            "key_findings": [
                "Eight cases keep two peaks with all walls reflecting, e.g. a geometric detour (t = 136 and 424) and a door array (t = 347 and 2160).",
                "Valley ratios lie between 0.009 and 0.066, below the 0.07 threshold used across the Grid2D reports.",
                "A biased sticky belt along the walls, without any internal wall, is enough for two peaks (t = 6 and 642).",
                "The share of walkers taking the fast route ranges from about 2% to 50% across the cases.",
            ],
        },
        "cn": {
            "teaser": '四壁全反射时（60 × 60 格点），八种代表性几何都保持两个到达峰，谷都不超过较小峰的 7%。',
            "title": "二维格点全反射边界下的双峰",
            "summary": (
                "四壁全部反射时（60 × 60 格点，懒惰游走），八种代表性几何——绕行通道、半透孔道、带偏置的输运轨道、门阵列、"
                "沿墙的带偏置黏滞带和柔性双轨布局——都保持两个到达峰，谷不超过较小峰的 7%。精确递推与 Abate–Whitt 反演结果一致，"
                "并叠加了蒙特卡洛结果。"
            ),
            "narrative": {
                "model_overview": (
                    "60 × 60 格点，四条边界全部反射，懒惰游走（以 0.8 的概率移动），一个吸收目标；绕行通道、有通过概率的门、"
                    "带偏置的轨道、黏滞格点等局部结构形成一快一慢两条路径。"
                ),
                "method_overview": (
                    "以精确递推为基准，Abate–Whitt 反演（L¹ 差不超过 3.1 × 10⁻¹⁴），蒙特卡洛 3 万到 6 万条轨迹。谷比 = "
                    "f(t_v)/min(h₁, h₂)，在 9 步平滑后的 f 上计算。"
                ),
                "result_overview": (
                    "八个代表情形在全反射边界下都保持两个峰，谷比在 0.009 到 0.066 之间。走快路径的概率随几何不同在 2% 到 50% 之间。"
                ),
            },
            "key_findings": [
                "八个情形在全反射边界下都有两个峰，例如几何绕行（t = 136 和 424）和门阵列（t = 347 和 2160）。",
                "谷比在 0.009 到 0.066 之间，低于各二维格点报告统一使用的 0.07 阈值。",
                "沿墙的带偏置黏滞带、不加任何内部墙，就足以产生两个峰（t = 6 和 642）。",
                "各情形中走快路径的游走者比例约在 2% 到 50% 之间。",
            ],
        },
    },
    "grid2d_blackboard_bimodality": {
        "en": {
            "teaser": 'Negative result: with the start and the target at the two ends of a walled corridor, f(t) has one peak and a long tail; the apparent late bump is an artefact of the time window.',
            "title": "Grid2D Corridor-Endpoint Case (Negative Result)",
            "summary": (
                "Negative result for reflecting-wall geometries in which the start and the target sit at the two ends of "
                "a walled corridor (lattices of 60 × 60 and 30 × 30 sites, lazy walk): f(t) has a single peak and a long "
                "tail, and the apparent late bump sits at the start of the late time window, an artefact of that window. "
                "A second peak appears only after adding a sticky belt with a circulating bias around the outside."
            ),
            "narrative": {
                "model_overview": (
                    "Reflecting walls throughout. Case Z: 60 × 60 lattice, two internal walls forming a vertical corridor "
                    "with an upward bias inside, start and target at its two ends. Case S: the same idea in a smaller "
                    "rectangle inside a 30 × 30 lattice."
                ),
                "method_overview": (
                    "Exact recursion as the baseline, with Abate–Whitt inversion and Monte Carlo; peak finding with a "
                    "minimum separation, falling back to early and late time windows when it finds only one peak."
                ),
                "result_overview": (
                    "Both base cases show a single peak and a long tail. Variants with no drift, stronger drift, a weaker "
                    "corridor bias or an outer sticky belt still have one peak; only the sticky belt combined with a "
                    "circulating bias gives a second peak."
                ),
            },
            "key_findings": [
                "The corridor-endpoint geometries (cases Z and S) have a single peak and a long tail.",
                "The late bump in the base cases sits at the start of the late time window (t = 1500 for case Z): it is an artefact of the window, not a second peak.",
                "Changing the drift, weakening the corridor bias or adding an outer sticky belt alone does not create a second peak.",
                "A second peak appears only when the outer sticky belt also carries a circulating bias.",
            ],
        },
        "cn": {
            "teaser": '否定结果：起点和目标在有墙走廊的两端时，f(t) 只有一个峰加长尾；看似晚到的隆起是时间窗造成的假象。',
            "title": "二维格点走廊两端起止的情形（否定结果）",
            "summary": (
                "否定结果：在反射墙几何中，起点和目标分处一条有墙走廊的两端（60 × 60 与 30 × 30 格点，懒惰游走）时，f(t) "
                "只有一个峰加长尾；看似晚到的隆起位于晚时窗的起点，是时间窗造成的假象。只有在外围加上带环向偏置的黏滞带后，才出现第二个峰。"
            ),
            "narrative": {
                "model_overview": (
                    "处处为反射墙。情形 Z：60 × 60 格点，两道内墙围成一条竖直走廊，走廊内有向上的偏置，起点和目标在走廊两端。"
                    "情形 S：同样的构造，放在 30 × 30 格点内的一个较小矩形中。"
                ),
                "method_overview": (
                    "以精确递推为基准，辅以 Abate–Whitt 反演和蒙特卡洛；找峰时要求最小间隔，只找到一个峰时退而比较早、晚两个时间窗。"
                ),
                "result_overview": (
                    "两个基本情形都是单峰加长尾。去掉漂移、加强漂移、减弱走廊偏置或只加外围黏滞带的变体仍然只有一个峰；"
                    "只有黏滞带再加上环向偏置时才出现第二个峰。"
                ),
            },
            "key_findings": [
                "走廊两端起止的几何（情形 Z 和 S）只有一个峰加长尾。",
                "基本情形中的晚时隆起位于晚时窗的起点（情形 Z 为 t = 1500），是时间窗造成的假象，不是第二个峰。",
                "仅改变漂移、减弱走廊偏置或只加外围黏滞带，都不会产生第二个峰。",
                "只有外围黏滞带同时带有环向偏置时，才出现第二个峰。",
            ],
        },
    },
    "grid2d_two_target_double_peak": {
        "en": {
            "teaser": 'Two targets on a 31 × 31 reflecting lattice, one reached by a fast corridor and one by a slow corridor: all four hand-built cases have two peaks, one per target.',
            "title": "Grid2D Two-Target Double-Peak",
            "summary": (
                "Two absorbing targets on a 31 × 31 reflecting lattice, a near one reached by a fast biased corridor and a "
                "far one by a slow corridor. The arrival-time distribution f(t) = f₁(t) + f₂(t) is computed exactly; all "
                "four hand-built cases have two peaks, and a scan of 35 corridor settings maps where the double peak is "
                "clear, weak or absent."
            ),
            "narrative": {
                "model_overview": (
                    "31 × 31 lattice, reflecting on all four sides, lazy walk (move with probability 0.2). Start at the "
                    "centre; near target 7 sites to the east, reached through a biased corridor; far target reached through "
                    "a long slow corridor. Local bias moves 0.2 of the stay probability into the corridor direction."
                ),
                "method_overview": (
                    "Exact absorbing-chain recursion with the split f(t) = f₁(t) + f₂(t) by target, up to t = 6000. Peaks on f "
                    "smoothed over 7 steps; a double peak is clear when the peaks are separated by more than the sum of "
                    "their half-widths."
                ),
                "result_overview": (
                    "All four cases have two peaks, the first from the near target and the second from the far one (for "
                    "example t = 35 and 284, with 36% and 49% of the probability going to each target). The scan over slow-corridor "
                    "width and unbiased length separates clear, weak and single-peak regions."
                ),
            },
            "key_findings": [
                "Each peak belongs to one target: the near target gives the early peak and the far target the late one.",
                "Case C1: peaks at t = 35 and 284; 36% of walkers end at the near target and 49% at the far one within the computed time.",
                "Clear double peaks occur for slow-corridor widths 1 to 4, each only for particular lengths of the unbiased stretch; the widest corridor (5 cells) gives weak double peaks only.",
                "In an independent set of 11 sparse test cases, 2 have two peaks.",
            ],
        },
        "cn": {
            "teaser": '31 × 31 反射格点上的两个目标，一个经快走廊到达，一个经慢走廊到达：四个人为构造的情形都有两个峰，每个目标对应一个。',
            "title": "二维格点双目标双峰",
            "summary": (
                "31 × 31 反射格点上的两个吸收目标：近目标经一条快速的偏置走廊到达，远目标经一条慢走廊到达。到达时间分布 "
                "f(t) = f₁(t) + f₂(t) 精确计算；四个人为构造的情形都有两个峰，对 35 组走廊设置的扫描标出了双峰清晰、较弱和不出现的区域。"
            ),
            "narrative": {
                "model_overview": (
                    "31 × 31 格点，四边反射，懒惰游走（以 0.2 的概率移动）。从中心出发；近目标在东边 7 个格点处，经一条偏置走廊到达；"
                    "远目标经一条长而慢的走廊到达。局部偏置把停留概率的 0.2 移到走廊方向。"
                ),
                "method_overview": (
                    "对吸收链做精确递推，按目标分解 f(t) = f₁(t) + f₂(t)，算到 t = 6000。在 7 步平滑后的 f 上找峰；"
                    "两峰间距大于二者半宽之和时称为清晰双峰。"
                ),
                "result_overview": (
                    "四个情形都有两个峰，第一个来自近目标，第二个来自远目标（例如 t = 35 和 284，分别有 36% 和 49% 的概率到达两个目标）。"
                    "对慢走廊宽度和无偏置段长度的扫描区分出清晰双峰、弱双峰和单峰区域。"
                ),
            },
            "key_findings": [
                "每个峰对应一个目标：近目标给出早峰，远目标给出晚峰。",
                "情形 C1：峰在 t = 35 和 284；在计算时间内，36% 的游走者到达近目标，49% 到达远目标。",
                "慢走廊宽 1 到 4 格时可以出现清晰双峰，但各自只在特定的无偏置段长度下出现；最宽的走廊（5 格）只给出弱双峰。",
                "在另外 11 个稀疏测试情形中，有 2 个出现两个峰。",
            ],
        },
    },
    "grid2d_two_walker_encounter_shortcut": {
        "en": {
            "teaser": 'Two lazy walkers with shortcuts on an 11 × 11 reflecting lattice: the exact first-encounter time has two peaks for shortcut strength β = 0.30–0.60, though at β = 0.40 only about 18% of pairs have met by t = 900.',
            "summary": (
                "Two independent lazy walkers with opposite drifts on an 11 × 11 reflecting lattice, each with a directed "
                "shortcut; their first-encounter distribution is computed exactly in the time domain. It has one peak for "
                "shortcut strength β ≤ 0.25 and two (at t = 7 and 13) for β = 0.30 to 0.60, but at β = 0.40 only about 18% of pairs "
                "have met by t = 900. A separate check confirms a ring formula for the pair's generating function against "
                "its mode sum (error ≤ 4.4 × 10⁻¹⁶)."
            ),
        },
        "cn": {
            "teaser": '11 × 11 反射格点上两个带捷径的懒惰游走者：精确计算的首次相遇时间在捷径强度 β = 0.30–0.60 时有两个峰，但 β = 0.40 时到 t = 900 只有约 18% 的游走者对已经相遇。',
            "summary": (
                "11 × 11 反射格点上两个漂移方向相反、相互独立的懒惰游走者，各有一条有向捷径；在时域中精确计算二者的首次相遇时间分布。"
                "捷径强度 β ≤ 0.25 时只有一个峰，β = 0.30 到 0.60 时有两个峰（在 t = 7 和 13），但 β = 0.40 时到 t = 900 只有约 18% 的游走者对已经相遇。"
                "另有一项检验，用模式求和核对了环上二者联合生成函数的公式（误差不超过 4.4 × 10⁻¹⁶）。"
            ),
        },
    },
    "grid2d_rect_bimodality": {
        "en": {
            "teaser": 'Rectangular reflecting lattices: clear double peaks survive only in narrow strips, with no single critical width; with one target and a corridor, only for one global bias and widths 8 to 16.',
            "title": "Grid2D Rectangle Bimodality",
            "summary": (
                "Rectangular lattices 60 sites long and W sites wide, with reflecting walls. With a target at each end and "
                "a biased stream towards each, clear double peaks survive only in narrow strips (W = 5–6 for one start "
                "position) and there is no single critical width. With one target and a walled corridor, clear double "
                "peaks appear only for one global bias (b_x = −0.08) and W = 8–16."
            ),
            "narrative": {
                "model_overview": (
                    "Rectangle of 60 × W sites, reflecting boundary, lazy walk (move with probability 0.8). Study I: two "
                    "targets near the two ends, with one-site-wide biased streams towards each. Study II: one target, start "
                    "and target joined by a corridor with walls and a local bias towards the target, plus a global bias b_x."
                ),
                "method_overview": (
                    "Exact recursion (t up to 20 000 for representative cases, 5000 in scans). Two-peak detection on f "
                    "smoothed over 7 steps; a clear double peak also needs the peaks separated by more than the sum of "
                    "their half-widths."
                ),
                "result_overview": (
                    "Study I: for the start at x = 10, clear double peaks at W = 5 and 6, weak at W = 7, none from W = 8; "
                    "other start positions differ, so there is no single critical width. Study II: clear double peaks only "
                    "at b_x = −0.08 with W = 8–16; corridors 3 to 7 cells wide enlarge that region."
                ),
            },
            "key_findings": [
                "Two targets: with the start at x = 10, clear double peaks at W = 5 and 6, a weak one at W = 7 and none from W = 8.",
                "The width at which the double peak disappears depends on the start position: there is no single critical width.",
                "One target with a walled corridor: clear double peaks only at global bias b_x = −0.08 for W = 8 to 16, weak ones from W = 18.",
                "A corridor one cell wide gives at most a weak double peak; corridors 3, 5 or 7 cells wide enlarge the clear region.",
            ],
        },
        "cn": {
            "teaser": '矩形反射格点：清晰双峰只在窄条中保持，没有统一的临界宽度；单目标加走廊时，只在一个整体偏置值、宽度 8 到 16 时出现。',
            "title": "二维矩形格点双峰",
            "summary": (
                "长 60、宽 W 个格点的矩形格点，四壁反射。两端各有一个目标、各有一条通往目标的偏置流时，清晰双峰只在窄条中保持"
                "（某一起点下 W = 5–6），不存在统一的临界宽度。一个目标加一条有墙走廊时，清晰双峰只在整体偏置 b_x = −0.08、"
                "W = 8–16 时出现。"
            ),
            "narrative": {
                "model_overview": (
                    "60 × W 的矩形，反射边界，懒惰游走（以 0.8 的概率移动）。研究一：两端附近各有一个目标，各有一条一个格点宽的偏置流。"
                    "研究二：一个目标，起点与目标之间有一条带墙、内部有指向目标的局部偏置的走廊，另加整体偏置 b_x。"
                ),
                "method_overview": (
                    "精确递推（代表情形算到 t = 20 000，扫描中算到 5000）。在 7 步平滑后的 f 上找两个峰；清晰双峰还要求两峰间距大于半宽之和。"
                ),
                "result_overview": (
                    "研究一：起点在 x = 10 时，W = 5、6 为清晰双峰，W = 7 为弱双峰，W ≥ 8 无双峰；其他起点不同，因此没有统一的临界宽度。"
                    "研究二：清晰双峰只在 b_x = −0.08、W = 8–16 时出现；3 到 7 格宽的走廊会扩大这一区域。"
                ),
            },
            "key_findings": [
                "双目标：起点在 x = 10 时，W = 5、6 为清晰双峰，W = 7 为弱双峰，W ≥ 8 无双峰。",
                "双峰消失的宽度取决于起点位置，不存在统一的临界宽度。",
                "单目标加带墙走廊：清晰双峰只在整体偏置 b_x = −0.08、W = 8 到 16 时出现，W ≥ 18 为弱双峰。",
                "一格宽的走廊最多给出弱双峰；3、5 或 7 格宽的走廊会扩大清晰双峰的区域。",
            ],
        },
    },
    "grid2d_membrane_near_target": {
        "en": {
            "teaser": "A semi-permeable membrane on a corridor's walls: with equal permeability κ on both walls, two clear peaks persist for κ ≤ 0.0035 and are gone for κ ≥ 0.03; compared with a two-target setting.",
            "summary": (
                "Tests how a semi-permeable membrane on the walls of a corridor (the same permeability κ on both walls, or "
                "different values on the two walls) changes the first-passage time to a single target, and compares this "
                "with a two-target setting without a corridor in which one target sits near the start. With equal "
                "permeability on both walls (W = 16), two clear peaks persist for κ ≤ 0.0035 and are gone for κ ≥ 0.03."
            ),
        },
        "cn": {
            "teaser": '走廊墙上的半透膜：两侧渗透率 κ 相同时，κ ≤ 0.0035 仍有两个清晰的峰，κ ≥ 0.03 时消失；并与一个双目标情形比较。',
            "summary": (
                "检验走廊墙上的半透膜（两侧墙渗透率 κ 相同，或两侧取不同值）如何改变到达单个目标的首达时间，并与一个没有走廊、"
                "其中一个目标靠近起点的双目标情形比较。两侧渗透率相同（W = 16）时，κ ≤ 0.0035 仍有两个清晰的峰，κ ≥ 0.03 时消失。"
            ),
        },
    },
    "grid2d_one_target_valley_peak_budget": {
        "en": {
            "teaser": 'Short report: in a walk with a membrane-walled corridor, late arrivals are late because they spend long stretches outside the corridor, not because they leave it earlier.',
            "title": "Grid2D One Target: Where the Late Arrivals Spend Their Time",
            "summary": (
                "Short report on a single-target walk with a corridor whose walls are a membrane of permeability κ. It "
                "compares walkers arriving in the first peak, the valley and the second peak: late arrivals are late "
                "because they spend long stretches outside the corridor (on average 718 steps in the valley window and "
                "1311 in the second-peak window at κ = 0), not because they leave it earlier."
            ),
        },
        "cn": {
            "teaser": '短报告：在走廊墙为膜的游走中，晚到的游走者之所以晚，是因为在走廊外停留得久，而不是更早离开走廊。',
            "title": "二维单目标：晚到的游走者把时间花在哪里",
            "summary": (
                "一篇短报告，研究走廊墙为渗透率 κ 的膜时的单目标游走。它比较在第一个峰、谷和第二个峰到达的游走者：晚到的游走者"
                "之所以晚，是因为在走廊外停留得久（κ = 0 时，谷时间窗平均 718 步，第二峰时间窗平均 1311 步），而不是更早离开走廊。"
            ),
        },
    },
    "grid2d_two_target_bias_radius": {
        "en": {"title": "Grid2D Two-Target: Bias vs Near-Target Distance"},
        "cn": {"title": "二维双目标：偏置强度与近目标距离"},
    },
    "cross_luca_regime_map": {
        "en": {
            "teaser": 'Benchmark on 160 lattice workloads: sparse exact time-stepping beat defect-reduced Abate–Whitt inversion in every case (median run-time ratio about 1 to 2000).',
            "title": "Cross-Model Solver Benchmark",
            "summary": (
                "Benchmarks two ways of computing the full first-passage-time distribution up to a fixed time horizon on 160 "
                "two-dimensional lattice workloads: sparse exact time-stepping, and Abate–Whitt inversion with a "
                "defect-reduced propagator (a Woodbury update over the defect sites). Sparse time-stepping was faster in "
                "all 160 (median run-time ratio about 1 to 2000); 110 of the defect-method timings are extrapolated from "
                "a sample of points."
            ),
            "narrative": {
                "model_overview": (
                    "160 workloads on two-dimensional lattices (120 with two targets, 40 with reflecting walls; N = 30, 31 "
                    "or 60), each solved for the full first-passage distribution up to the same horizon T = 300, 600 or 1200."
                ),
                "method_overview": (
                    "Method 1: sparse exact time-stepping of the transition matrix. Method 2: generating-function inversion "
                    "(Abate–Whitt) in which the propagator is obtained from the defect-free one by a Woodbury update over "
                    "the defect sites. One warm-up run, then the median of three timed runs; mean first-passage times from "
                    "a linear solve are kept only as a reference."
                ),
                "result_overview": (
                    "Sparse time-stepping was faster on all 160 workloads; the run-time ratio (sparse over defect method) has "
                    "median 0.0005 and is at most 0.26. Workloads with more defect sites favour sparse time-stepping even more. "
                    "Defect-method timings are measured directly for 50 workloads and extrapolated for 110."
                ),
            },
            "key_findings": [
                "Sparse exact time-stepping is faster than the defect-reduced inversion on all 160 workloads at a fixed time horizon.",
                "Median run-time ratio, sparse over defect-reduced, is 0.0005 (about 1 to 2000); the closest case reaches 0.26.",
                "The gap grows with the number of defect sites: the median ratio falls from about 0.07 (up to 20 defect pairs) to 0.0002 or less (over 300).",
                "Only 50 defect-method timings are measured end to end; the other 110 are extrapolated from timing a sample of points.",
            ],
        },
        "cn": {
            "teaser": '160 个格点算例的基准测试：稀疏精确逐步推进在每个算例上都快于缺陷约化的 Abate–Whitt 反演（运行时间比的中位数约为 1 比 2000）。',
            "title": "跨模型求解器基准测试",
            "summary": (
                "在 160 个二维格点算例上，比较两种计算到固定时间上限为止的完整首达时间分布的方法：稀疏矩阵的精确逐步推进，以及"
                "采用缺陷约化传播子（在缺陷格点上做 Woodbury 修正）的 Abate–Whitt 反演。160 个算例中稀疏逐步推进全部更快"
                "（运行时间比的中位数约为 1 比 2000）；缺陷方法有 110 个计时是由部分采样点外推得到的。"
            ),
            "narrative": {
                "model_overview": (
                    "160 个二维格点算例（120 个双目标，40 个反射边界；N = 30、31 或 60），都求到相同时间上限 T = 300、600 或 1200 "
                    "为止的完整首达分布。"
                ),
                "method_overview": (
                    "方法一：对转移矩阵做稀疏的精确逐步推进。方法二：生成函数反演（Abate–Whitt），其中传播子由无缺陷传播子经缺陷格点上的 "
                    "Woodbury 修正得到。先预热一次，再取三次计时的中位数；由线性方程组得到的平均首达时间只作参照。"
                ),
                "result_overview": (
                    "160 个算例中稀疏逐步推进全部更快；运行时间比（稀疏方法除以缺陷方法）的中位数为 0.0005，最大为 0.26。"
                    "缺陷格点越多，稀疏逐步推进的优势越大。缺陷方法有 50 个算例是直接计时，110 个是外推。"
                ),
            },
            "key_findings": [
                "在固定时间上限下，稀疏精确逐步推进在全部 160 个算例上都比缺陷约化反演快。",
                "运行时间比（稀疏除以缺陷约化）的中位数为 0.0005，约为 1 比 2000；最接近的情形为 0.26。",
                "差距随缺陷数增大：中位数从约 0.07（不超过 20 对缺陷）降到 0.0002 以下（超过 300 对）。",
                "缺陷方法只有 50 个算例完整计时，其余 110 个由部分采样点的计时外推。",
            ],
        },
    },
    "final_multitimescale_fpt_encounter": {
        "en": {
            "teaser": 'One test for a visible double peak applied across the ring and lattice reports, with the parameter windows and case counts where it holds.',
            "title": "Synthesis: When a Double Peak Counts",
            "summary": (
                "Brings the first-passage results of the ring and lattice reports under one test for a visible double peak "
                "(each route carries enough probability, the two time scales are well separated and the valley between "
                "them is resolved) and tabulates where it holds, for example 34 of 240 two-target ring cases and 210 of "
                "576 cases of a two-dimensional local-bias basin."
            ),
        },
        "cn": {
            "teaser": '把同一个可见双峰判据用于环与格点各报告，并列出满足判据的参数区间和情形数。',
            "title": "综述：双峰什么时候才算数",
            "summary": (
                "用同一个可见双峰判据（每条路径都有足够的概率、两个时间尺度分得开、二者之间的谷能分辨）汇总环与格点各报告的首达结果，"
                "并列出满足判据的情形，例如 240 个双目标环情形中的 34 个，以及二维局部偏置盆地 576 个情形中的 210 个。"
            ),
        },
    },
}


# Definitions shown in a report page's "Mathematics" section instead of the
# formulas extracted from the manuscript (used when the extraction yields only
# a generic placeholder). Each row: stage title, one-line explanation, LaTeX.
REPORT_DEFINITIONS: dict[str, list[dict[str, str]]] = {
    "ring_lazy_jump_ext": [
        {
            "stage_en": "First-passage time",
            "stage_cn": "首达时间",
            "description_en": "T is the first step at which the walker, started at site 1, stands on the target site 1 + N/2 (site 51 for N = 100); the target absorbs on the first visit.",
            "description_cn": "T 是从格点 1 出发的游走者第一次站在目标格点 1 + N/2（N = 100 时为格点 51）上的步数；目标在第一次到达时即吸收。",
            "latex": r"T=\min\{t\ge 1:\ X_t=n_{\mathrm{target}}\},\qquad X_0=1,\qquad n_{\mathrm{target}}=1+N/2",
        },
        {
            "stage_en": "Step rule",
            "stage_cn": "每一步的规则",
            "description_en": "Away from the shortcut the walker stays put with probability 1 − q or jumps up to K/2 sites either way, each with probability q/K; q = 2/3, K = 2 or 4.",
            "description_cn": "在捷径以外的格点，游走者以 1 − q 的概率停留，或以各 q/K 的概率向任一侧跳至多 K/2 个格点；q = 2/3，K = 2 或 4。",
            "latex": r"P(n\to n)=1-q,\qquad P(n\to n\pm j)=\frac{q}{K}\quad (j=1,\dots,K/2)",
        },
        {
            "stage_en": "Shortcut",
            "stage_cn": "捷径",
            "description_en": "The directed shortcut from site 6 to the site after the target takes a fraction β of the stay-put probability of site 6; nothing else changes.",
            "description_cn": "从格点 6 指向目标下一个格点的有向捷径，取走格点 6 停留概率的 β 倍；其余转移不变。",
            "latex": r"P(6\to n_{\mathrm{target}}+1)=p=\beta\,(1-q),\qquad P(6\to 6)=(1-q)-p",
        },
        {
            "stage_en": "Distribution and survival",
            "stage_cn": "分布与生存概率",
            "description_en": "f(t) is the probability of first arriving at step t; S(t) is the probability of not having arrived by step t.",
            "description_cn": "f(t) 是恰在第 t 步首次到达的概率；S(t) 是到第 t 步仍未到达的概率。",
            "latex": r"f(t)=\Pr[T=t],\qquad S(t)=\Pr[T>t]=1-\sum_{s=1}^{t}f(s)",
        },
        {
            "stage_en": "Peaks and valley",
            "stage_cn": "峰与谷",
            "description_en": "t₁ and t₂ are the two peaks (strict local maxima of f with f ≥ 10⁻⁷ and at least 1% of the highest peak) and t_v is the lowest point between them; a smaller valley ratio means a deeper valley.",
            "description_cn": "t₁、t₂ 是两个峰（f ≥ 10⁻⁷、且不低于最高峰 1% 的严格局部极大值），t_v 是二者之间的最低点；谷比越小，谷越深。",
            "latex": r"t_1<t_v<t_2,\qquad h_i=f(t_i),\qquad \text{valley ratio}=\frac{f(t_v)}{\max(h_1,h_2)}",
        },
        {
            "stage_en": "Tail decay rate",
            "stage_cn": "尾部衰减率",
            "description_en": "λ_max is the largest eigenvalue of the transition matrix restricted to the non-target sites; γ is the rate at which late arrivals die out.",
            "description_cn": "λ_max 是转移矩阵限制在非目标格点上的最大特征值；γ 是晚到概率衰减的速率。",
            "latex": r"S(t)\propto e^{-\gamma t}\quad (t\to\infty),\qquad \gamma=-\ln\lambda_{\max}",
        },
    ],
}
