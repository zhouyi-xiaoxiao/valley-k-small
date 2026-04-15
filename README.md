# valley-k-small

随机游走首达时间分布研究仓库，采用单一 canonical 结构：
- 人类优先阅读 `research/` 和 `platform/`
- agent 通过 `reportctl` 生成 handoff/pack，而不是依赖第二套仓库镜像
- 本地运行时状态统一放在隐藏目录 `.local/`
- 仓库默认按 agent-first 组织；人的参与主要是自然语言指令、调试协助和 PDF 方向性反馈

## Canonical Layout
```text
.
├── README.md
├── AGENTS.md
├── pyproject.toml
├── requirements.txt
├── research/
│   ├── reports/
│   ├── docs/
│   └── archives/
├── platform/
│   ├── web/
│   ├── agent/
│   ├── schemas/
│   ├── skills/
│   └── tools/
├── packages/
│   └── vkcore/src/vkcore/
├── scripts/
│   ├── reportctl.py
│   ├── ka
│   └── README.md
└── tests/
```

## Human Entry Points
- 研究总览: `research/docs/RESEARCH_SUMMARY.md`
- 研究文档索引: `research/docs/README.md`
- 报告目录索引: `research/reports/README.md`
- 平台与工具说明: `platform/README.md`

## Agent Entry Points
- 仓库约束: `AGENTS.md`
- continuation skill: `platform/skills/valley-k-small-continuation/`
- 生成 agent 视图:
  - `python3 scripts/reportctl.py agent-sync`
  - `python3 scripts/reportctl.py agent-pack`
- 生成输出位置: `.local/deliverables/agent_pack/v1`

## Common Commands
- `python3 scripts/reportctl.py list`
- `python3 scripts/reportctl.py resolve --report ring_valley_dst`
- `python3 scripts/reportctl.py build --report ring_valley_dst --lang cn`
- `python3 scripts/reportctl.py summary`
- `python3 scripts/reportctl.py validate-registry`
- `python3 scripts/reportctl.py validate-archives`
- `python3 scripts/reportctl.py check-docs-paths`
- `python3 scripts/reportctl.py doctor`
- `python3 scripts/reportctl.py cleanup --include-runtime`
- `./scripts/ka start <job> [task text...]`

## Reproducible Setup
```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python3 scripts/reportctl.py doctor
```

- `scripts/reportctl.py` 会在仓库根目录存在 `.venv/bin/python` 时优先使用它，避免校验链路落到系统 Python。
- 对外公开时，根目录只保留 canonical 表面：`research/`、`platform/`、`packages/`、`scripts/`、`tests/` 与 4 个根文件。

## Local State
- 站点预计算输出与公开静态资产会写入被 `.gitignore` 忽略的 web public 生成目录，不属于 canonical 仓库树
- `.local/checks/`、`.local/deliverables/`、`.local/keepalive/`、`.local/loop/` 是隐藏本地状态
- 这些路径都不属于人工主阅读面
