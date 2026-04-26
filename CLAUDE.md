# CLAUDE.md

Cold-start router for AI agents (Claude Code, Codex, Cursor, etc.).

## What this repo is

`valley-k-small` — a PhD research repo on first-passage time distributions of random walks (bimodality, valley/peak criteria, shortcut mechanisms, cross-model comparison). Hybrid Python (analysis + automation) + Next.js (talk site, interactive report browsing). The repo is **agent-first**: agents are the primary operators; humans give natural-language direction and feedback on PDF outputs.

## Read these in order

1. **`AGENTS.md`** — the repo contract. Mandatory upkeep, validation, cleanup, conventions. Authoritative.
2. **`README.md`** (Chinese) — canonical layout: `research/`, `platform/`, `packages/vkcore/`, `scripts/`, `tests/`.
3. **`platform/skills/valley-k-small-continuation/SKILL.md`** — operational playbook with workflow router and reference docs (`core-checklist.md`, `report-map.md`, `research-conventions.md`).
4. **`scripts/README.md`** — public CLI surface (28 `reportctl.py` subcommands + `ka` keepalive).

## Public CLI surface

Only two scripts are public. Don't call internals in `platform/tools/` directly.

```bash
python3 scripts/reportctl.py --help     # master CLI: list, resolve, build, validate, cleanup, summary, agent-pack, ...
./scripts/ka --help                     # keepalive job runner for recurring Codex execution
```

Health check: `python3 scripts/reportctl.py doctor`.

## Gotchas (read before touching code)

- **`platform/web/src/components/TalkRevealDeck.tsx` is custom React, NOT reveal.js.** Do not import `reveal.js`, do not use `Reveal.initialize`, `data-state` attributes, or slide events. Navigation is internal React state driven by URL hash (`#slide-N`). See file header.
- **`npm run dev` port falls back silently.** Defaults to 3000, jumps to 3001 if busy. Read the actual port from stdout — don't hardcode.
- **Mandatory after editing reports/docs**: run `python3 scripts/reportctl.py summary` to refresh `research/docs/RESEARCH_SUMMARY.md`. Stale summary breaks the agent contract.
- **Do not commit**: `.venv*/`, `venv/`, `build/`, `.next/`, `out/`, `node_modules/`, `__pycache__/`, `*.pyc`, `.local/`. (`.gitignore` covers these — verify before adding new artifact paths.)
- **`.local/`** is the canonical sink for runtime state and deliverables. Agent packs land at `.local/deliverables/agent_pack/v1`.

## Where things live

| Path | What |
|---|---|
| `research/reports/<id>/{code,notes,manuscript,artifacts}/` | One report per directory. No loose `*.tex` / `*.pdf` at the report root. |
| `research/docs/RESEARCH_SUMMARY.md` | Auto-generated repo brief. Refresh via `reportctl.py summary`. |
| `platform/web/` | Next.js static-export site. Builds to `public/data/v1/` + `public/artifacts/`. |
| `platform/tools/{repo,web,automation}/` | Real implementations behind `reportctl.py`. |
| `packages/vkcore/src/vkcore/{common,grid2d,ring,comparison}/` | Shared Python. |
| `scripts/` | The only public script surface. |
| `tests/` | pytest. |

## Conventions

- Python: 4-space indent, type hints preferred, `snake_case` functions/vars, `CamelCase` classes.
- Keep generated outputs deterministic where practical.
- Bilingual: Chinese for research narrative + root README; English for `AGENTS.md` and this file.
