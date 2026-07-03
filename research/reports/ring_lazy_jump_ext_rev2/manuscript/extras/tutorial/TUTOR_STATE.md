# DPMA 学习书 — 教学状态与 agent 交接协议

**目的**:用户(第一作者)要从零系统搞懂自己的 DPMA 工作。教学是**增量式**的:
聊天里讲一站 → 用户追问 → 回答写进书的"追问区" → 重编译。任何 agent 接手前先读本文件。

## 产物(全在本目录)
- `dpma_study_book.tex` → `build_book/dpma_study_book.pdf` — **主教材**(严谨数学,符号与
  成稿 `../../dpma_prr_manuscript.tex` 完全一致)。
- `dpma_interactive.html` + `dpma_demo_data.js` — **直觉实验室**(双击离线可用):
  实验一走子动画(站2)、实验二模开关(站4–5)、实验三 b 滑条鞍结(站6)。
  数据再生:`cd ../../../code && $VENV/python3 dpma_tutorial_demo_data.py`。
- 编译:`cd tutorial/ && xelatex -output-directory build_book dpma_study_book.tex`(×2;
  xelatex + ctex fontset=mac;venv 无关)。build_book/ 不提交(gitignore 的 build 约定)。

## 教学进度(随时更新此表!)
| 站 | 状态 | 说明 |
|---|---|---|
| 1 舞台与矩阵 | ✅ 已讲并入书(书 §1) | 含 Q1(Luca 手稿关系)已答 |
| 2 F(t) 与双峰直觉 | ⏳ 下一站 | 书 §2 只有引子;讲法:先让用户玩实验一,再讲两种剧本的时标估计(捕获时标 vs 绕环扩散时标 N²),引出"分得开才有双峰" |
| 3 精确解(Chebyshev) | ☐ | 对应成稿 App. A;讲矩阵行列式引理→D_u(y)→残数 |
| 4 模展开 | ☐ | s_j/B_j;衔接 Luca pack 面板(2)(3) |
| 5 归因 | ☐ | pack 面板(4);尾=1模、第二峰=3模(115%)、谷≈9、首峰≈31 |
| 6 鞍结分岔 | ☐ | S₁=S₂=0;实验三;全文心脏 |
| 7 相边界与常数 | ☐ | b_c(θ)、3.076432、0.789026(半直线变换)、(1/2,3/2) 标度 |
| 8 新颖性定位 | ☐ | 成稿 Sec. I 的 known-vs-new;也是对 Luca/审稿人的话术 |

## 教学纪律(务必遵守)
1. **一次只讲一站**,讲完停下等追问;每站结尾留一个钩子问题引出下一站。
2. 用户的每个追问 → 简答在聊天 + **完整版写进书对应章节"追问区"**(标日期)→ 重编译。
3. 符号纪律:与成稿一致(P_λ, a, F(t), B_j, s_j, Φ, S_n, b, θ, ξ, τ);别自创记号。
4. 数字纪律:所有常数以 `../../artifacts/tables/` 工件为准;**d=3/d=4 的塌落常数不同**
  (1.0–1.1e3 vs 1.4e3),**"50位"只是运算精度**——见 2026-07-03 对抗审计教训
  (`../dpma_luca_stepwise_report_20260703.md` 尾注)。
5. 讲错比不讲严重:不确定的数,先跑 venv python 验证再写进书。

## 相关文件地图
成稿 `../../dpma_prr_manuscript.tex`(14pp);Luca 汇报包 `../dpma_luca_stepwise_report_20260703.md`
+ `../../../artifacts/figures/dpma_luca_pack.pdf`;六月定律报告 `../../../notes/dpma_final_report_20260612.md`;
记忆条目 `project_dpma_double_peak.md`(含勘误)。
