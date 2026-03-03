# PDF Acquisition: Streamlined Process Design

**Problem**: Getting PDFs is the #1 human labor bottleneck. The current process is fragmented across 6+ tools and scripts, with too many manual steps and no single funnel.

**Goal**: Minimize human clicks to get PDFs from "AG says get these" to "PDFs are in `data/pdfs/`".

---

## Current Tools Inventory

| Tool | What It Does | License Status | Currently Working? |
|------|-------------|---------------|-------------------|
| **Unpaywall** | Free OA PDFs via API | Free (email-based) | ✅ Script exists (`acquire_pdfs_unpaywall.py`) |
| **Zotero** | Reference manager + PDF finder | Free (+ UCSD proxy) | ⚠️ Not reliably finding PDFs |
| **Elicit** | AI research assistant, finds papers | User subscribes | ❌ Not integrated |
| **Scite** | Citation analysis, paper discovery | User subscribes | ❌ Not integrated |
| **Consensus** | AI search over papers (ChatGPT plugin) | Via ChatGPT | ❌ Not integrated |
| **Scholar AI** | Academic search (ChatGPT plugin) | Via ChatGPT | ❌ Not integrated |
| **Google Scholar** | Paper search + some PDFs | Free | Manual only |
| **UCSD Library** | Full institutional access | Via proxy | Manual via browser |

---

## Proposed 3-Tier Acquisition Funnel

### Tier A: Automated (Zero Human Effort)

**Who does it**: AG or Claude via scripts

1. AG generates a `data/acquisition/wanted_papers.json` with DOIs and priority
2. Run `acquire_pdfs_unpaywall.py` → auto-downloads all open-access PDFs (~40-60% hit rate)
3. Run `scripts/acquire_pdfs_semantic_scholar.py` (TO BUILD) → checks S2 for open PDFs
4. Run `scripts/acquire_pdfs_crossref.py` (TO BUILD) → checks CrossRef for deposit links

**Expected yield**: ~50-60% of papers for free, zero human effort.

### Tier B: Semi-Automated (Minimal Human Effort — 2 min per batch)

**Who does it**: David, once per batch

**Option B1 — Elicit Batch (RECOMMENDED)**
1. AG generates a prompt file: `data/acquisition/elicit_search_queries.txt`
2. David pastes batch of DOIs into Elicit → Elicit finds papers + PDFs
3. David downloads PDFs from Elicit to `data/pdfs_incoming/`
4. AG runs extraction pipeline on incoming dir

**Option B2 — ChatGPT + Scholar AI / Consensus**
1. AG generates a ChatGPT prompt with DOIs and asks Scholar AI to find PDFs
2. David pastes prompt into ChatGPT → gets download links
3. David downloads to `data/pdfs_incoming/`

**Option B3 — Zotero + UCSD Proxy (for paywalled papers)**
1. AG generates RIS file (already implemented: `export_ris()`)
2. David imports RIS into Zotero with UCSD proxy active
3. Zotero auto-fetches PDFs via institutional access
4. David exports PDFs from Zotero's storage to `data/pdfs_incoming/`

> **Why Zotero isn't working**: Likely cause is that the UCSD proxy isn't configured in Zotero preferences, OR Zotero's "Find Available PDF" doesn't use the proxy for all publishers. The fix is to install the Zotero browser connector, sign into UCSD Library in the browser, and use "Save to Zotero" from the browser while on the publisher page. This bypasses Zotero's internal PDF finder.

### Tier C: Manual (5 min per paper — last resort)

**Who does it**: David

For paywalled papers that Tier A and B couldn't get:
1. Go to UCSD Library EZProxy: `https://login.ezproxy.library.ucsd.edu/`
2. Search for the paper
3. Download PDF
4. Drop in `data/pdfs_incoming/`

---

## The Single Funnel: `data/pdfs_incoming/`

**The critical process simplification**: Create ONE directory where you dump PDFs from ANY source.

