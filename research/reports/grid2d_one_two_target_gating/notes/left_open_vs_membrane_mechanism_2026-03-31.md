# left_open_vs_membrane_mechanism_2026-03-31

## 结论先行

如果 one-target 的研究主题从“半透膜 first-leak 的早/晚时序”进一步收束为

- 有多少轨迹穿过半透膜
- 有多少轨迹从 corridor 左端开口离开了 corridor 区域
- 它们分别怎样贡献第一峰与第二峰

那么当前 canonical 报告还不算最终完成稿，但已经有了足够的数据基础。缺的不是更多主扫描，而是把已有结果重新组织成一条更直接的机制叙事。

最重要的新结论是：

- 第一峰主要是 corridor 快路径。
- 第二峰主要不是“膜峰”，而是“左端开口 detour + rollback”峰。
- 纯 membrane-only 贡献在第二峰中始终很小；半透膜更像次级修饰，而不是第二峰主体来源。

## 当前稿子已经回答了什么

当前 canonical one-target 稿件已经比较完整地回答了下面这些问题：

- 半透膜 first-leak 是否发生，以及相对 canonical x-gate 是早还是晚。
- rollback 是否发生，也就是轨迹离开起始盆地 A 后是否又回到 A。
- top/bottom 膜不对称与 same-membrane directional 不对称如何改变双峰。
- start position、x-gate、代表点窗口分解如何影响 phase 和第二峰强弱。

因此，如果主题仍然是：

- “半透膜 leak 的早/晚”
- “rollback 是不是第二峰主机制”

那么当前稿件已经够 strong。

## 当前稿子还不够的地方

如果主题改成：

- “Reflective + 半透膜 corridor 几何里，第二峰到底有多少来自穿膜，多少来自从左端开口离开 corridor”

那当前 canonical 稿子还差一个关键补充：

- 它把膜 leak 讲清楚了
- 但还没有把“左端开口出去”单独量化成一条和 membrane leak 平行的机制线

也就是说，当前稿子默认了：

- `P/Q` 只统计 membrane leak

但没有把

- “进入 outside 的所有方式”
- “只走左口”
- “只走膜”
- “两者都走过”

系统地放进主文。

## 新增分析后最适合的主叙事

### 1. 第一峰

第一峰应表述为：

- 绝大多数命中轨迹不发生任何 corridor-to-outside exit；
- 它们主要一直留在 corridor 内部并快速到达 target；
- 因此第一峰是典型的 fast corridor branch。

baseline 的窗口分解显示：

- `peak1`: `none = 93.2%`
- `left_only = 6.56%`
- `mem_only = 0.18%`
- `both = 0.06%`

所以“第一峰就是直接走通道”这个说法基本成立，只需要补一句“仍有极小部分早期左口 detour”即可。

### 2. 第二峰

第二峰更适合表述为：

- 第二峰主体是左端开口 detour 之后的 delayed branch；
- 其中很大一部分还伴随 rollback 到起始盆地 A；
- 纯 membrane-only 轨迹只占很小比例；
- 膜更像是调节 late branch 宽度、时间尺度和 side usage 的次级因素。

baseline 的窗口分解显示：

- `peak2`: `left_only = 77.5%`
- `both = 8.15%`
- `mem_only = 0.62%`
- `none = 13.7%`

同一窗口的 first-event 统计显示：

- `tau_left` 概率约 `0.856`
- `tau_mem` 概率约 `0.0877`

这说明：

- 几乎所有第二峰候选轨迹都经历过“从左口离开 corridor”的事件；
- 只有少数第二峰轨迹真正依赖 membrane crossing。

### 3. phase 依赖的总体规律

在补充的 left-open vs membrane 全扫描中：

- `phase=2` case 的第二峰平均：
  - `late_left_only ≈ 0.752`
  - `late_mem_only ≈ 0.007`
  - `late_both ≈ 0.072`
  - `late_none ≈ 0.170`
- `phase=1` case 的第二峰平均：
  - `late_left_only ≈ 0.793`
  - `late_mem_only ≈ 0.005`
  - `late_both ≈ 0.126`
  - `late_none ≈ 0.076`

这说明第二峰在 clear/weak 双峰区里都稳定地由 left-open detour 主导，而不是由 membrane-only 轨迹主导。

## 对 sensitivity 扫描的最合适解释

已经补做的 sensitivity 表明：

- `corridor_halfwidth`、`bx` 主要决定 second peak 能否维持清楚的 slow branch。
- `delta_core`、`delta_open` 主要决定 second peak 的时间位置和分离度。
- `kappa_c2o`、`kappa_o2c` 更适合解释膜相关次级贡献，而不是 second peak 的主体来源。

因此，若主题切到“左口 vs 膜”的贡献分解，最自然的解释是：

- corridor 几何与 corridor 内驱动决定了有没有显著 left-open detour branch；
- membrane permeability 主要决定这条 late branch 里有多少次级 membrane-assisted mixing。

## 建议新增到 manuscript 的内容

最少应该新增一节：

- `one-target: left-open vs membrane exit decomposition`

这一节只需要回答三个问题：

1. 第一峰里各类贡献分别是多少。
2. 第二峰里各类贡献分别是多少。
3. sensitivity 扫描下，这个结论是否稳定。

## 建议新增的最少图表

如果只允许加很少的新内容，优先级建议如下：

1. 一张 baseline 三窗口 stacked bar
   - `peak1 / valley / peak2`
   - `none / left_only / mem_only / both`

2. 一张 sensitivity summary table
   - baseline
   - 最强双峰点
   - 最弱 phase1 点
   - 强 `delta_open` 点
   - 弱 corridor-bias 点

3. 一段文字把 `tau_left` 和 `tau_mem` 的含义并列说明
   - `tau_left`: first left-open corridor-to-outside exit
   - `tau_mem`: first membrane corridor-to-outside crossing

如果篇幅允许，再加：

4. 两张 parameter heatmap
   - `late_left_only`
   - `late_both`

这两张通常已经足够说明“第二峰主体来自左口，而膜主要通过 both-class 混入 late branch”。

## 对“稿子够不够好”的判断

当前稿子作为

- membrane leak
- rollback
- x-gate timing

这三条线的 canonical 整理稿，已经很好。

但如果你现在真正想让读者记住的是：

- “第二峰并不是半透膜峰，而主要是左口 detour 峰”

那我认为还差最后这一步：

- 把 left-open vs membrane 的四分类放进主文
- 把现有的膜 leak 叙事从“主体机制”降成“次级修饰机制”

## 我建议的最终主题句

最值得作为最终主题句的版本是：

> 在 reflective wall + semipermeable membrane 的 one-target corridor 几何中，第一峰对应 corridor 内快路径；第二峰不是由纯 membrane crossing 主导，而主要由从左端开口离开 corridor 的 detour/rollback 轨迹生成。半透膜主要调节这条 late branch 的次级混合与时间分布，而不是其主体质量来源。

## 对应数据文件

- baseline / sensitivity 总表：`artifacts/data/sensitivity/one_target_all_cases.csv`
- left-open vs membrane case summary：`artifacts/data/sensitivity/one_target_left_open_split_cases.csv`
- left-open vs membrane window summary：`artifacts/data/sensitivity/one_target_left_open_split_windows.csv`
- left-open vs membrane first-event summary：`artifacts/data/sensitivity/one_target_left_open_split_events.csv`
