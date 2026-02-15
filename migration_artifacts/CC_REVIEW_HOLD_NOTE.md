# CC Review Hold Note

Generated on: 2026-02-15

These artifacts are ready for review, but **do not apply migration patches/adapters yet**.

Hold condition:
- Wait until Sprint `0.1` through Sprint `0.3` are merged.

Reason:
- Pending directory/layout and import-path changes in those sprints can invalidate direct patch application paths.

Approved interim use:
- Review mapping tables, lossy conversion flags, and unmapped value flags.
- Validate adapter semantics against canonical contract:
  - `contracts/vocab/canonical_enums.json`
