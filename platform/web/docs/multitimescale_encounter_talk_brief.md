# Multitimescale Encounter Talk Brief

## Objective

Build a polished interactive web talk for `valley-k-small` at:

- `/talk/multitimescale-encounter/`
- `/cn/talk/multitimescale-encounter/`

The talk should feel like a real research presentation, not a report browser. It
must keep the existing `/talk/smet-phd/` route working.

## Core Message

First-passage double peaks can be evidence for hidden route families or separated
time scales, but only after artifact mechanisms are ruled out.

The talk should move from positive examples to guardrails:

1. Ring shortcut models show how a fast branch and delayed branch can coexist.
2. Grid2D models show how geometry, targets, outside budget, and membrane
   crossing split the mechanism.
3. The latest `final_multitimescale_fpt_encounter` work is the scientific
   guardrail: the current reflecting synchronous co-location encounter model did
   not produce a robust F2 double peak. Its unusual shapes are better explained
   as parity artifacts, same-target long tails, or weak target-shift shoulders.

The ending should make the project feel upgraded from "finding double peaks" to
"building an evidence grammar for when a double peak means mechanism."

## Implementation Notes

- Reuse the existing Next.js static export app and custom `TalkRevealDeck`.
- Do not import reveal.js APIs; `TalkRevealDeck` is a custom React component.
- Add new talk data and assets instead of overwriting `smet-phd`.
- Use accepted report artifacts and summary outputs. Do not rerun raw scientific
  searches.
- Convert or redraw PDF-only evidence only when it improves slide clarity.
- Add a meaningful interactive slide, not just static images.
- Support English and Chinese routes with localized titles, slide sentences,
  toolbar labels, and presenter notes.
- Keep GitHub Pages `NEXT_PUBLIC_BASE_PATH=/valley-k-small` compatible.

## Validation Gates

Run from the repository root unless stated otherwise:

```bash
python3 scripts/reportctl.py validate-web-data
python3 scripts/reportctl.py check-docs-paths
cd platform/web && npm run build
```

Preview locally and inspect:

- `/talk/multitimescale-encounter/`
- `/cn/talk/multitimescale-encounter/`
- `/`
- `/talk/smet-phd/`

Completion requires no broken images, no base-path errors, readable desktop and
mobile layouts, and no regression of the old talk route.
