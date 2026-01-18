
# Article Eater v20.7.14 — BN Playground (Admin UI)

## Overview

This sprint adds a small **BN Playground** pane to the Admin GUI that
lets you:

- load a BN export JSON produced by the RuleGraph v2 tab;
- send it to a new backend endpoint that reuses the same helpers as
  `bn_suggest_outcome_templates.py`;
- see a compact, text-only summary of:
  - outcome family distribution; and
  - the most common subject-parent type patterns.

This keeps the GUI lightweight but gives Admins a quick way to sanity
check whether the subject typing and heterogeneity structure "looks
right" before handing the export off to BN-Maker.
