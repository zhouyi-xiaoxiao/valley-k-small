# Figure Language: Shared-X Curve With Embedded Window Bars

This note stores the preferred reusable wording for the Fig. 1 right-hand panel style used in `grid2d_one_target_valley_peak_budget`.

## Recommended Self-Contained Description

This is a shared-x composite figure. The main layer consists of one or more continuous curves that represent how a quantity varies along a common horizontal axis. At a selected set of horizontal positions or time windows, stacked bars are embedded directly into the same panel and aligned to those positions. Each stacked bar encodes the within-window composition of some decomposed quantity, such as normalized component shares, time-budget fractions, or conditional distributions. When multiple conditions are shown, the bars for those conditions are given a slight horizontal offset so they remain visually distinguishable without losing their alignment to the same window. The curves and the stacked bars therefore share the same horizontal coordinate system, but the bars encode window-level composition and do not necessarily share the same vertical physical units as the curves.

## Shorter Caption-Style Description

A shared-x composite panel in which one or more continuous curves are augmented by window-aligned stacked bars that encode normalized within-window composition.

## Chinese Reusable Version

这是一种共享横轴的复合图。图的主体是一条或多条表示某个连续量随横轴变化的曲线；在若干预先选定的横轴位置或时间窗口处，直接嵌入与这些位置对齐的堆叠柱。每根堆叠柱表示对应窗口内某个分解量的组成结构，例如组成比例、时间预算份额或条件分布；柱内各分块之和通常归一化为 1。若存在多个条件或多个数据组，则在同一窗口位置对柱体做轻微横向错开，以避免遮挡并保留可比性。曲线与堆叠柱共享横轴位置，但堆叠柱编码的是窗口级组成信息，不一定与曲线共享同一个纵轴物理量。

## Figure-Specific Wording For This Report

The right-hand panel of Fig. 1 is a shared-x composite panel: the two representative `f(t)` curves for `kappa = 0` and `kappa = 0.0040` are shown on the same time axis, and ring-style stacked composition bars are inserted at the valley and second-peak windows. The bars remain aligned to the corresponding windows, are slightly offset for readability, and encode the normalized time-budget shares in `left side`, `corridor`, and `outer/right side`.
