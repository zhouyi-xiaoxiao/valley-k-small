# AGENT_REPORT_2025-12-14

> Note (2025-12-16): the repo was reorganized so each report lives under `reports/<report_name>/` with its own `code/`, `figures/`, `data/`, `tables/`. Paths in this document follow the new structure; see `reports/README.md` for layout. The former `bimodality_flux_report` is now `reports/ring_lazy_flux/` (CN/EN).

## Overview
- **目标**：在固定 `N=100, K=6, n0=1, target=50` 下，仅扫描 shortcut 指向终点 `dst`，观察解析 first-passage `A(t)` 的第二峰如何变化，并用 Monte Carlo 统计「吸收时间落在第二峰窗口内」的轨迹中，shortcut 的穿越比例；同时对比两种起点设置：Case A（论文设定 `src=n0+5=6`）与 Case B（用户设定 `src=n0=1`）。
- **做了什么**：
  - 编写/整理并运行 `reports/ring_valley_dst/code/dst_shortcut_usage_mc.py`，完成解析扫描（AW 反演）+ MC 统计，生成结构化数据与矢量图（PDF），并按参数前缀归档到 `reports/ring_valley_dst/data/` 与 `reports/ring_valley_dst/figures/` 下。
  - 维护一份汇总报告 `reports/ring_valley_dst/ring_valley_dst_cn.tex`，将两种 `src` 的扫描结果、代表性解析曲线、MC 穿越比例与相关性分析统一排版输出；修复报告中“空白页/大块留白占页”的布局问题，保证插图使用 PDF（矢量）而非 PNG。
  - 新增一份“验证双峰性”的确定性扫描：用 \*\*flux/master equation\*\* 直接推进得到整段首达 PMF `f(t)`，并对少数代表点用 AW 反演交叉核对，生成新报告 `reports/ring_lazy_flux/ring_lazy_flux_cn.tex` / `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`。
- **结果**：
  - 生成并更新 `reports/ring_valley_dst/ring_valley_dst_cn.pdf`（当前为 **11 页**），Case A/Case B 内容均保留，主要图均以 `.pdf` 形式插入。
  - 结论（以 report 中定义的“第二峰窗口条件下穿越比例”为准）：在 **late-second-peak** 族（`t2` 较晚）里，第二峰越高，窗口内 shortcut 使用比例通常越高；等价地，第二峰越低时 “0 crossing” 越多。Case B 还会出现 **early-`t2`**（`t2 <= 2K`）的特殊点：当 `dst` 接近 `target` 时存在极短吸收路径，窗口内几乎必经 shortcut，需要与 late-second-peak 分开解读。
  - 生成并更新 `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`（当前为 **9 页**），给出 `dst` 扫描结果、两套双峰判据（Fig.3 规则 + time-separation robust 规则）以及 AW-vs-flux 的误差核对（最大误差量级约 `1e-13`）。

## Actions（按时间顺序）
1. **定位工程与产物**
   - 进入并检查目录结构：`valley-k-small/`，确认核心脚本、数据输出与 LaTeX 报告位置。
2. **运行解析扫描 + MC（两种 src）并落盘归档**
   - Case A（论文设定）：运行 `python3 reports/ring_valley_dst/code/dst_shortcut_usage_mc.py --sc-src 6 --mc-all-bimodal --seed 0`，输出归档到：
     - `reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_6/`
     - `reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_6/`
     - latest run 信息记录在 `reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_6/latest/results.json`（`run.id=20251214_182308`）。
   - Case B（用户设定）：运行 `python3 reports/ring_valley_dst/code/dst_shortcut_usage_mc.py --sc-src 1 --mc-all-bimodal --seed 0`，输出归档到：
     - `reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_1/`
     - `reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_1/`
     - latest run 信息记录在 `reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_1/latest/results.json`（`run.id=20251214_182542`）。
   - 目的：用固定 seed 保证 MC 可复现；并将每次运行的扫描数据、MC 数据、图与 LaTeX 可直接 `\\input` 的表格/摘要统一结构化保存。
