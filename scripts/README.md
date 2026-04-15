# Scripts

公开脚本表面只保留 3 个入口：
- `scripts/reportctl.py`: 唯一 Python CLI
- `scripts/ka`: keepalive / recurring Codex shell 入口
- `scripts/README.md`: 本说明

## `reportctl` 常用子命令
- `list`
- `resolve`
- `run`
- `build`
- `summary`
- `cleanup`
- `validate-registry`
- `validate-archives`
- `check-docs-paths`
- `audit`
- `doctor`
- `web-data`
- `book-data`
- `translation-qc`
- `validate-web-data`
- `agent-sync`
- `agent-pack`
- `publication-pdf`
- `deliverables`

## Keepalive
- 启动: `./scripts/ka start <job> [task text...]`
- 查看状态: `./scripts/ka status <job>`
- 查看日志: `./scripts/ka logs <job> [tail]`
- 停止: `./scripts/ka stop <job>`
