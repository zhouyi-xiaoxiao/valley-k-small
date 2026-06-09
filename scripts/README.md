# Scripts

公开脚本表面只保留 3 个入口：
- `scripts/reportctl.py`: 唯一 Python CLI
- `scripts/ka`: keepalive / recurring Codex shell 入口
- `scripts/README.md`: 本说明

## `reportctl` 全部子命令（29 个）

报告操作:
- `list`
- `resolve`
- `run`
- `build`
- `summary`
- `archive`
- `prune-legacy-artifacts`
- `cleanup`

校验与健康检查:
- `validate-registry`
- `validate-archives`
- `check-docs-paths`
- `validate-science-rules`
- `audit`
- `doctor`
- `translation-qc`
- `validate-web-data`

站点与数据生成:
- `web-data`
- `book-data`
- `backbone-data`
- `web-build`
- `web-preview`
- `book-preview`
- `sync-local-remote`

agent 与交付:
- `agent-sync`
- `agent-pack`
- `publication-pdf`
- `deliverables`
- `openclaw-review`
- `content-iterate`

## Keepalive
- 启动: `./scripts/ka start <job> [task text...]`
- 查看状态: `./scripts/ka status <job>`
- 查看日志: `./scripts/ka logs <job> [tail]`
- 停止: `./scripts/ka stop <job>`
