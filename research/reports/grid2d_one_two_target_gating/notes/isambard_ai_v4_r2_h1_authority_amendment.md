# v4-r2 h1 authority amendment

This append-only amendment preserves base r2 payload
`c6c77f62d05fb17c25160723f87324654041c2de484c3f4e12b2bf92bb8af404`.
It adds content-level v3 canary reduction authorization, an implementation-
independent v4 raw/TRES replay, exact receipt contracts, and a phase-specific
submit state machine.  Base r2 receipts are not sufficient for pooling.

The h1 release is fail-closed and append-only.  It independently parses the
fixed v3 canary's exact eight completed allocations and raw JSON/NPZ pairs,
then requires an exact four-GPU canary -> 480-allocation production -> reducer
-> replay -> combined submission chain.  Pooling additionally reverse-hashes
the fixed v3/v4 evidence and rejects noncanonical, duplicate-key, extra-member,
wrong-mode, wrong-TRES, wrong-config, wrong-RNG, wrong-Slurm, or forged-receipt
inputs.  No h1 receipt may authorize work until every predecessor artifact and
receipt exists at its fixed path and passes its content-level replay.
