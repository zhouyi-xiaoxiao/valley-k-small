# exact_recursion_method_guide

教学型方法 companion，系统讲解本仓库主线中使用的 Exact Recursion / time recursion，并与 AW 数值反演、Luca/Giuggioli 生成函数路线做并列比较。

## Canonical Paths
- Manuscript: `research/reports/exact_recursion_method_guide/manuscript/exact_recursion_method_guide_cn.tex`
- PDF: `research/reports/exact_recursion_method_guide/manuscript/exact_recursion_method_guide_cn.pdf`
- Figures: `research/reports/exact_recursion_method_guide/artifacts/figures/`
- Tables: `research/reports/exact_recursion_method_guide/artifacts/tables/`
- Notes: `research/reports/exact_recursion_method_guide/notes/`

## Reproduce
From repo root:

```bash
python3 scripts/reportctl.py build --report exact_recursion_method_guide --lang cn
```

## Notes
- 这是一个文稿优先的 explanatory report，当前不依赖单独的 `code/` 入口脚本。
- 主线例子固定使用 `grid2d_one_two_target_gating` 的 shared symmetric one-target baseline。
