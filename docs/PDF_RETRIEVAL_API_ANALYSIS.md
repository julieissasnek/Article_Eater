# PDF Retrieval: API Analysis & Why AG Struggles

**Date**: 2026-03-02  
**Context**: User reports AG's PDF retrieval has been disappointing; wants to know what APIs to add and how to use Academia.edu subscription  

---

## Part 1: Why AG's PDF Retrieval Is Disappointing

### The Honest Diagnosis

AG (Antigravity) runs in a **sandboxed environment** with significant constraints:

| Constraint | Impact |
|-----------|--------|
| **Sandbox network restrictions** | Cannot make outbound HTTP requests to arbitrary URLs; `requests.get()` fails silently or gets blocked |
| **No browser automation** | Cannot log into UCSD Library, Academia.edu, or any authenticated service |
| **No persistent cookies/sessions** | Even if AG could access a site once, can't maintain login state |
| **File download limits** | PDF downloads via `read_url_content` or similar tools strip binary content |
| **Rate limiting by publishers** | Elsevier, Wiley, Taylor & Francis block non-browser user agents |

**The real bottleneck**: AG can find DOIs, build queries, and generate prompts, but **cannot actually download PDFs from most publisher websites**. This is by design (publisher paywalls) and by environment (sandbox restrictions).

### What AG CAN Do
- ✅ Query metadata APIs (Unpaywall, OpenAlex, CrossRef, S2, PubMed) → find WHERE PDFs are
- ✅ Generate acquisition lists, prompts, RIS files → tell David exactly what to get
- ✅ Process PDFs once they're in `data/pdfs_incoming/` → extract and integrate
- ❌ Actually download paywalled PDFs
- ❌ Log into institutional proxies
- ❌ Access authenticated services (Academia.edu, Elicit, Scite)

### How to Fix This

The fix is **not making AG better at downloading** — it's **making the workflow give AG less to download**. The strategy should be:

1. **Maximize automated OA retrieval** (Unpaywall + CORE + OpenAlex) → ~50-60% free
2. **Make David's manual effort as efficient as possible** (batch operations, single drop dir)
3. **Use David's paid subscriptions strategically** (Elicit for batch, Academia for rare papers)

---

## Part 2: Your Current APIs — Are They Being Used?

| API | Key Status | Currently Used By | Working? |
|-----|-----------|-------------------|----------|
| **Semantic Scholar** | ✅ Key provided | `paper_fetcher.py`, `semantic_scholar_enrichment.py` | ⚠️ Metadata only — S2 rarely has full PDFs |
| **PubMed** | ✅ Key provided | `paper_fetcher.py` | ⚠️ Metadata only — links to publisher, not PDFs |
| **CrossRef** | ✅ Polite pool (mailto) | `semantic_scholar_enrichment.py` | ⚠️ Metadata only — no PDFs |
| **Unpaywall** | ✅ Free (email-based) | `acquire_pdfs_unpaywall.py` | ✅ Actual PDF URLs for OA papers |

**Key finding**: 3 of 4 APIs give metadata only. Only Unpaywall gives actual PDF download links, and only for open-access papers.

---

## Part 3: APIs You SHOULD Add

### Tier 1: Free, High-Value (add immediately)

#### 1. OpenAlex API (FREE, no key needed)
- **What**: 250M+ works, all metadata + OA status + PDF URLs
- **Replaces/augments**: CrossRef + Unpaywall combined
- **Endpoint**: `https://api.openalex.org/works?filter=doi:{DOI}`
- **PDF access**: Returns `open_access.oa_url` with direct PDF links for OA papers
- **I just tested it** — it works and returns structured JSON with OA status
- **Rate limit**: 10 req/sec with polite pool (add `mailto:dkirsh@ucsd.edu` to headers)

#### 2. CORE API (FREE with registration)
- **What**: 37M full texts from institutional repositories worldwide
- **Key advantage**: Has full texts that publishers paywall — because it indexes *repository* copies (preprints, author manuscripts, green OA)
- **Endpoint**: `https://api.core.ac.uk/v3/`
- **This is the #1 source we're NOT using.** CORE often has PDFs that Unpaywall misses because it indexes university repositories directly.
- **Register**: `https://core.ac.uk/services/api`

#### 3. PubMed Central (PMC) Open Access (FREE)
- **What**: 8M+ open-access biomedical full texts
- **Many lighting/circadian and health papers will be here** — NIH mandates public access
- **Endpoint**: `https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{id}`
- **Returns**: Direct full-text XML or PDF links

### Tier 2: Paid/Subscription, Worth It

#### 4. Elicit API (PAID — you already subscribe)
- **What**: AI research assistant with paper discovery
- **Best use**: NOT as an API — use the web UI for batch DOI lookup
- **Workflow**: Paste 20 DOIs → Elicit shows them → bulk download PDFs → drop in incoming
- **Elicit does NOT have a public API** as of 2025, but their web UI supports batch operations

#### 5. Scite API (PAID — you already subscribe)
- **What**: Citation context analysis ("supports"/"contrasts"/"mentions")
- **Has API**: `https://api.scite.ai/` — can query by DOI
- **Best use for us**: After we have papers, query scite to find supporting/contrasting papers we DON'T have → corpus expansion
- **PDF access**: No — scite is metadata/context only

