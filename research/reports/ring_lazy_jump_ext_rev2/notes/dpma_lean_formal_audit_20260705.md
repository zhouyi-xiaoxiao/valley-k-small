# DPMA Lean 形式化审计(2026-07-05)

对 `manuscript/dpma_prr_manuscript.tex` 的**全部精确代数内容**做 Lean 4 + mathlib 机器验证,
形成审计包 `code/formal_lean/`。结论:**46 条定理全部 sorry-free 证毕,公理报告全部只依赖
Lean 标准公理(propext / Classical.choice / Quot.sound),陈述忠实性逐模块对抗审计零 blocker,
未发现论文数学错误**(无需更正正文任何公式)。

## 范围三分层(审计包的核心声明)

1. **精确代数层 → Lean 证毕(46 定理,7 模块)**:App A 的 Chebyshev 乘积恒等式、三项递推
   与 Green/Wronskian 列解(eq:Guu 的三对角逆结构)、Montroll 行列式清分母(eq:Du)、分子
   坍缩(eq:Fraw→eq:num)、Sherman–Morrison 构造解(eq:smcol)、π_sc 闭式(eq:pisc,经
   killed walk 的后向方程组逐点验证)及对映点约化 r*/(a+N/2);App B 的 δ-sink 跳跃条件
   ⟺ D_θ=0、连续性/Dirichlet 端点、对映点坍缩 tan w=−2w/b、归一化恒等式 J=sin(k)D_k/4b
   (eq:JD,抽象约束簇版本+三角实例化)、对映点 sin²w/J/G 闭式(数值脚本所用公式);
   Sec III 的 Φ'=−S₁、Φ''=S₂(有限符号指数混合逐项求导)、两模 fold 不可能定理、三模比例
   +交替符号定理;App C 的 normal-form 根/间隙/prominence 前因子(含 4√2/3=2^{5/2}/3,
   即此前手推曾出错、数值纠正过的那一步——现已机器锁死)、半直线变换 eq:fhl 全代数链、
   分支割积分核 eq:phihl 代数(含支撑上分母严格正)。
2. **数值常数层 → 不形式化,维持多路数值交叉验证**:b_c(θ)、τ_c、B*=0.7890262、
   c*=0.1579221、前因子数值 0.0247518/0.357444、N^{-2.08}、β_c^{2D}≈0.68、MC 一致性
   (正文 Table II;振荡谱和的区间算术形式化超出合理范围)。
3. **解析极限层 → 论文本以引用+假设呈现**:范数预解收敛假设 (F)、Bromwich 围道、IFT fold
   持久性、窗口连通性(数值命题)。

## 执行方式

- 工具链:elan + Lean `v4.32.0-rc1` + mathlib `v4.32.0-rc1`(锁定 commit `360da6fa66c1`,
  见 `lake-manifest.json`);构建在 `~/.local-build/valley-k-small/formal_lean/`(od-divert
  惯例,OneDrive 内不放 `.lake/` 构建物;Reservoir TLS 被 SASE 挡,改 GitHub git 依赖)。
- 陈述骨架(定理名、假设、结论、论文公式号锚点)由主 agent 手写钉死;证明由 7 个并行
  prover agent 填充(硬约束:禁改陈述、禁新公理、禁 native_decide;"陈述不可证"须上报
  而非弱化)。中途一次网络断连(ECONNRESET)打断 6 个 agent,journal 缓存续跑恢复。
- 每模块由独立对抗审计 agent 复核**陈述忠实性**(防"证了个弱化版":逐条对照原稿公式、
  空虚性探针、假设强弱、常数核对),并用 venv numpy/mpmath 对 Lean 陈述原文做随机参数
  数值抽查(如 chebyshev_product 在 sin φ~1e-9 处 50 位复验残差 6e-33)。
- 审计员全部判定 faithful=True;minor 备注均为范围性说明(有限和 vs 无穷和的 (F) 边界、
  Lean x/0=0 惯例、辅助恒等式的平凡性),其中唯一实质项——正文断言分支割分母在支撑上
  **严格正**——已补 `cut_denominator_pos` 闭合。
- 公理报告:`lake env lean AxiomsReport.lean` → 46/46 仅 [propext, Classical.choice,
  Quot.sound],快照存 `code/formal_lean/axioms_report_20260705.txt`。

## 论文对应改动

- App F(app:numerics)在 Code-and-data-availability 前新增 \emph{Formal verification.}
  段落(声明精确代数层已 Lean 机器验证、指向审计包;明确数值常数不在形式化范围)。
- `manuscript/extras/reproducibility/README.md` 增 Lean 复验一节(构建命令+验收标准)。
- 未发现需要更正的数学内容;所有此前数值验证过的恒等式(Table II 上半部)如预期通过
  形式化,双重独立(数值 + 形式)成立。

## 复验命令

```bash
cd code/formal_lean   # 先把目录拷/链到本地盘再构建(OneDrive 内勿建 .lake)
lake exe cache get && lake build          # 零错误零 sorry
grep -rn "sorry\|admit\|native_decide" FormalLean/   # 空
lake env lean AxiomsReport.lean           # 46 行,全部仅标准公理
```
