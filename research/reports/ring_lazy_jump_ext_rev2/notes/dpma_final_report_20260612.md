# 双峰模归因研究(DPMA)— 最终报告

日期:2026-06-12 · 报告:`ring_lazy_jump_ext_rev2` · 状态:v8(2026-06-30 **全 PRR-内容三方审计 + 修正**:Claude fan-out + ChatGPT gpt-5-5-pro PRR-referee + 数值仲裁,经 `triangulated-audit` skill。**两技术阻塞真正清除**——b_c 认证(含 √fold 正规形标度 gap∼δ^½/prom∼δ^{3/2})+ **一般-θ FULL master 曲线落地**(此前 G 仅验 affected 模=过度声称,已补 node 模幅 G_n^node、全曲线 rel-err 1e-5/O(1/N))。PRR-referee 判 **MAJOR REVISION**,缺口=significance/universality(存在性定理+普适性+物理落地+PRR级图),**非 correctness**。roadmap+odds(JPA 55–65%/PRE 60–70%/PRR 50–60%)见 `notes/dpma_prr_audit_20260630.md`;前序 `dpma_chatgpt_pro_audit_20260630.md` + `dpma_adversarial_audit_20260630.md`)· **v9(2026-06-30 roadmap#1 闭合)**:**一般鞍结存在性定理**(判据 S₁=S₂=0、b_c(θ) 边界+端点律 0.789/d+最小 3 交替模定理;gpt-5-5-pro 推导+数值仲裁 rel-diff 1e-6)—— referee 最大理论缺口已闭合。见 `notes/dpma_saddle_node_existence_theorem_20260630.md`
模型:懒惰环 N 格点(停留 1−q,左右各 q/2),吸收目标 v=0,对径捷径源 u=N/2
把 β(1−q) 的自环概率改接到有向边 u→v;起点距 u 偏移 d(C.2 几何),ρ=L−d,L=N/2。

---

## 一、核心结论(TL;DR)

研究问题(导师共识版):**双峰窗口在 (N,β) 平面上的位置能否提前预测?哪些谱项
(modes)主导曲线的各个特征与衰减?**

**四条定律 + 一张归因表回答全部问题:**

**定律 1(通道分配,精确闭式,已证明+机器精度验证)**
经捷径吸收的总概率质量 = **捷径通道分裂概率(splitting probability,全时间最终经捷径
吸收的概率)**——**严格命名(2026-06-30 三审一致)**:这是 Sherman–Morrison 秩一缺陷
预解给出的**分裂概率**,**不是**第一峰/时间局域质量,叙述中务必如此命名,勿混。
  π_sc = ρ/(a+L),a = q/(β(1−q))。
推导:Sherman–Morrison 秩一(缺陷 −λe_u e_uᵀ)更新恒等式
π_sc = λG₀(n0,u)/(1+λG₀(u,u)),G₀ 的 z=1 Chebyshev 值
G₀(n0,u)=ρ/q、G₀(u,u)=L/q。验证:全网格(1632 格点)|偏差| < 2×10⁻¹²;
第二轮审计独立通量记账(明确累加 β(1−q)p_t(u))复核至 ~1×10⁻¹³。

**定律 2(均匀谱移,一阶微扰,50 位精度验证)**
对所有携带振幅的反射对称模:δs_j = −2β(1−q)/N + O(β²);反对称模(γ_r)冻结。
物理:u 是全部对称模的公共反节点,归一化振幅平方恰为 2/N。
等价形式(平行线定律):N²(1−s_k)/q = (2k−1)²π²/2 + 2b,b = β(1−q)N/q。
验证:50 位精度下比值 → 1(N=200、β=1e−5 时偏差 1×10⁻⁴,随 β 线性消失)。

**定律 3(q-约化引理,两行证明)**
特征行列式 D(y)=aT_L(y)+U_{L−1}(y) 不含 q;全部结构只依赖 (N, d, b),
q 仅作为时间单位(1−s = q(1−y),对**谱根精确**)。扫描中删除 q 轴。
注(2026-06-30 审计):时域塌缩 τ=q·t 为**前导阶**(根精确,离散-t 修正 O(1/N)),
非逐 t 精确——措辞勿过强。**q-消去已数值钉死**:固定 (N,d,b) 下行列式根 y_j 在
q=0.5/0.667/0.9 **逐位相同**(ChatGPT gpt-5-5-pro 的 "q-约化被推翻" 实为过度声称,
已驳)。**但** Pro 的"绝对嵌入(u 奇偶)而非仅距离 d"一点成立但极小:固定 (N,d,b)
仅平移 u 一格,标度谱差 ~0.01–0.04%@N=120(O(1/N) 嵌入修正,N→∞ 消失),非 q 问题。

**定律 4(双峰窗口边界律,数值发现;第二轮对抗审计后的修正版)**
clear 双峰窗口(C.2 五条件分类器)的边界呈**两分支结构**(绑定条件切换):

*下边界*(N 充分大于 N_min 时绑定 h₂/h₁ ≤ 10;近 N_min 处先由谷深条件绑定):
  β_lo·N² → A(d),按 1/N 干净收敛(Richardson + 多模型拟合):
  A(3) = 9.087(9)、A(4) = 12.168(20)(即 A(d)/d = 3.029(3)、3.042(5),**真实
  d 依赖**)。早期的 "A(d)≈πd" 鉴定在大 N 外推下被**排除**(π 高出极限 3.3–3.7%,
  为拟合散布的 20–40 倍);**闭式已导出**(§三 b):A(d) = C₂(0)·d/(10(1−q)c_w(d)),
  与已发布 CSV 的 1/N 外推一致到 0.05–0.14%。

*上边界*存在交叉尺度 N*(d)(≈360 @ d=3、≈450 @ d=4;来源:固定 β·N 下
  h₁·N ≈ const、h₂·N² ≈ const ⟹ h₂/h₁ ∝ 1/N,在 N* 处穿过 0.1):
  - N < N*(谷深条件绑定):β_hi·N ≈ 3.146–3.149 平台(N=240 实测 3.1477;
    各外推模型给 3.146–3.149,全部高于 π 至少 0.004,**π 鉴定不成立**——
    此值为有限 N 平台常数,N>N* 后失效);
  - N > N*(h₂/h₁ ≥ 0.1 绑定):窗口上缘塌落,β_hi·N² ≈ 1.0–1.1×10³ 缓慢漂移
    (d=3 实测:β_hi·N = 2.74@400、2.03@520、1.61@640、1.26@800)。
  最小系统 N_min(d) ≈ 14d。

塌缩坐标下(中等 N,N_min ≪ N < N*):A(d)/(2N)·(模型单位) ≲ b ≲ 1.574;
q-不变性实测:上边界 0.023%(可忽略),下边界残余 q 依赖 0.3–0.5%
(q=1/2 vs 2/3,N=240)——约化引理对根精确、对窗口近似。
对照:C.2 发表值(N=100 上边界 0.030–0.032)⇔ 3.15/N = 0.0315 ✓(N=100 < N*)。

**无阈值物理边界(2026-06-12 第四轮审稿后新增,头条级)** —— 上述窗口常数
都挂在分类器阈值上(referee 一致的头号攻击点)。真正内禀、不含任何阈值的上界
是**鞍结分岔 b_c**:第二峰(绕环波极大)在 b 增大时与谷合并湮灭,
**双峰存在 ⟺ b < b_c**。从闭式主函数 Φ(§三 b)算得 **b_c = 3.0764**
(谷 x=0.0378 与峰 x=0.0389 在 b_c 处合并);精确有限-N 链(完全不碰分类器)
在 N=400/800/1200 一致给出第二峰消失于 b∈[3.05, 3.10],把 b_c 夹在正中且
**N-无关**。C.2 "clear" 窗口的上沿 b_pl=1.573 落在 b_c 的 51%——即分类器
窗口是物理存在区间 (0, b_c) 的一个阈值化子区间。
**单位对照(2026-06-30 审计,统一两处此前未连起来的边界)**:digest §3 的物理
**合并边界** β_hi·N≈6.15 与此 b_c 是**同一边界**——b=β(1−q)N/q ⟹ β·N=b·q/(1−q),
q=2/3 时 β·N=2b,故 b_c=3.0764 ⟺ β·N=6.153。即「合并边界 6.15」就是「无阈值
鞍结 b_c」的 β·N 表述,应合并叙述。
**鞍结已认证(2026-06-30,经 ChatGPT gpt-5-5-pro 对抗挑战后强化)**:Pro 曾断言 b_c
**非**鞍结(理由:2 模正幅和 G₁,G₂>0 完全单调、无内极值 ⟹ 只是模主导交叉)。**该前提
被证伪**:模幅 B_j **有正有负**(`code/dpma_saddle_node_certification.py` 实测 N=400 约
100 正/100 负、ΣB_j≈0,因 F(0)=0),带符号指数混合非完全单调、本就允许内极值。独立认证:
b→b_c 时 (谷-极小, 峰-极大) **对合并**——间隔 (τ_max−τ_min) 与突起 (Φ_max−Φ_min) **同时→0**
(b=3.060: 间隔3.2e-3/突起5.0e-4;b=3.0764: 间隔1.4e-4/突起4.4e-8),其后 b≥3.078 该对**湮灭**
⟹ Φ'(τ_c)=Φ''(τ_c)=0(二重根)⟹ **真鞍结(fold),非主导交叉**。这正是三方审计共同要求的
无阈值认证;**PRR 头条成立且被强化**。**正规形标度(2026-06-30 PRR 审计补)**:
gap∼(b_c−b)^0.50、prominence∼(b_c−b)^1.50,双根 b_c=3.076432——标准 √ fold 的灾变签名
(非主导交叉),回应 referee 对「catastrophe 语言未证」的质疑。脚本 `code/dpma_saddle_node_certification.py`。
脚本 `code/dpma_saddle_node.py` → `artifacts/tables/dpma_saddle_node.txt`。
**投稿重构要点**:论文头条应是 Φ(x;b) 与 tan w=−2w/b + 鞍结边界 b_c,
分类器窗口降为下游推论(见 §八)。

**归因表(哪些项最重要 — 最终答案)**

| 特征 | 主导项 | 1% 精度所需模数 k₁% | 备注 |
|---|---|---|---|
| 第一峰(俘获波,t₁≈d²量级) | 多模相干波包 | 跨 d 范围 25–39(N=100,d=5/4/3:25/29–33/39);d=4 时 ≈0.6L(N=200:61–65),随 d 增大而减少 | 按模排名无意义(干涉);π_sc 是**全时间**通道质量,第一峰的**时间局域**质量仅占 π_sc 的 ~0.12–0.28(见诚实备注,勿混) |
| 谷(t_v) | 慢带 | 7–11 | |
| 第二峰(扩散波,t₂~N²) | **mode 1 为主** | **3** | mode 1 占 F(t₂) 的 ≈115%(实测 1.1505),由负幅模修正 |
| 长尾(t→∞) | **mode 1 单项** | 1 | B₁s₁^{t−1},t* = −1/ln s₁(旧争议已闭) |

诚实备注(2026-06-30 审计:量化此前模糊的"measured < π_sc"):π_sc 是**通道**
质量(全时间经捷径吸收),**远**大于**时间局域**的第一峰/谷前质量——实测谷前质量
仅为 π_sc 的 **0.12–0.28(即 3–4 倍差)**(N=100,d=4:β=0.02→π_sc=0.307 vs 谷前
0.070;β=0.03→0.394 vs 0.111),因为捷径通量的 **~72–83% 在谷之后**才被吸收。
故归因表中第一峰**不可**说成"由 π_sc 控制"。π_sc 的正确角色:精确通道守恒律
(π_sc+π_direct=1)+ 完美塌缩坐标;窗口边界的机制解释以绑定条件数据为准。

---

## 二、验证链(全流程)

1. **几何仲裁**:同模型两种双峰——起点贴目标(浅,t·F 上,β=0 最强,封顶 ~5%)
   vs 起点贴捷径源(强,F(t) 本身,两路竞争)。研究对象 = 后者(C.2 几何)。
2. **分类器对齐仓库正典**(research-conventions.md 声明制):三层并行输出——
   vkcore `paper_style_bimodality`(直接 import)、jumpover `macro_bimodal`
   (t₂/t₁≥10)、C.2 五条件(主标签源);词表 double_peak/shoulder/local_bump。
3. **实现交叉核对(自一致复现,非外部金标准验证)**:C.2 仓库分类器表 6/6 行
   精确复现(含 n0=4,5,6 的 None 行;关键实现细节:时间序前两峰、t=1 边界候选)。
   ——注:这是新实现与仓库既有 C.2 分类器的**一致性**核对,不是对外部独立基准的验证。
4. **引擎交叉验证**:对称瞬态块 eigh ↔ Chebyshev 闭式残差 < 5×10⁻¹⁶;质量守恒
   < 10⁻⁹;50 位 mpmath 抽查(根、残差、边界点)。
5. **对抗审计**:第一轮 4-agent 评审(方法论/扮演Luca/可行性/备选路径)已吸收
   (fold 边界、b-塌缩、检测卫生、文献锚点);第二轮(攻击结果)见 §七。

## 三、产物清单(全部确定性,带 manifest)

| 类型 | 路径 |
|---|---|
| 研究方案 | `notes/dpma_research_plan_20260612.md` |
| 核心库 | `code/shortcut_double_peak_mode_attribution.py`(模型/谱/分类器/验证 CLI)|
| 扫描 | `code/dpma_phase_scan.py` → `artifacts/data/dpma_phase_scan_full.csv` (+pilot) |
| 边界精化 | `code/dpma_boundary_refine.py` → `artifacts/data/dpma_boundary_refined.csv` |
| 绑定条件 | `code/dpma_binding_conditions.py` → `artifacts/tables/dpma_binding_conditions.csv` |
| 50位验证 | `code/dpma_law_verification_50dps.py` → `artifacts/tables/dpma_law_verification_50dps.txt` |
| 归因 | `code/dpma_attribution.py` → `artifacts/tables/dpma_attribution.csv` |
| 图 | `code/dpma_figures.py` → `artifacts/figures/dpma_fig{1..4}_*.{png,pdf}` |
| C.2 复现 | `artifacts/outputs/dpma_c2_reproduction.json` |
| 约化模型推导 | `code/dpma_reduced_model.py` → `artifacts/tables/dpma_reduced_model.txt` |
| ρ∝N 族 | `code/dpma_rhoN_family_scan.py` → `artifacts/data/dpma_rhoN_family_scan.csv` (+manifest) |
| q-不变性 | `code/dpma_q_invariance.py` → `artifacts/tables/dpma_q_invariance.csv` |
| 阈值敏感性 | `code/dpma_threshold_sensitivity.py` → `artifacts/tables/dpma_threshold_sensitivity.csv` |
| 非对径捷径 | `code/dpma_general_u.py` → `artifacts/tables/dpma_general_u.txt` |
| **精确主函数** | `code/dpma_master_function.py` → `artifacts/tables/dpma_master_function.txt` |
| **无阈值边界 b_c** | `code/dpma_saddle_node.py` → `artifacts/tables/dpma_saddle_node.txt` |
| Luca 英文短文 | `manuscript/extras/dpma_note_for_luca_20260612.tex` (+ build PDF) |
| **一般-u 主函数(已验证)** | `code/dpma_general_u_master.py` → `artifacts/tables/dpma_general_u_master.txt` |
| ChatGPT 整合digest | `notes/dpma_chatgpt_integration_20260612.md` |
| ChatGPT 原文存档 | `notes/external_inputs/chatgpt_share_6a4273c0_20260612.md` |

图:F1 相图(三个 d 面板,标签场+精化边界+渐近律+β_c 参考线);
F2 谱流(原始 s_k(β)、平行线塌缩、二阶残差);
F3 振幅流与归因(B_j(β)→f_j、k₁% 证书、通道-vs-时间质量、样例曲线);
F4 边界律(β_lo·N²→A(d)、上边界两分支与 N* 切换、b-窗口);
大 N 扩展边界:`artifacts/data/dpma_boundary_refined_largeN.csv`(N=320–640;
**注意**:其上边界有效并独立确认塌落分支,其下边界在 N≥400 被粗网格地板
6.3×10⁻⁵ 左删失,下边界外推请引用审计的细化数值/报告定律 4)。

## 三 b、边界常数的闭式推导(两组分约化模型,2026-06-12 晚)

组分:俘获波 F_cap(t)=λ·W_free(d,t)(自由懒走占据,λ=β(1−q));绕环波
F_arr = Dirichlet 路径模和(吸收环的瞬态块恰是 Dirichlet 路径:本征值
1−q+q·cos(kπ/N)、本征向量 sin(kπj/N);奇 k=α 族、偶 k=γ 族)。

**推导出的常数与公式(全部经数值验证):**

| 量 | 公式 | 预测 vs 测量 |
|---|---|---|
| c_w(d) = d·max_t W_free(d,t) | 离散格点常数,→ e^{−1/2}/√(2π)=0.24197 | c_w(3..6)=0.24432/0.24327/0.24279/0.24254 |
| C₂(0) = lim N²·max F⁰ | = q·M,M=3.700260(x*=0.41117)为反对径首达 theta 级数 2πΣ(−1)^j(2j+1)e^{−(2j+1)²x} 的最大值 | 2.466840(1/N² 外推),**与 d 无关**,= q·M 精确 |
| **A(d) = C₂(0)·d/(10(1−q)c_w(d))** | 下边界(h₂/h₁=10) | 预测 9.087/12.168/15.240;已发布 CSV(N=200,240)的 1/N 外推 = 9.082/12.157/15.219,**一致到 0.05–0.14%**;审计的多模型大 N 外推 9.087(9)/12.168(20) 与预测同位 |
| 塌落渐近 = 100·A(d) | 上下边界同条件、比值 10↔0.1 | 909 vs Richardson 外推 ~917(d=3,N=400–800;N=800 行见 `dpma_boundary_refined_largeN2.csv`) |
| N*(d) = 10·C₂(b_pl)·d/(q·b_pl·c_w(d)) | 绑定切换 | 355/478 vs 审计 ~360/~450 |
| h₁·N = qb·c_w(d)/d | 俘获峰高 | 0.0842 vs 0.0836 |
| 平台 b_pl | **精确主函数闭合(2026-06-12 深夜)**:扩散极限特征方程 **tan w = −2w/b**(每分支一根),μ_j=2w_j²,闭式振幅 G_j=4w_j(1−cos w_j)/(sin w_j[1+b(b+2)/(4w_j²)]),Φ(x;b)=qΣG_je^{−μ_jx};谷方程(内部谷局部极小 vs 末个局部极大)Φ(x_v)=0.8·Φ(x_p₂) 给 **b_pl=1.57332**(**精确程度声明**:根方程 tan w=−2w/b 与 μ_j=2w_j² 精确;振幅 G_j 为 1/N 前导阶,N=800 时 Φ 整体偏 ~0.55%,故 Φ 不应整体标记为 exact) | **vs 实测 1.5738@N=240 / 1/N 外推 ~1.573:误差 0.03%,缺口闭合**;逐模验证 μ 到 1e−6、G 到 O(bd/N);b→0 回收平行线定律与 M=3.700260(早期前导阶 1.375 是冻结振幅近似,已被取代) |

脚本:`code/dpma_reduced_model.py` → `artifacts/tables/dpma_reduced_model.txt`。

## 三 c、ρ∝N 族(固定 x=d/N)

约化模型预测 h₂/h₁ = C₂·x/(qb·c_w) 与 N 无关 ⟹ b-窗口 N-不变;第二/第一峰
时标比 0.0833/x²(b→0;平台处收缩为 0.0609/x²)⟹ x≳0.1 时双峰消失。
扫描验证(脚本 `code/dpma_rhoN_family_scan.py` → `dpma_rhoN_family_scan.csv`):
**x=0.05 的 clear b-窗口 [0.083, 1.417] 在 N=60..240 间逐网格点不变**;
x=0.1、0.2 全程无 clear 双峰。结论:固定 d(边界层)与固定 x 是两个不同的
标度族,前者窗口随 N 移动(β∈[A/N², …]),后者在 b 坐标完全冻结。

## 三 d、非对径捷径 u ≠ N/2(后续论文的种子)

两条推广定律(`code/dpma_general_u.py`):

- **模选择性谱移**:δs_k = −β(1−q)·(2/N)·sin²(kπu/N) + O(β²)。
  u=N/4 验证:sin² 模式 (0.5, 1, 0.5, 0, 0.5, 1),sin²=0 的模**精确冻结**;
  对径情形退化为均匀移/冻结二分。
- **通用俘获律**:π_sc = λG₀(j0,u)/(1+λG₀(u,u)),G₀(i,j)=(2/q)·min(i,j)(N−max(i,j))/N
  (Dirichlet 路径 Green 函数)。4 组配置验证至 10⁻¹⁵;对径退化为 ρ/(a+L)。
### 三 d-2、一般-u 主函数(2026-06-12 晚,源自 ChatGPT Pro 对话并经本仓库独立验证)

把对径 master function 推广到任意 shortcut 位置 u(= 冲 PRR 的核心杠杆)。谱行列式 **D_u(y)=a·U_{N−1}(y)+2·U_{u−1}(y)·U_{N−u−1}(y)**;分段分子 N_{r,u};时域 F^(u)_r(t)=Σ_j B^(u)_rj s_j^{t−1};channel-mass **π_sc^(u)(r)=2min(r,u)[N−max]/(aN+2u(N−u))**;谱移 δs_k=−2β(1−q)/N·sin²(kπu/N)。连续极限 = [0,1] 上带 **interior δ-sink @ x=θ=u/N** 的扩散,master 谱方程 **M_θ(w;b)=w sin2w + b sin2θw·sin2(1−θ)w=0**,θ=1/2 回收 tan w=−2w/b。**验证**(`code/dpma_general_u_master.py` + 第三轮 6-agent 对抗审计):有限-N 主函数(D_u/分子/残差,12 组硬配置含 r>u、N 奇、u 贴边界、β≤0.5、node-frozen)对精确矩阵 ≤5e-18;**连续振幅 G_{ξ,θ} 已验证并提交(2026-06-30)**:闭式 G_{ξ,θ}(w;b)=2w²·φ_{w,θ}(ξ)·I_{w,θ}/J_{w,θ}(源自 ChatGPT gpt-5.5-thinking,经 gpt-5-5-pro 对抗交叉——pro 给的另一形被**数值否决**——并由本仓库**独立数值验证**:对精确有限-N 残差 A_j=(N²/q)B_j 之比 → 1.0000,**max|A/G−1|=2.1e-4@N=1200,O(1/N²)**,θ=1/2 与 1/3、affected 模)。**node 模幅已补全(2026-06-30 PRR 审计后)**:G_n^node=nπ[1−(−1)ⁿ]sin(nπξ)(非微扰 Dirichlet 残差;偶 n 消失);**FULL master 曲线已验证**——affected+node 合并重构精确 (N²/q)F,rel-err ~1e-5@N=1200、O(1/N),τ∈[0.01,0.2],θ=1/3、2/5、1/2(affected-only 在早期 τ 偏 83%,补 node 后消除)。脚本 `code/dpma_general_u_master_amplitudes.py`(振幅)+ `code/dpma_general_u_master_curve.py`(全曲线)。**重要修正**:平台 master 用的对径 G(无 ξ)是**中心起点 ξ=1/2 的特例**,一般起点带 sin(2wξ) 因子(G_{ξ,1/2}=4w(1−cosw)sin(2wξ)/(sin²w[1+b(b+2)/(4w²)]),ξ=1/2 回收旧式);**一般-θ 连续谱**(θ=1/3、2/5)N²(1−s_j)/q→2w_j² 到 O(1/N²);channel 左右拆分 π_L/π_R+守恒=1 到 1e-62;no-Jordan/无 secular 项已证(两步:删 v 后为对称 Jacobi 矩阵、+q/2 正离对角 ⟹ 谱单 ⟹ 残差良定、无 t·λᵗ)。完整逐项核对见 `notes/dpma_chatgpt_integration_20260612.md`;2026-06-30 PRR 三方审计见 `notes/dpma_prr_audit_20260630.md`。

**scaling-regime 修正(应采纳)**:Regime A 宏观 |ξ−θ|=O(1) → 全曲线 = Φ_{ξ,θ}(τ;b);Regime B source-layer d=O(1)(我们的 C.2)→ 需 matched asymptotics。**第三轮审计细化(诚信修正)**:β_hi·N 平台的 O(N⁻²) 回退是**分类器(height-ratio [0.1,10])伪象**,不是物理:物理**合并边界**(两峰真正并合)是稳的 O(1/N),β_hi·N≈6.15(N=100–1600);3.1475 特指 prominence-augmented C.2 边。手稿须明写「分类器边 vs 合并边」之分。

**θ-collapse 负结果(第三轮推翻)**:固定非对径 θ(1/3、1/4)+ 宏观起点 ξ=0.7 下**无双峰**(0/60,单扩散峰),故不能作为 PRR collapse 图;双峰存在于近对径/竞争分支几何。替代 collapse 候选 = §三c 的 ρ∝N 族(x=0.05 窗口 b-不变)或近对径几何。

- **三峰否定(稳健负结果)**:12 组三时标配置(u ∈ {N/4, N/8, N/12, N/16},
  三时标比 d²:u²:(N−u)² 至 ~1:400:19600,实测峰时比至 1:184;全部归档于
  `dpma_general_u.txt`)峰数全部封顶于 2。机制:t~N² 时 QSD 已形成,长弧到达波的路径
  身份被扩散混合抹除——晚期峰是弛豫特征(单慢模驼峰),不是到达特征;
  路线多样性不会增殖峰数。

## 四、与文献的关系

双峰首达现象学背景。**⚠️ 2026-06-30 审计修正(prior-art 错误,blocker 级)**:
- Mattos–Mejía-Monasterio–Metzler–Oshanin PRE 86, 031143 (2012) 是**分裂概率/
  到达比 P(ω) 的双峰**,**不是**首达密度 f(t) 的双峰——此前措辞把它当作 f(t)
  结果,错,须改。
- Godec–Metzler PRX 6, 041037 (2016)。
- **必须补引(此前漏引,且是导师本人工作)**:**Giuggioli, PRX 10, 021045
  (2020)**——格点 Green 函数/缺陷-预解(defect-resolvent)方法,与本框架**直接
  同源**;以及 Montroll–Weiss 缺陷技术。漏引导师 PRX 是审稿致命点。
- 内部 δ-sink / 部分吸收 FPT 的最近 prior-art(Grebenkov / Bressloff / Lawley)
  **待查**;b_c 鞍结是否被前人预期 **待查**。

本研究**可辩护的新颖性**(范围收紧,不再声称"文献中均无对应"):有向捷径单缺陷的
**精确有限 N** Montroll 行列式 D_u=aU_{N−1}+2U_{u−1}U_{N−u−1}、闭式通道律 π_sc、
均匀谱移/平行线定律、以及**无阈值鞍结边界 b_c**——相对 Giuggioli 缺陷-预解纲领
与教科书 δ-sink 谱的**净增量**待 ChatGPT prior-art 裁定量化(audit deliverable B)。
注:边界塌缩律 A(d) 依赖 C.2 分类器阈值,**不是**普适物理律,不应列为文献空白。

## 五、局限与下一步

- ~~A(d) 闭式~~ **已导出并精确命中**;~~塌落分支渐近~~ **已导出并一致**;
  ~~平台常数~~ **已精确闭合**(§三 b:主函数 Φ(x;b),b_pl=1.57332,误差
  0.03%)。**2026-06-30 审计 honesty 修正**:解析常数 M、c_w 无自由拟合参数,但
  A(d)/b_pl/N* 另**内嵌 C.2 分类器阈值**(因子 10、谷比 0.8)作为约定常数——故
  "零自由参数"仅适用于解析部分,这些**边界律本身并非阈值无关的物理普适常数**(头条
  应改用无阈值 b_c,详见 §八)。仍开放:M=3.700260、c_w(d) 与
  b_pl 是否有初等闭式(目前为显式超越方程/级数的解)。
- ~~ρ ∝ N 族未扫~~ **已扫并理论解释**(§三 c:x=0.05 窗口 N-不变,x≥0.1 消失)。
- ~~非对径捷径~~ **两条推广定律已验证 + 三峰否定**(§三 d);其完整 (N,β,u)
  窗口扫描与后续论文写作仍开放。
- q 已证为时间单位,但分类器作用在离散 t 上,极小 q 的离散化效应未测。
- ~~阈值敏感性~~ **已跑**(`dpma_threshold_sensitivity.py`:9 个单因子变体的双边二分;边界随阈值平滑移动,如 valley=0.9 → β_hi·N=4.12,无悬崖)。
- M、c_w(d)、b_pl 的初等闭式(见上;均已有显式特征方程/级数定义)。

## 八、投稿就绪度(第四轮:模拟 PRE/PRR 审稿组,2026-06-12)

三个对抗 referee(first-passage 专家 / rigor-scope / 同情但严格的精确格点派)
+ editor 一致:**数学可发表,但手稿现状未达 PRE 投稿就绪**。

- **校准接受概率**:现状投 PRE ~10–15%(头条被判"预测自己分类器的标签",
  大概率 major-revision 边缘 reject-resubmit);现状投 **J. Phys. A ~55–65%**;
  **做完下列重构再投 PRE ~70–80%**。落差全在 framing,不在 correctness。
- **一致致命点(3/3)**:(1) 窗口边界律是分类器输出而非物理(A(d) 因子 10、
  b_pl 的 0.8 都是人为阈值);(2) 最强结果 Φ/tan w=−2w/b 被埋成"钉常数";
  (3) 相对 Mattos 2012 / Godec–Metzler 2016 的新颖性只断言未量化。
- **已交付 #1 修复**:无阈值鞍结边界 b_c=3.0764,精确链 N-无关验证;头条从
  "我们的标签边界"转为"第二峰存在的物理分岔,分类器窗口是其阈值化子区间"。
- **剩余重构(写作+定位,非新研究)**:① 头条改 Φ;② b_c(已做);③ 修 Φ
  exact 措辞(已做);④ 物理动机节(传送/重置/网络捷径)+ 去信件体;⑤ 非对径
  通用律提正文、对径作特例;⑥ 一段量化 known-vs-new;⑦ 分类器定义+敏感性表
  进正文;⑧ 100·A(d) 分支误差预算 / 从 Φ 推 N*。
- **路径**:重构后 PRE 为主,PRR 需 Φ 立头条;想快可先投 J. Phys. A。建议把
  此判断连同短文交 Luca 定 venue 与物理 framing。

**第五轮:三方对抗审计校准(2026-06-30 — Claude 多-agent + ChatGPT gpt-5.5-thinking +
gpt-5-5-pro,经 ai-bridge 浏览器自动化驱动)**:
- **两个技术阻塞已清除**:(1) **b_c 已认证为真鞍结**(fold,gap+突起同时→0;
  `dpma_saddle_node_certification.py`)——这是 PRR 头条所缺的"无阈值认证",现已补齐;
  (2) **一般-θ 连续振幅 G_{ξ,θ} 已闭式+验证+提交**(`dpma_general_u_master_amplitudes.py`,
  max|A/G−1|=2.1e-4)——PRR 核心杠杆落地。
- **三方一致的剩余缺口 = framing/prior-art(非新研究,但 pro 强调部分是 content 非纯措辞)**:
  ① 头条改 Φ/δ-sink/b_c 鞍结,A(d)/b_pl/N* 全降为 C.2 分类器推论(三方一致判其为分类器伪象);
  ② 删头条里一切分类器定义量,改用无阈值量(critical-point 数 / hazard 曲率 / Δ=t₂−t₁);
  ③ prior-art 必须诚实:**补引导师 Giuggioli PRX 2020(方法锚点)**、Montroll-Weiss,纠正
  Mattos 2012=P(ω);净新颖性收紧为"有向内部捷径在不可逆懒走中诱导的多峰时域分解 + 认证鞍结";
  ④ π_sc 一律称"分裂概率",勿当第一峰质量。
- **校准接受率(三方折中)**:J.Phys.A **今天即可投** 55–70%(精确缺陷-预解谱研究);
  PRE 重构后 **60–70%**(pro:新颖性缺口是 content,可能 fail,故非 70–80%);
  PRR:两个技术阻塞已清(b_c 认证 + G 闭式),**剩纯 framing+prior-art**——做完 ①②③ 后
  约 **35–55%**(头条 = 认证的无阈值鞍结 + δ-sink 物理 + 精确有限-N 缺陷理论)。
- pro 一句话:"数学骨架与缺陷-预解理论一致,但手稿当前过度声称尚未被数学认证的物理相变"——
  其点名的"未认证"恰是 b_c,现已认证,故该批评已被实质回应。

**第六轮:全 PRR-内容三方审计(2026-06-30,经可复用 `triangulated-audit` skill)** — Claude
fan-out(6 cluster)+ ChatGPT gpt-5-5-pro PRR-referee + 数值仲裁。详见 `notes/dpma_prr_audit_20260630.md`。
- **catch + fix(诚信)**:Claude 抓到此前「G_{ξ,θ} 已验证+提交、PRR 杠杆落地」**过度声称**——
  提交脚本只验 affected 模、跳过 node 模(θ=1/3 占 ~33% 权重,affected-only 早期 τ 偏 83%)。
  **已补 node 模幅并验证 FULL master 曲线**(rel-err ~1e-5、O(1/N);`dpma_general_u_master_curve.py`)。
  故「两技术阻塞已清」现**才真正成立**(b_c + 全 G 曲线均落地)。
- **gpt-5-5-pro PRR-referee 判 MAJOR REVISION**(borderline PRR / 有降 JPA 风险):数学不再是问题,
  **缺口=significance/universality**。冲 PRR 的真实待办(roadmap):① **一般鞍结存在性定理——✅ 已完成(2026-06-30)**:
  判据 **S₁=S₂=0**(带符号谱矩 S_m=Σ G_j μ_j^m e^{−μ_j τ},Φ'=−S₁、Φ''=S₂;nondeg S₃≠0/∂_b S₁≠0),
  双峰存在 ⟺ 0<b<b_c(θ);显式 b_c(θ) 边界(对称,min@θ≈0.381)、端点律 **b_c∼0.789/min(θ,1−θ)**、
  近对径 b_c=3.0764−133.1ε²、**最小模定理**(≥3 交替号模,2 模不可能)。gpt-5-5-pro 推导 + 本仓库
  数值仲裁(b_c(θ) 逐点 rel-diff ~1e-6)。见 `notes/dpma_saddle_node_existence_theorem_20260630.md`
  + `code/dpma_saddle_node_bc_theta.py`——**referee 最大理论缺口已闭合**;② **普适性/鲁棒性**(2D / 多 shortcut / 随机系综之一 + b_c 对 (β,q,θ) 扰动稳健);
  ③ **物理落地**(reset/search、小世界传输、生化主动捷径之一 + 非厄米算子 Q+|u⟩λ⟨u| 表述);
  ④ **PRR 级图**(b-N 相图、峰谷湮灭标度塌缩、谱 vs 时域对比、鲁棒性);⑤ framing/prior-art。
- **重校接受率(两脑折中)**:JPA 今 55–65%、PRE 重构后 60–70%、**PRR ~50–60%**(两技术阻塞已清,
  缺口转为 significance/universality,非 correctness)。建议:先投 JPA;推存在性定理 + 一条普适性
  结果再认真冲 PRR;此 roadmap 交 Luca 定 venue。

## 六、复现指南

```bash
PY="$(pwd)/.venv/bin/python3"   # set at repo root: numpy + mpmath
cd research/reports/ring_lazy_jump_ext_rev2/code
$PY shortcut_double_peak_mode_attribution.py validate   # C.2 金标准 + 基础不变量
$PY dpma_phase_scan.py --out ../artifacts/data/dpma_phase_scan_full.csv
$PY dpma_boundary_refine.py
$PY dpma_binding_conditions.py
$PY dpma_law_verification_50dps.py
$PY dpma_attribution.py
$PY dpma_reduced_model.py
$PY dpma_master_function.py
$PY dpma_general_u.py
$PY dpma_rhoN_family_scan.py
$PY dpma_q_invariance.py
$PY dpma_threshold_sensitivity.py
$PY dpma_boundary_refine.py --ns 320 400 520 640 --ds 3 4 --suffix _largeN
$PY dpma_boundary_refine.py --ns 800 --ds 3 --suffix _largeN2
$PY dpma_figures.py
```
(venv 需 numpy + mpmath + matplotlib;每步产物路径以 `__file__` 锚定,与 cwd 无关。)

## 七、审计轨迹

- 2026-06-12 第一轮(方向):4 agents(方法论批评/扮演 Luca/数值可行性/备选
  路径)。采纳:fold/persistence 语言、b-塌缩坐标、检测卫生、q-约化、文献
  锚点、两组分分解;几何仲裁以一手证据(C.2 复现)裁决。
- 2026-06-12 第二轮(结果):3 agents。
  (a) 独立复算(从零重写实现,三引擎交叉验证):5/5 项全复现——C.2 锚点
  时刻精确、高度 9 位一致、π_sc 至 1e−13、归因 k=31/9/3 精确、边界翻转条件
  逐一吻合。
  (b) π-猜想攻击:**成功推翻** β_hi·N→π 与 A(d)→πd(见定律 4 修正版);
  发现上边界绑定条件切换 N*(d) 与大 N 塌落分支;q-不变性量化(上边界
  0.023%、下边界 0.3–0.5%)。N=320–640 扩展扫描已纳入产物
  (`dpma_boundary_refined_largeN.csv`)。
  (c) 报告审稿:修正全网格 π_sc 偏差界(2e−12)、绑定条件近 N_min 例外
  (30 行中 6 行下边界由谷深绑定)、归因 d 限定、复现路径、图参数载荷。
  方法论教训(已写入流程):**命名任何常数前必须先做收敛加速外推
  (Richardson/多模型 1/N 拟合),要求常数落入外推置信区间**。
- 2026-06-12 第三轮(全量终审):3 agents。
  (a) 独立复算:六组新结果(c_w、C₂/theta、A(d)、通用 u 双定律、x-族、三峰
  否定)**零推翻**,四项呈现级修正(M 取整 3.700260、C₂ 用 1/N² 外推
  = q·M 精确、A(d) 测量端来源、d=4 行复制粘贴)——全部已落实。
  (b) 文档审稿:三峰 12 组配置当时盘上只有 6 组(探针未归档)——**已补齐
  归档并修订措辞**;0.0609 vs 0.0833 峰时比常数歧义已解决(两者各属其 b);
  N=800 行补档;复现指南补全;q-不变性与阈值敏感性升格为脚本化产物。
  (c) 目标完备性:任务 1 的平台常数高阶闭合正式划界为开放项(存在性+前导阶
  已证;1.3746 vs 1.5738);其余四任务判定完成。
  审计后已重跑 `reportctl.py summary` 刷新仓库摘要。
- 2026-06-12 深夜补遗(平台闭合):推导扩散极限主函数(根方程
  tan w=−2w/b + 闭式 G_j),b_pl=1.57332 vs 实测外推 ~1.573(0.03%),
  四项内部验证(逐模 N=800、曲线级、b→0 极限、N* 复中)+ **独立 agent
  从零复推:两式逐字确认(代数精确;μ 收敛 O(1/N²)、G 收敛 O(1/N) 且常数
  与 d·b 预期一致),b_pl 独立解 = 1.5733154;附赠:一阶修正 +2b 对所有 j
  一致、b→∞ 退化为半环 Dirichlet 谱(完美陷阱)。**
- 2026-06-30 第五轮(双审计):**(a) Claude 多-agent 对抗审计**(6 cluster 围攻
  → 每条发现独立对抗复核 → 综合裁判;workflow `wf_f9fb1a8b-f2c`,opus/high)——
  33 发现、31 过复核;**数学核心零推翻**(Laws 1/2/3、b_c 鞍结、一般-u 行列式、
  通道律全部经独立重推+数值复核),阻碍全在 framing/honesty/prior-art。完整记录
  `notes/dpma_adversarial_audit_20260630.md`。**(b) ChatGPT Pro 审计**经 ai-bridge
  MCP 发包(`.ai-bridge/pro-context.md` + `AUDIT_REQUEST.md`,11 claim + 两交付物:
  G_{ξ,θ} 闭式、prior-art 裁定)——**待并入**。**已应用的安全修正**(本轮):G_{ξ,θ}
  "VERIFIED"→未提交诚实降级、π_sc 通道-vs-时间质量量化(3–4×)、prior-art 修正
  (补引导师 Giuggioli PRX 2020、纠正 Mattos 2012=P(ω) 非 f(t))、"金标准"→实现
  交叉核对、b_c⟺β_hi·N=6.15 单位统一、"零自由参数"加分类器阈值 caveat、τ=qt 前导阶
  gloss、no-Jordan 两步逻辑。**待并入(consolidated pass)**:头条重构(b_c 立头条、
  A(d)/b_pl/N* 降为分类器推论)、§八 可发表度重校(本轮 Claude 审计给:PRE 现状
  10–15%、JPA 55–65%、PRE 重构后 60–70%、PRR 30–40%→50–60%)、committed G 验证脚本、
  代码大-N 溢出守卫。
  **完成(2026-06-30 consolidated)**:ChatGPT 审计经 ai-bridge 浏览器自动化跑完
  **gpt-5-5-pro**(Extended Pro,模型 slug 实证)+ gpt-5.5-thinking 交叉(自动选模、注入、
  发送、抓取全自主)。产出:① G_{ξ,θ} 闭式数值裁定(thinking 形**对**、pro 形**错**)并提交
  `dpma_general_u_master_amplitudes.py`(max|A/G−1|=2.1e-4);② **b_c 认证为真鞍结**
  `dpma_saddle_node_certification.py`(pro 的"非鞍结"基于正幅假设、被符号幅 ~100±/100∓ 证伪;
  fold:gap+突起同时→0);③ q-约化数值钉死(根逐位 q-不变,pro"REFUTED"过度声称);④ §八
  三方校准、channel-mass 改称分裂概率。整合记录 `notes/dpma_chatgpt_pro_audit_20260630.md`。
