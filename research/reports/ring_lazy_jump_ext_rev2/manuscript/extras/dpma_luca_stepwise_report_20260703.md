# 给 Luca 的阶梯式汇报方案(数值 → 理论,2026-07-03)

**一句话回答你的问题**:上次会议定的三图程序(N–β 窗口 → 根 s_k(β) → 振幅 ρ_i(β) →
which term contributes most of the tail)**已经完整做完**,而且成稿把它推进到了定理层。
汇报材料 = 一张四面板图 `artifacts/figures/dpma_luca_pack.pdf`(坐标轴完全按会议约定),
按下面 6 步走,每步一张面板、一句英文结论、一个过渡问题。**不要一上来给他看成稿。**

---

## Step 0(30 秒)— 复述共识,建立"这就是我们说好的"
> "Last time we agreed on a three-plot programme: where the double peak lives in the
> (N, β) plane; how the roots s_k move with β; and, analytically, how the amplitudes ρ_i
> move — to find out **which term contributes most of the tail and drives the double peak**.
> I did exactly that. Here are the three plots, plus the answer."

## Step 1 — 面板 (1):双峰住在哪里(纯数值,他要的第一张图)
**看到什么**:log–log 的 (N, β) 平面,蓝点 = C.2 双峰,灰点 = 单峰;双峰区是一个被两条
虚线精确夹住的楔形。
**结论句**:
> "Above a finite-size onset N_min ≈ 14d (≈56 here), the double-peak region is a sharp wedge.
> The lower boundary is β·N² = A(d) — A(4)=12.17, measured to ~0.2% — and the upper boundary,
> over this scan (N ≤ 240 < N\*≈450), is the plateau β·N ≈ 3.148. Beyond the crossover N\* the
> edge collapses: β·N² ≈ 1.4×10³ measured at N=520–640 for d=4, drifting toward the closed-form
> asymptote 100·A(4) ≈ 1.22×10³. So the natural control variable is b ∝ β·N, not β alone."

(注意:**别引用 1.0–1.1×10³——那是 d=3 的数**;d=4 实测 1.43–1.48×10³,渐近 1.22×10³。)
**过渡问题**:"So what actually changes inside this window — the roots, or the amplitudes?"

## Step 2 — 面板 (2):根的运动是平凡的(数值点 → 一条解析直线)
**看到什么**:六个最慢根的移动 s_k(β)−s_k(0):奇 k 的点全部塌在一条虚线
δs = −2β(1−q)/N 上;偶 k 钉在零。
**结论句**:
> "The roots do essentially nothing. Odd-k modes shift **uniformly** — all by the same
> −2β(1−q)/N, because the source u=N/2 is a common antinode — and even-k modes are frozen
> (u is their node). We checked this in 50-digit arithmetic: the ratio to the first-order law
> goes to 1 as β→0 (the residual is O(β), about 10⁻⁴ at β=10⁻⁵), and the visible departure at
> the window edge is exactly the second-order term. The panel shows two lattice sizes collapsing
> onto the same law in the variable N·δs."

(措辞纪律:**不要说 "verified to 50 decimal places"**——50 位是运算精度,定律是一阶的;
这样说还会和你们争论过的真·50 位 sum-rule 检验混淆。)
**过渡问题**:"If the spectrum is this boring, the whole morphology must live in the
amplitudes."

## Step 3 — 面板 (3):振幅承载全部 β 依赖,而且是闭式(他要的"解析"层)
**看到什么**:ρ_j(β) 的闭式曲线(Chebyshev 残数公式)恰好穿过 eigh 数值点
(吻合 10⁻⁸);偶模振幅横在零线上。
**结论句**:
> "The amplitudes carry **all** the β-dependence, and they are in closed form —
> ρ_j = q·N_{r,u}(y_j)/D′_u(y_j), Chebyshev polynomials, nothing else. And a bonus: the
> even modes are not just spectrally frozen, their amplitudes are **exactly zero** — the
> two boundary fluxes cancel in antiphase and the shortcut sits on their node, so half the
> spectrum simply leaves the stage."
**过渡问题**:"So with a few live modes and signed amplitudes — who builds which part of
the curve?"

## Step 4 — 面板 (4):答案(which term contributes most of the tail)
**看到什么**:F(t) 全曲线 vs 部分和(mode 1 / modes 1–3 / modes 1–9),三条竖线标
peak 1 / valley / peak 2。
**结论句(这是他要的答案,分四段说)**:
> - "**The tail is mode 1, full stop** — the slowest root alone is 100% of F(t) deep in
>   the tail."
> - "**The second peak is a three-mode story**: mode 1 alone overshoots it (115%), and
>   mode 3 — with its **negative** amplitude — carves it back. That signed cancellation IS
>   the second peak."
> - "The valley needs ~9 modes (5 live, since the even ones are dark); the first peak is a
>   genuine wave packet — ~31 modes by the 1% criterion, 17 of them live."
> - "So the answer to our question is: the tail has ONE important term; the double-peak
>   *morphology* is controlled by the **three slowest live modes with alternating signs** —
>   and that observation is provable."
**过渡句**:"And 'provable' is where it gets interesting."

