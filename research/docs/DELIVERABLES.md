# Valley-K Small Three Deliverables

This repository ships three primary deliverables from one source of truth:

1. Website (interactive, bilingual, theory + figures):  
   `https://zhouyi-xiaoxiao.github.io/valley-k-small/`
2. Publication-grade compendium PDF (EN/CN):
   - `artifacts/deliverables/publication/valley_k_small_compendium_en.pdf`
   - `artifacts/deliverables/publication/valley_k_small_compendium_cn.pdf`
3. Agent handoff package (machine-readable continuation pack):
   - `artifacts/deliverables/agent_pack/v1/manifest.json`
   - `artifacts/deliverables/agent_pack/v1/report_cards.jsonl`
   - `artifacts/deliverables/agent_pack/v1/AGENT_GUIDE.md`

## Build Commands

- Build all three deliverables with multi-agent style orchestration:
  - `python3 scripts/reportctl.py deliverables --mode full`
- Build website pipeline only:
  - `python3 scripts/reportctl.py web-build --mode full`
- Build publication PDF only:
  - `python3 scripts/reportctl.py publication-pdf --lang en`
  - `python3 scripts/reportctl.py publication-pdf --lang cn`
- Build agent handoff package only:
  - `python3 scripts/reportctl.py agent-pack`

## OpenClaw + Persistent Logs

- High-thinking review output is persisted (not temporary chat):
  - `artifacts/checks/openclaw_review.json`
- Agent pack mirrors OpenClaw findings into:
  - `artifacts/deliverables/agent_pack/v1/openclaw_tasks.json`

## Quality Gates (Now Enforced)

- `python3 scripts/validate_web_data.py` now enforces:
  - KaTeX strict renderability over extracted `math_blocks` + `math_story`
  - CN/EN structure parity for key narrative arrays
  - JSON schema validity for web + agent payloads
- `site/src/components/ReportPlotPanel.tsx` now uses per-series semantics:
  - defaults to metric/probability series
  - blocks smoothing/normalization for binary/parameter helper series
  - log-scale eligibility is evaluated on currently visible series only

## Continuous Multi-Agent Optimization

- Start loop:
  - `bash scripts/loop_ctl.sh start`
- Status:
  - `bash scripts/loop_ctl.sh status`
- Real-time progress files:
  - `artifacts/loop/progress/heartbeat.json`
  - `artifacts/loop/daemon.log`
  - `artifacts/loop/supervisor.log`