3. **整理并修复 LaTeX 报告布局（避免空白页、图表插入更稳定）**
   - 编辑 `reports/ring_valley_dst/ring_valley_dst_cn.tex`：
     - 引入 `enumitem` 并全局收紧列表与 float 间距，减少“图/标题导致分页后空白占页”。
     - 移除若干强制 `\\newpage`，改用 `\\FloatBarrier` 控制浮动体但不强行换页。
     - 汇总表缩小字号与表格间距（`\\scriptsize`、`\\tabcolsep`、`\\arraystretch`），为结论页留出空间。
     - 将“如何复现”合并进结论末尾，避免单独占页。
4. **编译与校验报告输出**
   - 编译：`cd reports/ring_valley_dst && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_valley_dst_cn.tex`
   - 用 Ghostscript 生成逐页预览图进行目检（仅用于 review，不作为报告插图来源）：`gs -sDEVICE=pngalpha ... reports/ring_valley_dst/ring_valley_dst_cn.pdf`
5. **实现并运行“确定性双峰验证”扫描（flux/master equation）**
   - 新增脚本 `reports/ring_valley_dst/code/bimodality_flux_scan.py`：对每个 `dst` 构建 `K`-neighbour ring + 有向 shortcut `src->dst`，用 master equation（flux）推进计算 `f(t)=P(T=t)`（不建 `N×N` 矩阵），并输出 `scan.csv/results.json` 与矢量图（PDF）。
   - Case A：运行 `python3 reports/ring_valley_dst/code/bimodality_flux_scan.py --sc-src 6 --aw-check`（同时生成 AW-vs-flux 叠加图作为交叉核对）。
   - Case B：运行 `python3 reports/ring_valley_dst/code/bimodality_flux_scan.py --sc-src 1 --aw-check`。