## Step 5 — 理论揭示(把数值升级为定理,每条都可指到手稿章节)
> "Since the morphology is a signed few-mode sum, the birth/death of the second peak is a
> **saddle-node fold**: Φ′=Φ″=0, i.e. S₁=S₂=0 in the signed spectral moments
> S_n = Σ G_j μ_j^n e^{−μ_j τ}. From that single criterion everything follows:"
- **可计算相边界** b_c(θ)(min ≈2.165 @ θ≈0.381;对径 b_c(½)=3.076432);
- **(1/2, 3/2) 正规形标度**,前因子解析:0.0248/0.357;
- **最少三模定理**(两模不可能 fold;Laguerre 指数和零点法则同时给出"≥3 项"与
  "交替号"两半——正是面板 (4) 看到的结构);
- **端点律** b_c ≈ 0.789/min(θ,1−θ),常数由显式半直线变换给出;
- 有限格点阈值收敛 b_{c,N} → b_c ∝ N^{−2.08}。
**一个务必主动讲清的细节**(避免 Luca 混淆两个"上边界"):
> "Careful: the C.2 window's upper branch β·N ≈ 3.15 is the **classifier** boundary
> (where the double peak stops being *clearly visible*: h₂/h₁ ≥ 0.1, valley depth, etc.).
> The **fold** boundary — where the second extremum pair ceases to *exist* — is higher:
> b_c(½)=3.076 source-started, i.e. β·N ≈ 6.15 (the C.2 off-gate start shifts it slightly
> upward, ≈6.2). Classifier window ⊂ fold window; two different questions, two different
> constants — and the mapping between them is already derived: the plateau constant follows
> from the valley-visibility criterion Φ(x_v)=0.8·Φ(x_p₂) evaluated in the same master
> function that gives b_c (June report §3b)."

## Step 6 — 收尾(只在他消化完后才提)
> "All of this is already written up as a full-length manuscript with complete appendix
> derivations, extensively audited (multi-agent internal rounds plus three external reviews),
> with a reproducibility package — whenever you want to see it, it's one file."
然后按人工待决项走:作者序 / funding / venue(建议 PRR,PRE 自动兜底)/ 是否公开代码仓库。

---

## 会议约定 ↔ 已有产物对照表

| Luca 约定的图 | 产物 | 定律/结论 |
|---|---|---|
| (N, β) 双峰范围 | pack 面板(1);`dpma_phase_scan_full.csv`(1632 格点) | 起点 N_min≈14d;β_lo N²=A(d),A(4)=12.168;上边界:βN=3.1475 (N<N\*≈450),N>N\* 塌落 βN²≈1.4e3 实测→1.22e3 渐近(d=4;d=3 才是 1.0–1.1e3);`notes/dpma_final_report_20260612.md` §四定律 |
| β vs s_k(扫 N) | pack 面板(2)(N=100 与 200 塌缩) | 均匀谱移 δs=−2β(1−q)/N(奇模)、偶模冻结;50 位算术下比值→1,残差 O(β):`dpma_law_verification_50dps.txt` |
| β vs ρ_i(解析) | pack 面板(3) | 闭式残数(手稿 App. A);偶模振幅恒为零(解耦) |
| which term → tail | pack 面板(4);`dpma_attribution.csv` | 尾=mode 1(100%);第二峰=3 模(mode 1=115%,mode 3 负号回削);谷≈9 模;首峰≈31 模波包 |
| (升级)何时生/灭 | 成稿 Sec. III | S₁=S₂=0 fold;b_c(θ);(½,3/2) 标度;≥3 交替模定理 |

## 对这个研究方向的评估(多轮对抗审视结论)
方向本身**正确且已经执行完毕**——它就是 6 月 12 日 DPMA v1 程序(四定律+模归因),
成稿又把"哪些项重要"从观察升级为定理(fold 判据+最少三模+Laguerre)。不需要另找路径。
若 Luca 问"下一步",按诚实程度排序的候选(对抗审计校准后):
1. **u 依赖的归因/分类表**(谱移一般式 δs_k=−β(1−q)(2/N)sin²(kπu/N) 与一般-θ 边界
   b_c(θ) 都已是定理级;开放的只是把归因表系统展开到 u≠N/2);
2. **(成稿真正的开放问题)2D**:gap+prominence 联合坍缩检验与大-L 重整化标度;
3. **二阶谱移闭式**——但要如实说:这是 App. A 特征方程的机械展开(一次拟合已覆盖
   112% 残差),是练习题不是研究难点;classifier↔fold 的定量映射**不要列为开放**,
   六月报告已经闭合(见上框)。

> 本包与本方案经 19-finding 对抗审计修正(d=4 塌落常数、N_min 起点、50-位表述、
> 活模计数、N-扫描面板、格点数 1632 等)。
