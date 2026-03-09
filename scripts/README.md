# Scripts

`scripts/` 现在是兼容入口层，不再承载主要实现。

## 结构
- `scripts/*.py`: 薄包装器，转发到 `platform/tools/{repo,web,automation}/`
- `scripts/ka`, `scripts/keepalive`: 日常 shell 入口
- `scripts/loop_*.sh`: 辅助 shell 控制脚本

## 最常用入口
- `python3 scripts/reportctl.py list`
- `python3 scripts/validate_registry.py`
- `python3 scripts/validate_archives.py`
- `python3 scripts/update_research_summary.py`
- `python3 scripts/check_docs_paths.py`
- `python3 scripts/build_web_data.py --mode full`
- `python3 scripts/build_agent_sync.py`
- `python3 scripts/validate_web_data.py`
- `./scripts/ka start <job> [task text...]`

## 实现位置
- 仓库维护实现: `platform/tools/repo/`
- Web / deliverable 实现: `platform/tools/web/`
- 自动化实现: `platform/tools/automation/`
