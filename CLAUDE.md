# CLAUDE.md

Cold-start router for AI agents (Claude Code, Codex, Cursor, etc.).

## What this repo is

`valley-k-small` is a PhD research repo on first-passage and first-encounter
time distributions in structured lattice random walks. It studies shoulders,
local bumps, second peaks, double-peak-like structures, shortcut mechanisms,
target-channel decompositions, and encounter-position decompositions. Hybrid
Python (analysis + automation) + Next.js (talk site, interactive report
browsing). The repo is **agent-first**: agents are the primary operators;
humans give natural-language direction and feedback on PDF outputs.

The remaining work is to revise current reports and figures, extend 1D and 2D
two-target first-passage models, validate reflecting-boundary two-walker
encounters, and decompose encounter distributions by diagonal encounter
position.

## Read these in order

1. **`AGENTS.md`** — the repo contract. Mandatory upkeep, validation, cleanup, conventions. Authoritative.
2. **`README.md`** (Chinese) — canonical layout: `research/`, `platform/`, `packages/vkcore/`, `scripts/`, `tests/`.
3. **`platform/skills/valley-k-small-continuation/SKILL.md`** — operational playbook with workflow router and reference docs (`core-checklist.md`, `report-map.md`, `research-conventions.md`).
4. **`scripts/README.md`** — public CLI surface (29 `reportctl.py` subcommands + `ka` keepalive).

## Public CLI surface

Only two scripts are public. Don't call internals in `platform/tools/` directly.

```bash
python3 scripts/reportctl.py --help     # master CLI: list, resolve, build, validate, cleanup, summary, agent-pack, ...
./scripts/ka --help                     # keepalive job runner for recurring Codex execution
```

Health check: `python3 scripts/reportctl.py doctor`.

## General development rules

- Keep changes scoped to the requested report, document, or tool.
- Do not modify scientific code for guardrail, roadmap, or documentation-only
  tasks.
- Do not run large scans unless the prompt explicitly asks for them.
- Do not modify unrelated reports.
- Use `reportctl.py` for public repository operations.
- Keep generated outputs deterministic when practical and inside the owning
  report's `artifacts/` or `manuscript/` tree.

## Mathematical guardrails

- Transition probabilities must be nonnegative.
- Discrete-time transition matrices must be row-stochastic unless a report
  explicitly documents another convention.
- Absorbing targets must stop the process immediately.
- Mass balance must hold.
- Two-target decomposition must satisfy `f_total(t)=f_target1(t)+f_target2(t)`.
- Encounter decomposition must satisfy `f_E(t)=sum_k f_k(t)`.
- Do not confuse mean first-passage time with the full first-passage
  distribution.
- Do not call a curve `double_peak` unless the classifier criteria are met.
- Do not overclaim double peaks from visual inspection; use `shoulder` or
  `local_bump` for weaker structures.

## Boundary-condition conventions

- Reflecting boundary means attempted-outside-stays unless stated otherwise.
- State periodic, reflecting, absorbing, mixed, lazy, and non-lazy conventions
  before comparing results across reports or models.
- Absorbing targets have priority over subsequent transition choices.
- Do not state that the 2D encounter walker always has eight directions unless
  synchronous lazy update is explicitly used.

## Plotting rules

- Make figures readable at report scale: clear axes, units, legends, parameter
  payload, boundary mode, and target/encounter labels.
- If a plot highlights peaks or bumps, include classifier labels or a nearby
  diagnostic artifact with thresholds.
- Use vector figures for manuscript inclusion where possible.
- Do not title or caption a curve as `double_peak` unless the classifier output
  says `double_peak`.

## Testing expectations

- For documentation and guardrail changes: run `python3 scripts/reportctl.py
  check-docs-paths` and `python3 scripts/reportctl.py validate-science-rules`.
- For code changes: run focused pytest tests plus the relevant `reportctl`
  validation or build.
- For transition kernels: test nonnegativity, row sums, absorbing-state
  stopping, and mass balance.
- For two-target and encounter decompositions: test `f_total(t)=f_target1(t)+f_target2(t)`
  and `f_E(t)=sum_k f_k(t)`.

## Report output conventions

- Report code goes in `research/reports/<id>/code/`.
- Figures, tables, data, and outputs go in `research/reports/<id>/artifacts/`.
- Manuscripts, extras, and build directories go in
  `research/reports/<id>/manuscript/`.
- Notes and reproducibility logs go in `research/reports/<id>/notes/`.
- Final handoffs must list changed files, commands run, generated outputs,
  validation errors, and remaining risks.

## Gotchas (read before touching code)

- **`platform/web/src/components/TalkRevealDeck.tsx` is custom React, NOT reveal.js.** Do not import `reveal.js`, do not use `Reveal.initialize`, `data-state` attributes, or slide events. Navigation is internal React state driven by URL hash (`#slide-N`). See file header.
- **`npm run dev` port falls back silently.** Defaults to 3000, jumps to 3001 if busy. Read the actual port from stdout — don't hardcode.
- **Mandatory after editing reports/docs**: run `python3 scripts/reportctl.py summary` to refresh `research/docs/RESEARCH_SUMMARY.md`. Stale summary breaks the agent contract.
- **Do not commit**: `.venv*/`, `venv/`, `build/`, `.next/`, `out/`, `node_modules/`, `__pycache__/`, `*.pyc`, `.local/`. (`.gitignore` covers these — verify before adding new artifact paths.)
- **`.local/`** is the canonical sink for runtime state and deliverables. Agent packs land at `.local/deliverables/agent_pack/v1`.
- **Runtime dirs are diverted out of OneDrive (od-divert, 2026-06-09).** `.venv`, `.local`, `platform/web/{node_modules,.next,out}`, and `platform/web/public/artifacts` are symlinks into `~/.local-build/valley-k-small/`. Source stays OneDrive-synced; builds and venv I/O hit real local disk (fixes the numpy-`.so` mmap failures and the `next build` sync storm). If a target is missing, regenerate it in place (`python3 -m venv`, `npm install`, `next build`, `reportctl web-data`) — content lands outside OneDrive automatically. Two npm caveats: (1) `npm ci` deletes the `node_modules` symlink itself and reinstalls into OneDrive — use `npm install`, or re-divert afterwards; (2) Next.js workers resolve modules from the `.next` REALPATH, so `~/.local-build/valley-k-small/node_modules` must stay symlinked to the diverted node_modules or builds die with `Cannot find module 'react/jsx-runtime'`. Do NOT divert `platform/web/public/data/v1` (contains tracked files; git does not follow symlinks).

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
