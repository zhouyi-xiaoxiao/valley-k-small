# Valley-K Small Deliverables

仓库当前的三类主要交付物：

1. Website
   - `https://zhouyi-xiaoxiao.github.io/valley-k-small/`
2. Publication PDF
   - `.local/deliverables/publication/valley_k_small_compendium_en.pdf`
   - `.local/deliverables/publication/valley_k_small_compendium_cn.pdf`
3. Agent handoff pack
   - `.local/deliverables/agent_pack/v1/manifest.json`
   - `.local/deliverables/agent_pack/v1/report_cards.jsonl`
   - `.local/deliverables/agent_pack/v1/AGENT_GUIDE.md`

## Build Commands
- All deliverables:
  - `python3 scripts/reportctl.py deliverables --mode full`
- Website pipeline:
  - `python3 scripts/reportctl.py web-build --mode full`
- Publication PDF:
  - `python3 scripts/reportctl.py publication-pdf --lang en`
  - `python3 scripts/reportctl.py publication-pdf --lang cn`
- Agent handoff pack:
  - `python3 scripts/reportctl.py agent-pack`

## Validation
- Translation QC:
  - `python3 scripts/reportctl.py translation-qc`
- Web payload schema validation:
  - `python3 scripts/reportctl.py validate-web-data`
- Full repo gate:
  - `python3 scripts/reportctl.py doctor`

## Persistent Review Traces
- OpenClaw review:
  - `.local/checks/openclaw_review.json`
- Content iteration history:
  - `.local/checks/content_iteration/run_history.jsonl`
