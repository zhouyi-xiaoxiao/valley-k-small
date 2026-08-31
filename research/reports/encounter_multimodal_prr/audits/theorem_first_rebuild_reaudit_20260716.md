# Theorem-first working-set rebuild re-audit

Date: 2026-07-16

Status: **DETERMINISTIC LATEX REBUILD PASS / PDF PARSE PASS / CURRENT POPPLER TOOLCHAIN HOLD / NO SCIENTIFIC PROMOTION**

## Purpose

The canonical build driver was observed waiting indefinitely while invoking
`pdfinfo`.  This re-audit distinguishes a manuscript or LaTeX failure from a
host-tool failure without changing the accepted source, compiler driver,
published PDFs or compile manifest.

## Host diagnosis

On this host `/opt/homebrew/bin/pdfinfo` resolves to Poppler 26.07.0.
`pdfinfo -v` waits before processing any PDF.  A one-second process sample
places the main thread in the macOS dynamic loader while mapping a Homebrew
dylib, blocked in `fcntl`.  The same symptom occurs before a document path is
supplied, so it is not evidence of malformed manuscript output.

No package reinstall, network access, privilege elevation, provenance removal
or accepted-driver edit was performed.  The accepted build driver remains:

```text
15098db6e731e23a31967077b79ace723849b5e8383169bb497fa57f9b92725e
```

## Independent LaTeX rebuild evidence

Four clean output directories under a fresh `/private/tmp` root were used with
the canonical environment:

```text
FORCE_SOURCE_DATE=1
LC_ALL=C
SOURCE_DATE_EPOCH=1783987200
TZ=UTC
```

The active main was built twice and the Supplemental Material was built twice
with `latexmk -pdf -g -interaction=nonstopmode -halt-on-error
-file-line-error`.  All four commands exited successfully.

| document | run 1 SHA-256 | run 2 SHA-256 | frozen published SHA-256 |
| --- | --- | --- | --- |
| main | `577d2d4b494633a3e009f13fbd581a9c889d7c84fd11c18e5b3367a6e4b1a42e` | same | same |
| Supplemental Material | `70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb` | same | same |

The four TeX logs contain none of the driver's forbidden unresolved-reference,
undefined-citation, overfull-box, multiply-defined-label, rerun, emergency-stop
or fatal-error patterns.

Ghostscript 10.04.0 parsed all four PDFs with `-dSAFER -sDEVICE=nullpage`.
An additional read-only Ghostscript inspection reports seven main pages and 23
Supplemental pages.  Every one of the 30 physical pages has MediaBox
`[0 0 612 792]` points.

## Frozen publication evidence

- active main TeX:
  `10d62404f15e306072e093aaa6fa5abbf5f6bdb0ecb42a341e3740dcf77aac2c`;
- published main PDF:
  `577d2d4b494633a3e009f13fbd581a9c889d7c84fd11c18e5b3367a6e4b1a42e`;
- published Supplemental PDF:
  `70de25968298d58222bbab10639a2253067f5c01d4d6462d743e3e6eca5790fb`;
- compile manifest:
  `704c96f173c51423457ef8b03fa8ee914ec10bedebc3e6aa435965991d34a6ea`.

## Boundary

This closes the question of whether the frozen theorem-first sources still
compile deterministically on the current TeX installation.  It does not claim
that the current Poppler installation is healthy, does not replace the
canonical full PDF audit, and does not authorize Round 170, positive-budget
evaluation, F0/F1/F3 promotion, a strict continuum theorem or submission.

## Historical-freeze regression repair

The first combined status/build regression run also exposed three assertions
in the Round-166/167 freeze tests that still treated living manuscript,
continuum-contract and compile-manifest paths as immutable current bytes.  In
particular, one assertion required the superseded six-page/22-page working set
even though the accepted C0-A migration freezes seven plus 23 pages.

The tests were migrated to the already established Round-165 convention:
stage-specific files and immutable audit files remain byte-frozen, while
superseded living-file hashes must remain present in their immutable historical
audit instead of matching the current path.  No historical audit was edited.
The combined compile/status/freeze regression then passed 29/29 tests.
