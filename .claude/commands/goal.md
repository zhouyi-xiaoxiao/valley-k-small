---
description: Full repo audit + unify + regenerate pass for valley-k-small. Runs the reportctl harness, checks governance-doc consistency the harness can't, applies only safe unifications, surfaces risky decisions, and writes a structured handoff.
argument-hint: "[audit | full | <report_id>] [--no-commit]"
---

# /goal — complete update · audit · unify for `valley-k-small`

You are running the repository's **goal** command: a single, repeatable pass that
leaves `valley-k-small` fully **audited**, **updated**, and **unified** — every
canonical source consistent with reality and with each other — and produces an
honest handoff. Treat this as a *goal with acceptance criteria* (below), not a
checklist to skim.

Arguments passed: `$ARGUMENTS`

---

## 0 · Goal & acceptance criteria

The run **succeeds** only when all of these are true (report each as ✅/⚠️/❌ at the end):

1. Every `reportctl` validation in Phase 2 exits clean (or each failure is explained + triaged).
2. Every **canonical source** in the table below is consistent with the filesystem and with the docs that mirror it.
3. `research/docs/RESEARCH_SUMMARY.md` (date + `AUTO-INDEX`) reflects the current registry.
4. Working tree is either clean, or every change is intentional and listed in the handoff.
5. No scientific code was modified, no report content was moved/deleted, nothing was pushed — unless this pass only *recommended* it and a human approved.