6. **生成“验证双峰性”新报告**
   - 新增并编译 `reports/ring_lazy_flux/ring_lazy_flux_cn.tex`：
     - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`

## Files changed（按文件分组）
### `reports/ring_valley_dst/code/dst_shortcut_usage_mc.py`
- 增强为可复现、可归档的一体化流水线：
  - 参数化输出目录：以 `N/K/n0/target/src` 组成前缀，并按 `runs/<run_id>/` 归档；同时复制到 `latest/` 供报告稳定引用（见 `FIG_ROOT/DATA_ROOT` 以及 `latest` 复制逻辑）。
  - MC 可复现：新增 `--seed`（默认 `0`），并用 `SeedSequence(seed)` 为分 batch 的采样派生子 seed，保证同参数同 seed 重跑一致。
  - 产物结构化：输出 `scan.csv`、`mc.csv`、`results.json`，并生成 `analysis_summary.tex`、`scope_summary.tex`、`selected_table.tex` 供 LaTeX `\\input`。
  - 画图全部输出为 PDF（矢量），包括 `peak2_vs_dst.pdf`、`peak_times_vs_dst.pdf`、`exact_selected_cases.pdf`、`second_peak_crossing_fractions.pdf`、`pcross_relationships.pdf`。
- /diff 关键信息摘录（节选）：
  - 固定随机种子与批处理派生：
    ```python
    p.add_argument("--seed", type=int, default=0)
    ss = np.random.SeedSequence(seed)
    child_seeds = ss.spawn(n_batches)
    ```
  - 运行归档与 `latest/` 复制：
    ```python
    fig_run_dir = FIG_ROOT / prefix / "runs" / run_id
    ...
    copy_latest(fig_peak2, latest_fig / "peak2_vs_dst.pdf")
    copy_latest(scan_csv, latest_data / "scan.csv")
    ```

### `reports/ring_valley_dst/ring_valley_dst_cn.tex`
- 报告内容组织：
  - 同时包含 Case A（`src=6`）与 Case B（`src=1`）的扫描、代表性解析曲线与 MC 统计，并用 `latest/` 目录作为图/表输入路径，避免 run_id 变动影响编译。
  - 明确 second-peak 窗口与穿越比例定义：`P(C=0 | T∈W)` / `P(C≥1 | T∈W)`，并在文中解释“曲线尖锐”的离散时间 PMF 原因。
- 布局修复：
  - 收紧 float/list spacing，减少大块留白。
  - 移除强制换页点，避免“标题+空页”。
  - 缩小汇总表并把复现命令并入结论页，减少尾页空白。
- /diff 关键信息摘录（节选）：
  ```tex
  \usepackage{enumitem}
  \setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
  \setlength{\floatsep}{8pt plus 2pt minus 2pt}
  ```

### `reports/ring_valley_dst/ring_valley_dst_cn.pdf`
- `latexmk -xelatex` 编译生成的可分发报告（当前 11 页），图均以 PDF（矢量）插入。

### `reports/ring_valley_dst/code/bimodality_flux_scan.py`
- 确定性扫描（无随机数）：
  - 用边列表 `src/dst/w` + `np.bincount` 做 master equation 推进得到 `f(t)=P(T=t)`，并记录截断尾部质量上界 `remaining`。
  - 实现两套双峰判据：
    - `fig3_bimodal`：直接复用 `valley_study.detect_peaks_fig3`（论文 Fig.3 caption 规则）。
    - `robust_bimodal`：在 Fig.3 局部峰基础上要求两峰时间间隔 `>= 2K`，并输出谷深指标 `V`（开区间最小值归一化），用作“强双峰”诊断。
  - 输出结构化数据与矢量图，并按 `runs/<run_id>/` 归档、复制到 `latest/` 供 LaTeX 稳定引用：
    - `reports/ring_valley_dst/data/bimodality_flux_scan/<prefix>/latest/scan.csv`
    - `reports/ring_valley_dst/data/bimodality_flux_scan/<prefix>/latest/bimodal_table.tex`
    - `reports/ring_valley_dst/data/bimodality_flux_scan/<prefix>/latest/results.json`
    - `reports/ring_valley_dst/figures/bimodality_flux_scan/<prefix>/latest/*.pdf`
- /diff 关键信息摘录（节选）：
  - 峰间谷深度按开区间计算（避免端点导致 `V≈1` 的假象）：
    ```python
    seg = f[t1 : t2 - 1]
    valley = float(np.min(seg)) if seg.size else float(min(h1, h2))
    valley_ratio = float(valley / hmin)
    ```

### `reports/ring_lazy_flux/ring_lazy_flux_cn.tex`
- 新报告（9 页）：给出模型定义、flux/master equation 方法、双峰判据、两种 `src` 的 `dst` 扫描图/表，以及 AW-vs-flux 交叉核对图（全部插图为 PDF）。
- 通过 `latest/` 目录引用图表，避免 run_id 变动导致编译失败：
  - Case A：`reports/ring_valley_dst/figures/bimodality_flux_scan/N100K6_n0_1_target_50_src_6/latest/`
  - Case B：`reports/ring_valley_dst/figures/bimodality_flux_scan/N100K6_n0_1_target_50_src_1/latest/`

### `reports/ring_lazy_flux/ring_lazy_flux_cn.pdf`
- `latexmk -xelatex` 编译生成的可分发报告（当前 9 页）。

### 生成的归档数据与图（运行产物）
- Case A（`src=6`）：
  - `reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_6/latest/`
  - `reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_6/latest/`
- Case B（`src=1`）：
  - `reports/ring_valley_dst/data/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_1/latest/`
  - `reports/ring_valley_dst/figures/second_peak_dst_shortcut_usage/N100K6_n0_1_target_50_src_1/latest/`
 - Case A（flux 扫描，`src=6`）：
   - `reports/ring_valley_dst/data/bimodality_flux_scan/N100K6_n0_1_target_50_src_6/latest/`
   - `reports/ring_valley_dst/figures/bimodality_flux_scan/N100K6_n0_1_target_50_src_6/latest/`
 - Case B（flux 扫描，`src=1`）：
   - `reports/ring_valley_dst/data/bimodality_flux_scan/N100K6_n0_1_target_50_src_1/latest/`
   - `reports/ring_valley_dst/figures/bimodality_flux_scan/N100K6_n0_1_target_50_src_1/latest/`

## Reproducibility
### 环境（来自运行产物记录）
- 运行平台：macOS（见 `.../latest/results.json: run.platform`）
- Python：3.9.6
- NumPy：2.0.2
- Matplotlib：3.9.4
- 依赖清单：`requirements.txt`
- TeX：TeX Live 2025（`latexmk -xelatex`）
- Runner（/status）：`approval_policy=never`，`sandbox_mode=danger-full-access`，`network_access=enabled`，`shell=zsh`

### 复现步骤
1. 安装 Python 依赖（示例）：
   - `python3 -m venv .venv && source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. 运行扫描 + MC（会自动写入 `reports/ring_valley_dst/data/` 与 `reports/ring_valley_dst/figures/`，并复制到 `latest/`）：
   - Case A：`python3 reports/ring_valley_dst/code/dst_shortcut_usage_mc.py --sc-src 6 --mc-all-bimodal --seed 0`
   - Case B：`python3 reports/ring_valley_dst/code/dst_shortcut_usage_mc.py --sc-src 1 --mc-all-bimodal --seed 0`
   - 可选：用 `--run-id <ID>` 固定输出文件名（否则默认按时间戳生成）。
3. 编译报告：
   - `cd reports/ring_valley_dst && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_valley_dst_cn.tex`
4. 确定性 flux 扫描（无随机种子）：
   - Case A：`python3 reports/ring_valley_dst/code/bimodality_flux_scan.py --sc-src 6 --aw-check`
   - Case B：`python3 reports/ring_valley_dst/code/bimodality_flux_scan.py --sc-src 1 --aw-check`
5. 编译双峰验证报告：
   - `cd reports/ring_lazy_flux && latexmk -xelatex -interaction=nonstopmode -halt-on-error -auxdir=build -emulate-aux-dir ring_lazy_flux_cn.tex`

### 随机性控制
- MC 随机种子由 `--seed` 控制（默认 `0`）；批量采样使用 `SeedSequence(seed)` 派生子 seed，确保同参数同 seed 可复现。
- flux/master equation 扫描为确定性推进，无随机性；截断误差由 `scan.csv` 的 `remaining` 给出尾部质量上界（本次默认 `max_steps=2000`）。

## Notes/TODO
- **最后一页留白**：报告末页仍会有少量空白，但已避免“只剩标题/只剩一段文字占一整页”的情况；如需进一步压缩，可考虑降低字号、或把“总体结论”改为更紧凑的段落样式。
- **更强的 early-peak 证明**：报告用“存在极短吸收路径”解释 early-`t2`；如需更形式化的验证，可加一个可选脚本/flag，把 master equation 的精确传播结果自动导出并在报告中引用。
- **谷深阈值**：大量 Fig.3-bimodal/robust-bimodal 的峰间谷深度指标 $V$ 接近 1；如果将“明显谷”作为硬判据（例如要求 $V\le0.95$），会显著减少被归为“双峰”的 `dst` 数量。
- **截断尾部**：`max_steps=2000` 时最坏 `remaining≈0.02`；若需要更完整的尾部质量或研究更晚的峰，可提高 `--max-steps` 或改为自适应推进到 `remaining<eps_stop`。
- **版本归档**：当前仓库处于“全部文件未被 git 追踪”的状态（`git status` 显示均为 untracked）；若要正式归档与审计，建议补全 git 跟踪与 `.gitignore`（例如忽略 `build/`、预览图等）。