### Tier 3: Special Cases

#### 6. Internet Archive Scholar
- **What**: 25M+ papers from web archives
- **Free, no API key needed**: `https://scholar.archive.org/`
- **Has old/rare papers** that aren't on other platforms
- **Good for**: Berlyne 1971, Appleton 1975, and other foundational books/papers

#### 7. BASE (Bielefeld Academic Search Engine)
- **What**: 300M+ documents from 10K+ repositories
- **Free API**: `https://api.base-search.net/cgi-bin/BaseHttpSearchInterface.fcgi`
- **Useful for**: Finding repository copies of papers when publisher version is paywalled

---

## Part 4: Academia.edu Analysis

### Does Academia.edu Have an API?

**No public API.** I checked — `academia.edu/api` returns 404. Their developer API was deprecated years ago.

### What Academia.edu IS Good For

Academia.edu is a **social network for researchers** where authors self-upload papers. Key facts:
- Authors upload full-text PDFs voluntarily
- Many paywalled papers have author-uploaded copies here
- The "premium" subscription gives you unlimited downloads

### How to Use Your Academia.edu Subscription

**Manual but effective workflow:**

1. AG generates a search query list for Academia.edu:
   ```
   "Kaplan attention restoration theory" site:academia.edu
   "prospect refuge Appleton architecture" site:academia.edu
   ```
2. David searches on Academia.edu, downloads PDFs
3. Drops in `data/pdfs_incoming/`

**Alternative — bulk approach:**
1. Search Academia.edu for author names from our reading list (Kaplan, Ulrich, Appleton, etc.)
2. Many foundational authors have uploaded their own papers there
3. Download their uploaded papers in bulk

### Can We Scrape Academia.edu?

Technically possible but against their ToS and they actively block scrapers. **Don't recommend.** The manual search + download is fine for 53 papers.

---

## Part 5: Recommended API Stack

Here's what your complete API stack should look like:

| # | API | Purpose | Cost | Priority |
|---|-----|---------|------|----------|
| 1 | **Unpaywall** | OA PDF URLs | Free | ✅ Have it |
| 2 | **Semantic Scholar** | Metadata + citations | Free | ✅ Have it |
| 3 | **PubMed** | Biomedical metadata | Free | ✅ Have it |
| 4 | **CrossRef** | DOI resolution | Free | ✅ Have it |
| 5 | **OpenAlex** | OA status + PDF URLs | Free | 🔥 ADD NOW |
| 6 | **CORE** | Repository full texts (37M) | Free | 🔥 ADD NOW |
| 7 | **PMC OA** | Biomedical full texts | Free | 🔥 ADD NOW |
| 8 | **Internet Archive Scholar** | Old/rare papers | Free | ADD |
| 9 | **BASE** | Repository search | Free | ADD |
| 10 | **Elicit** | AI paper search | Subscribed | Use web UI |
| 11 | **Scite** | Citation context | Subscribed | Use for discovery |
| 12 | **Academia.edu** | Author-uploaded PDFs | Subscribed | Manual search |

### What This Stack Gets You

Running all free APIs before asking David for anything:

```
DOI → Unpaywall (OA PDFs)
    → OpenAlex (OA status, PDF URLs)
    → CORE (repository full texts — THIS IS THE BIG ONE)
    → PMC (biomedical full texts)
    → Internet Archive (old/rare)
    → BASE (repository search)
```

**Expected automated yield**: ~65-75% of papers (up from ~50-60% with Unpaywall alone). CORE is the game-changer — it has repository copies of papers that publishers paywall.

The remaining ~25-35% go to David's "batch paste" workflow with Elicit + Academia.edu.

---

## Part 6: Better PDF Retrieval Methods

### What the Best Systems Do

The academic community has converged on a "cascade" approach:

```
1. Check if DOI has OA version (Unpaywall/OpenAlex)
2. Check institutional repositories (CORE)
3. Check PubMed Central (PMC)
4. Check preprint servers (arXiv, bioRxiv, PsyArXiv)
5. Check author pages (Academia, ResearchGate)
6. Last resort: institutional proxy (UCSD Library)
```

### Preprint Servers We Should Check

For our domain (environmental psychology, neuroscience, architecture):
- **PsyArXiv**: Psychology preprints — `https://psyarxiv.com/` (via OSF API)
- **bioRxiv**: Neuroscience preprints — `https://api.biorxiv.org/`
- **SSRN**: Social science — `https://papers.ssrn.com/`
- **OSF Preprints**: Umbrella preprint server — `https://api.osf.io/v2/preprints/`

### The "Green OA" Insight

Many paywalled papers have a "green open access" version — the author's accepted manuscript deposited in their university repository. This is:
- **Legal** (most publisher contracts allow it after embargo period)
- **Identical content** to the published version (minus formatting)
- **Findable via CORE** (which indexes 14K+ repositories)

This is why CORE is the biggest gap in our current stack. It finds papers that Unpaywall marks as "closed" because it looks in repositories, not just publisher sites.