Stop and ask the human (don't grind) when: a canonical source conflict has no safe
resolution, a fix would touch scientific code or move report content, or a `reportctl`
failure implies real scientific/data breakage rather than a doc/path nit.

---

## 1 · Single source of truth (the unification contract)

These decisions are **authoritative**. When two places disagree, the canonical one wins
and the other is brought into line (or flagged if that isn't safe to automate).

| Concern | ✅ Canonical source | Mirrors / derived (must defer, never compete) |
|---|---|---|
| Repo contract, math/boundary/plotting/testing guardrails | `AGENTS.md` | `CLAUDE.md` keeps a **load-bearing copy** for Claude cold-start — keep it but it must stay *in sync* with AGENTS.md, never diverge |
| AI cold-start router | `CLAUDE.md` | — |
| Human layout + entry points (zh) | `README.md` | — |
| Machine report registry | `research/reports/report_registry.yaml` | `report-map.md` is a human view; index READMEs + AUTO-INDEX derive from it |
| Repo brief / overview | `research/docs/RESEARCH_SUMMARY.md` (auto-generated) | regenerate via `reportctl.py summary`; **never hand-edit** the `AUTO-INDEX` block |
| Human report inventory | `research/reports/README.md` + `research/docs/README.md` | must list exactly the registry's reports |
| Operational playbook | `platform/skills/valley-k-small-continuation/SKILL.md` (+ `core-checklist.md`, `report-map.md`, `research-conventions.md`) | — |
| Public CLI surface | `scripts/reportctl.py` and `scripts/ka` | never call `platform/tools/**` directly; never invent a parallel script |
| Runtime/deliverable sink | `.local/` | always git-ignored, never a human read surface |

> **Per-report layout is canonical at `research/reports/<id>/{code,notes,manuscript,artifacts}/`.**
> `artifacts/` holds `figures|tables|data|outputs`. Some reports also have root-level
> `data`/`figures`/`tables` — **these are symlinks into `artifacts/` (e.g. `data -> artifacts/data`).
> That is intentional back-compat, NOT drift. Do not flag symlinks-to-artifacts and never "move" them.**

---

## 2 · Hard guardrails for this pass

- **OneDrive perf trap.** This repo lives under OneDrive. `next build` / `next dev` (i.e.
  `reportctl.py web-build`, `web-preview`, `book-preview`, and `deliverables` which calls them)
  triggers a OneDrive+Defender+Spotlight sync storm. **Do NOT run those unless `full` mode is
  requested AND you warn first** (suggest quitting OneDrive). Python-only steps (`web-data`,
  `validate-web-data`, `summary`, `agent-sync`, `agent-pack`, `publication-pdf`) are safe.
- **Scoping contract (from AGENTS.md).** Never modify scientific code, never bulk-move/rename/delete
  report content, never run large regenerations for a doc/audit task. Auto-apply only **doc/text**
  changes that are provably correct and reversible.
- **Use the venv if present:** `PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python`. Always wrap
  `reportctl` calls in `timeout 120`. Read the *actual* dev port from stdout if you ever start the site.
- **Git:** you may stage + make a **local** commit (conventional style, e.g. `chore(repo): ...`,
  `docs: ...`) when the working tree changes are all safe unifications. **Never `git push`.** Honor
  `--no-commit`. The deprecated mirror at `~/codex-work/valley-k-small` must **not** be synced (repo
  policy: agents regenerate packs via reportctl, not a second mirror) — only note if it has diverged.
- Confirm `pwd` ends in `valley-k-small` before any write.

---

## 3 · Modes (parse `$ARGUMENTS`)

- **(no args)** → **STANDARD**: Phases 1→6. Read-only audits + *safe* unifications + light regen
  (`summary`, `agent-sync`, `web-data`, `validate-web-data`) + handoff + optional local commit.
- **`audit`** (alias `--dry-run`, `dry`) → **READ-ONLY**: Phases 1→3 + handoff. Make **zero** writes,
  zero regen, no commit. Output the findings and the *would-fix / would-surface* lists.
- **`full`** → STANDARD **plus** heavier regen: `agent-pack`, `publication-pdf`, and (only after an
  explicit OneDrive warning + go-ahead) `web-build`/`deliverables`. Run the **non-`--fast`** `audit`.
- **a token matching a report id** (check against `reportctl.py list`) → scope the deep report/structure
  checks in Phase 3 to that report; still run repo-wide harness validations.
- **`--no-commit`** anywhere → do everything except the commit.

Announce the resolved mode in one line before starting.

---

## 4 · Phase 1 — Orient

```bash
cd "<repo root>"; PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
timeout 120 $PY scripts/reportctl.py list
git status --short && git log --oneline -6
```
- Confirm root, capture the report set, capture working-tree state, note current branch.
- Skim `AGENTS.md` (the contract) and the SKILL playbook if anything is ambiguous.

## 5 · Phase 2 — Harness audit (don't reinvent; orchestrate)

Run the repo's own validators (read-only). Capture pass/fail + the tail of any failure:
```bash
timeout 120 $PY scripts/reportctl.py doctor
timeout 120 $PY scripts/reportctl.py audit            # use --fast in STANDARD; full audit in `full`
timeout 120 $PY scripts/reportctl.py validate-registry
timeout 120 $PY scripts/reportctl.py validate-archives
timeout 120 $PY scripts/reportctl.py check-docs-paths
timeout 120 $PY scripts/reportctl.py validate-science-rules
timeout 120 $PY scripts/reportctl.py translation-qc        # bilingual CN/EN QC
timeout 120 $PY scripts/reportctl.py validate-web-data      # if web payloads exist
```
A failure here that implies **scientific/data breakage** → stop and surface, do not "fix".

## 6 · Phase 3 — Consistency / unification audit (the value this command adds)

The harness validates code, TeX, registry, and referenced paths — but **not** whether the
prose governance docs agree with reality and with each other. Check each, record findings:

1. **README layout vs reality.** Parse the fenced layout tree in `README.md`; for every directory it
   lists, verify it exists on disk, and for every real top-level dir, verify it's represented.
   *(Known seed: `README.md` once listed `platform/agent/`, which does not exist — `platform/` is
   `web schemas skills tools`. Verify and fix any such stale entry.)*
2. **Guardrail sync: `CLAUDE.md` ⇄ `AGENTS.md`.** These intentionally duplicate the rule blocks
   *Mathematical Guardrails · Boundary-Condition Conventions · Plotting Rules · Testing Expectations ·
   Report Output Conventions · Conventions*. Diff them section-by-section. If they have **drifted**,
   `AGENTS.md` wins — propose bringing `CLAUDE.md` back in sync. **Do not delete** the CLAUDE.md copy
   (it is load-bearing for cold-start). Treat reconciliation as a *surfaced* decision unless the diff
   is a trivial, unambiguous text restatement.
3. **Inventory vs registry.** `research/reports/report_registry.yaml` is canonical. Confirm the report
   dirs on disk, the registry entries, and the human indexes (`research/reports/README.md`,
   `research/docs/README.md`) all name the **same** set. Missing/extra report → reconcile the human
   indexes (safe) and flag registry mismatches (surface).
4. **Summary freshness.** Compare `RESEARCH_SUMMARY.md`'s date + `AUTO-INDEX` block against the registry
   and recent commits. Stale → regenerate in Phase 5 (`summary`); never hand-edit the AUTO-INDEX.
5. **Per-report skeleton.** Each report has `code notes manuscript artifacts` (+ `README.md`).
   Root-level `data/figures/tables` that are **symlinks into `artifacts/`** are fine — ignore them.
   Only flag a *real* missing canonical subdir or a *loose `*.tex`/`*.pdf` at a report root*.
6. **Git hygiene.** Classify every uncommitted/untracked path: regenerated report artifact, new
   governance doc, or stray runtime state. Ensure `.gitignore` still covers `.venv* .local out .next
   node_modules __pycache__`. Reconcile the safe ones; surface anything ambiguous (e.g. an untracked
   `manuscript/extras/*` audit folder — is it a keeper or scratch?).
7. **CLI surface drift.** No new top-level `scripts/*.py` competing with `reportctl.py`; tools stay
   behind the CLI.

## 7 · Phase 4 — Decide & unify (you make the call)

Split every finding into two buckets and act:

- **APPLY (safe, auto):** stale doc-tree entries; index READMEs that miss/duplicate a registry report;
  obviously-broken path references; trivially-divergent duplicated text where the canonical side is
  unambiguous; refreshing generated files. All are doc/text, reversible, and touch no science.
- **SURFACE (recommend, don't apply):** CLAUDE⇄AGENTS guardrail divergence beyond trivial; any
  report-content move/rename; anything touching `packages/`, report `code/`, or kernels; deleting
  files; mirror sync; pushing. For each, give a one-line recommendation + the exact command/edit you'd
  run, and let the human decide.

When unsure which bucket → it's SURFACE. The repo's contract prefers a missed auto-fix over an
unwanted change.

## 8 · Phase 5 — Regenerate derived artifacts (skip entirely in `audit` mode)

Only if Phase 3/4 changed inventory or docs, or the summary was stale:
```bash
timeout 120 $PY scripts/reportctl.py summary          # refresh RESEARCH_SUMMARY date + AUTO-INDEX
timeout 120 $PY scripts/reportctl.py agent-sync        # refresh agent JSONL/manifest views
timeout 120 $PY scripts/reportctl.py web-data          # python-only payloads (safe under OneDrive)
timeout 120 $PY scripts/reportctl.py validate-web-data
```
`full` mode adds: `agent-pack`, `publication-pdf`, and — only after warning about the OneDrive
sync storm and getting a go-ahead — `web-build` / `deliverables`.
Re-run the relevant Phase 2 validators after regenerating, to confirm still-green.

## 9 · Phase 6 — Verify & hand off

Emit a structured report (this mirrors AGENTS.md's required end-of-run handoff):

```
## /goal run — <mode> — <branch>
### Acceptance (§0)
  1 validations … ✅/⚠️/❌   2 canonical consistency … ✅/⚠️/❌   3 summary fresh … ✅
  4 working tree intentional … ✅   5 no out-of-scope change … ✅
### Audit findings
  harness:      <pass/fail per validator, with the failing tail>
  consistency:  <each Phase-3 finding, severity>
### Unifications applied (safe)
  <file — what changed — why>
### Decisions surfaced (need a human call)
  <finding — recommendation — exact command/edit — why not auto-applied>
### Commands run        ### Generated/refreshed outputs
### Git
  <git status --short>; proposed commit: `<conventional message>` (or "committed <sha>" / "skipped: --no-commit")
### Remaining risks
```

Then, unless `audit` mode or `--no-commit`: if the working tree contains only safe unifications,
stage and make a **local** commit with a conventional message summarizing them. Never push.

---

## Quick reference — `reportctl.py` subcommands (all behind the one CLI)

`list resolve run build` · `summary cleanup` · `validate-registry validate-archives check-docs-paths
validate-science-rules audit doctor translation-qc validate-web-data` · `archive prune-legacy-artifacts`
· `web-data book-data backbone-data web-build sync-local-remote` · `agent-sync agent-pack deliverables
publication-pdf content-iterate` · `web-preview book-preview openclaw-review`
