# DPMA 教学状态与 agent 交接协议(v2 — 单轨课程)

**目的**:用户(第一作者)要从零系统搞懂自己的 DPMA 工作。任何 agent 接手前先读本文件。

## 唯一正典:`dpma_course.html`(2026-07-04 起)

单文件交互课程,双击离线可用。KaTeX 本地渲染(`vendor/katex/`,勿删 fonts),
交互数据 `dpma_demo_data.js`(再生:`cd ../../../code && $VENV/python3 dpma_tutorial_demo_data.py`),
逻辑在 `dpma_course.js`。**只假设数学分析 + 高等代数**(用户明确说不知道"谱分解"是什么
——第 0 章先把谱分解翻译成"实对称矩阵正交对角化"再开讲,这个假设水位不许抬高)。

结构(2026-07-04 完备性大修后,共 11 节):第 0 章预备知识 → 1 模型 → 2 双峰直觉(实验一:
走子直方图)→ 3 精确解(Montroll 行列式 D_u,成稿 Eq.5 原形)→ 4 负权重造峰(实验二:双指数
调音台)→ 5 逐项归因(实验三:模开关;含通道≠模警示)→ 6 鞍结分岔(实验四:b 滑条;含谱矩
S_n 正式定义、解析前置系数、6.5 最小三模定理/Laguerre/K 截断)→ 7 连续极限(含 7.3 幅值
G=2w²φI/J、J 恒等式、端点半直线 B*/c*)→ 8 证据链与扩展(成稿 Sec.IV–V:五重验证、Woodbury、
双门三峰 cusp、2D+对数警告、稳健性)→ 9 全景/Luca字典/六月定律接线/resetting≠delivery/非厄米辨析
→ 附录:符号总表 + **成稿逐节对照表(coverage map)**。关键名词均带英文。
每章:goal 框、keybox(关键公式)、warn(常见误解)、details 折叠推导、自测+折叠答案、
`<div class="qa-anchor" id="qa-chN">` 追问区锚点。进度勾选存 localStorage。

**完备性契约**:成稿每个 Sec./App. 在附录对照表里都有课程席位;深度约定 = 正文覆盖"定义/来源/作用",
附录逐行代数(N_{r,u} 分段式、I,J 反导函数)不搬运、按需追问展开。改成稿必须同步改对照表。
**2026-07-04 大修修掉的两处教学错误(勿回退)**:①第 3 章特征方程此前写成 1−λ(2/q)U·U/U 形
(符号错),已改成稿 Eq.5 的 D_u=aU_{N-1}+2U_{u-1}U_{N-u-1};②S_n 此前被讲成"lnΦ 对 lnτ 的
n 阶导"(错),正确定义是带符号谱矩 ΣG_jμ_j^n e^{−μ_jτ},fold 在普通 τ 坐标。

**已废弃(留档不再更新)**:`dpma_study_book.tex`/`build_book/`(PDF 书)与
`dpma_interactive.html`(旧实验室,页首已挂废弃横幅)。v1 双轨被用户否决:两个来回切换麻烦、
旧页公式渲染不全、起点假设过高。原书第 1 站内容(含 Q1:与 Luca 手稿的关系)已并入课程第 1、8 章。

## 追问协议(核心工作流)

用户在聊天里提问 → 简答在聊天 + 完整版写进课程对应章节的追问区:在 `qa-chN` 锚点前插入

```html
<div class="qa"><span class="qdate">Q(YYYY-MM-DD)</span> 问题……<br>回答……(公式用 \( \) / \[ \])</div>
```

然后无头 Chrome 截图该章验证渲染(命令见下)再答复。

## 验证命令

```bash
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless --disable-gpu --window-size=1400,2600 --virtual-time-budget=6000 \
  --screenshot=/tmp/course.png "file://$PWD/dpma_course.html#ch0"
```

## 教学纪律(务必遵守)

1. 符号纪律:与成稿 `../../dpma_prr_manuscript.tex` 一致(P_λ, a, F(t), B_j, s_j, Φ, S_n,
   b, θ, ξ, τ);别自创记号。
2. 数字纪律:所有常数以 `../../../artifacts/tables/` 工件为准;**d=3/d=4 塌落常数不同**
   (1.0–1.1e3 vs 1.4e3);**"50 位"只是运算精度**;**分类器窗 βN≈3.15 ≠ fold 窗 βN≈6.15**
   (两套判据,映射见六月报告 §3b)——这三个坑都在 2026-07-03 对抗审计里翻过车。
3. 讲错比不讲严重:不确定的数,先跑 venv python(`~/.local-build/valley-k-small/.venv/bin/python3`,
   在 `code/` 里跑)验证再写。
4. 用户自称"比你想象的菜":解释宁慢勿跳步;新术语必须先落到高等代数/数学分析已有概念上。

## 学习进度(随时更新)

| 章 | 状态 |
|---|---|
| 0–8 全部章节 + 附录 | ✅ 内容已写好并渲染验证(2026-07-04) |
| 用户实际学到 | 尚未开始;上一轮(v1 书)只讲过旧第 1 站 |
| 验收方式 | 第 8 章"三场一分钟对话"讲给 agent 听,agent 当审稿人 |

## 相关文件地图

成稿 `../../dpma_prr_manuscript.tex`(14pp);Luca 汇报包 `../dpma_luca_stepwise_report_20260703.md`
+ `../../../artifacts/figures/dpma_luca_pack.pdf`;六月定律报告 `../../../notes/dpma_final_report_20260612.md`;
记忆条目 `project_dpma_double_peak.md`(含勘误)。
