# valley-k-small

研究随机游走首达时间分布的单仓库，现已整理为“研究内容 + 平台能力”双主轴结构。

## 入口
- 研究内容在 `research/`
- 平台能力在 `platform/`
- 共享 Python 核心库在 `packages/vkcore/src/vkcore/`
- 兼容脚本入口保留在 `scripts/`

## 目录
```text
.
├── research/
│   ├── reports/      # 报告、文稿、图表数据、研究索引
│   ├── docs/         # 研究总览、日志、提交材料
│   └── archives/     # 历史 runs 与归档产物
├── platform/
│   ├── web/          # Next.js 站点与预计算数据
│   ├── tools/        # 实际脚本实现（repo/web/automation）
│   ├── schemas/      # JSON schema
│   ├── skills/       # 仓库与 agent skill
│   ├── agent/        # agent 人格/引导文档
│   └── runtime/      # 本地产物、日志、keepalive 状态
├── packages/
│   └── vkcore/src/vkcore/
├── scripts/          # 兼容包装器与 shell 入口
└── tests/
```

## 最常用命令
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
- `python3 scripts/validate_registry.py`
- `python3 scripts/validate_archives.py`
- `python3 scripts/update_research_summary.py`
- `python3 scripts/check_docs_paths.py`
- `python3 scripts/cleanup_local.py --include-runtime`

## 人看研究
- 研究总览: `research/docs/RESEARCH_SUMMARY.md`
- 文档索引: `research/docs/README.md`
- 报告索引: `research/reports/README.md`

## 人看平台
- 平台说明: `platform/README.md`
- 脚本说明: `scripts/README.md`

## 说明
- 根目录保留了少量旧路径 symlink（如 `reports/`、`docs/`、`site/`），只用于兼容旧脚本与旧文档；新工作流统一使用 `research/`、`platform/`、`packages/` 路径。