```
data/pdfs_incoming/        ← David drops PDFs here from Zotero, Elicit, manual
data/pdfs/                  ← Processed PDFs (renamed by DOI)
data/pdfs_incoming/.gitkeep ← So the dir exists in git
```

A watcher script processes incoming PDFs:
```bash
python scripts/process_incoming_pdfs.py
# 1. Identifies each PDF (by filename or DOI lookup)
# 2. Renames to DOI-based filename
# 3. Moves to data/pdfs/
# 4. Triggers extraction pipeline
# 5. Updates acquisition status
```

This means David's ONLY job is: **drop PDFs in `data/pdfs_incoming/`**. Everything else is automated.

---

## Optimizing Each Tool

### Elicit (most promising for batch)
Elicit can search by:- DOI → direct paper lookup- Keywords → finds related papers- "Find similar to" → discovers papers we don't know about

**Best use**: Batch paste 20 DOIs → Elicit collects them → download as ZIP → drop in incoming.

### Scite (best for citation-aware discovery)
Scite shows whether papers are "supporting," "contrasting," or "mentioning" citations. 
**Best use**: For the 53 foundational papers — enter each DOI and check what scite says about citing papers. This could discover new empirical papers we should add to the corpus.

### Consensus (best for specific questions)
**Best use**: Ask domain questions ("What studies show CCT affects alertness?") and get papers with direct evidence links. Not good for batch DOI lookup.

### Scholar AI (best for obscure/older papers)
**Best use**: Finding PDFs of older foundational papers (Berlyne 1971, Appleton 1975, Gibson 1979) that may be in university repositories.

---

## Proposed Zotero Setup Fix

The likely reason Zotero isn't finding PDFs:

1. **UCSD proxy not configured**: In Zotero → Edit → Preferences → Advanced → Config Editor, search `extensions.zotero.proxies.proxies` and add:
   ```
   https://login.ezproxy.library.ucsd.edu/login?url=%u
   ```

2. **Alternative (more reliable)**: Use the Zotero browser connector:
   - Install Zotero Connector extension in Chrome/Firefox
   - Log into UCSD Library in the browser
   - Navigate to paper on publisher site → click Zotero Connector → saves with PDF

3. **Create a dedicated AE collection in Zotero**:
   - Zotero desktop → New Collection → "Article_Eater"
   - All AE papers go here
   - Can export entire collection's PDFs at once

---

## Can AG Access Zotero Directly?

**Not currently.** But there are two options:

### Option A: Zotero WebDAV/Cloud Sync (EASIEST)
If David enables Zotero cloud storage (free 300MB, or paid for more):
- Zotero syncs PDFs to `zotero.org`
- AG could potentially access via Zotero API (requires API key)
- We already have `zotero_push.py` that writes TO Zotero
- We'd need a `zotero_pull.py` that reads FROM Zotero

### Option B: Shared Local Directory (SIMPLEST)
David creates `data/pdfs_incoming/` and just drops files there. AG sees them immediately (same filesystem). **This is the simplest and most reliable approach.**

### Option C: Zotero Group Library (COLLABORATIVE)
Create a Zotero Group Library that both David and the system can access via API. This is the most "proper" but requires Zotero storage subscription for PDF sync.

**Recommendation**: Start with **Option B** (shared local dir) because it works TODAY with zero setup. Consider Option A later if the volume justifies it.

---

## Immediate Action Plan

### What AG does NOW:
1. Create `data/pdfs_incoming/` directory with `.gitkeep`
2. Generate `data/acquisition/wanted_papers.json` for the 53 foundational papers
3. Run Unpaywall on those 53 DOIs → get the open-access ones automatically
4. Generate Elicit/ChatGPT prompt files for the remaining paywalled ones
5. Generate RIS for Zotero import of the remainder

### What David does (5-10 min):
1. Fix Zotero UCSD proxy (one-time)
2. Import the generated RIS into Zotero
3. For papers Zotero misses, paste batch into Elicit
4. Drop all PDFs into `data/pdfs_incoming/`

### What AG does AFTER:
1. Process incoming PDFs
2. Run extraction pipeline
3. Update acquisition status
4. Report results
