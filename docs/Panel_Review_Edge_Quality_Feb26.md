# Expert Panel Review: Quality Assessment of 1,731 Keyword-Bridge Edges

## Panel Composition

This review convenes nine experts whose competences span the epistemic warrant chain from formal argumentation to practical knowledge engineering:

| Panelist | Role | Domain Competence |
|----------|------|-------------------|
| **Susan Haack** (Chair) | Foundherentist Epistemologist | Whether keyword-based bridges meet the standard for epistemic warrant |
| **Judea Pearl** | Causal Inference | Whether "explains" edges create causal claims not supported by evidence |
| **Nancy Cartwright** | External Validity | Whether bridges create false scope generalisations |
| **Paul Thagard** | Coherence Theory | Impact on web coherence metrics — do noisy edges help or hurt? |
| **Henry Prakken** | Argumentation Theory | Whether the 5 contradiction edges meet formal standards for "contradicts" |
| **Roger Cooke** | Structured Expert Judgement | Calibration of edge strength (is 0.3 appropriate?) |
| **Butler Lampson** | Systems Engineering | Whether the script's matching algorithm has well-documented failure modes |
| **Phan Minh Dung** | Abstract Argumentation | Impact on the grounded extension and defeat semantics |
| **Deborah Mayo** | Severe Testing | Whether this process has been probed for ways it could fail |

---

## I. THE EVIDENCE BEFORE THE PANEL

### A. Script Architecture

The `safe_improve_web_health.py` script generates edges through two strategies:

**Strategy 1: Template Keyword Bridge (1,726 edges).** For each isolated belief (no constraint edges), the script:
1. Tokenises the belief content into lowercase substrings
2. Matches substrings against a keyword index built from template constructs, T1 framework IDs, template name tokens (>4 chars), and mechanism chain description tokens (>6 chars)
3. If a match is found, creates an "explains" edge (strength 0.3) from the isolated belief to the first already-connected belief that also matches the same template keyword
4. Only the first template match is used; the process stops after one edge per isolated belief

**Strategy 3: Contradiction Discovery (5 edges).** Parses belief content for `"environment -> outcome (direction)"` patterns and flags pairs that assert opposite directions on the same environment→outcome pair.

### B. Keyword Index Analysis

The keyword index contains **2,260 entries** built from **~200 templates**. Critical findings:

**Problem 1: T1 Framework Abbreviations as Substrings.**
The T1 framework IDs (PP, NM, IC, DT, SN, MS, EC, CB) are entered into the keyword index as lowercase 2-character strings. Because the matching uses Python's `in` operator (substring containment, not word boundary), these create massive false-positive rates:

| Keyword | Templates Matched | Example False Positives |
|---------|------------------|----------------------|
| "pp" | 110 | "ha**pp**iness", "su**pp**ort", "a**pp**lied", "sto**pp**ing" |
| "nm" | 58 | "enviro**nm**ent", "gover**nm**ent", "enrich**nm**ent" |
| "ic" | 46 | "publ**ic**", "mus**ic**", "acoust**ic**", "specif**ic**" |
| "dt" | 24 | "wi**dt**h", "ban**dt**" |
| "sn" | 23 | "res**sn**ap" (rare, but "SN" commonly starts sentences in some templates) |
| "ms" | 22 | "ar**ms**", "for**ms**", "syste**ms**" |
| "ec" | 20 | "eff**ec**t", "dir**ec**tion", "conn**ec**tion", "s**ec**tion" |
| "cb" | 12 | "feedba**cb**" — rare, but still noise |

**Estimated impact**: The keyword "pp" alone could match virtually every belief in the web (most scientific text contains words with "pp"). This means edges routed through "pp" carry zero epistemic signal — they are random pairings of beliefs that happen to contain common English digraphs.

**Problem 2: Generic English Words.**
Mechanism chain description tokens > 6 characters include generic words that match many templates but carry no domain-specific meaning:

| Keyword | Templates Matched | Epistemic Content |
|---------|------------------|-------------------|
| "environmental" | 43 | Generic — nearly every template involves an environmental variable |
| "response" | 34 | Generic — meaningless without specifying *what* response |
| "processing" | 33 | Semi-generic — cognitive processing, but what kind? |
| "generates" | 16 | Generic verb |
| "without" | 12 | Stopword-level |
| "between" | 12 | Stopword-level |

**Problem 3: Over-Matching from Short Template Name Tokens.**
Template name tokens > 4 characters include semi-generic domain words:

| Keyword | Templates Matched | Issue |
|---------|------------------|-------|
| "spatial" | 41 | Too broad — nearly all architectural templates are "spatial" |
| "acoustic" | 20 | Reasonable domain term but very broad |
| "error" | 16 | Could mean prediction error, measurement error, or human error |

**Problem 4: First-Match Selection.**
When an isolated belief matches a template, the script selects `targets[0]` — the first already-connected belief that also matches that template keyword. This is not ranked by semantic relevance, keyword specificity, construct overlap, or any other quality criterion. The first belief in the list is determined by database insertion order, which has no epistemic significance.

---

## II. PANEL DELIBERATION

### Opening Statement (Haack, Chair)

> The question before us is not whether connecting orphaned beliefs to the web is a good idea — it plainly is — but whether these *specific* connections meet the standard for epistemic warrant. An "explains" edge, even at strength 0.3, asserts that one belief is *explanatorily relevant* to another. A connection based on the substring "pp" appearing in both beliefs does not assert this. It asserts only that both beliefs contain a common English digraph. The distinction between epistemic warrant and statistical noise is precisely the distinction that the web of belief system is designed to uphold.

### Causal Semantics (Pearl)

> An "explains" edge in a coherentist web is not a causal claim in the technical sense, but it does assert *inferential relevance* — that learning about one belief should update your credence in the other. Substring matching cannot establish inferential relevance. The word "happiness" sharing "pp" with "Predictive Processing" creates a link between a psychological outcome and a neural framework, but the link carries no directional, mechanistic, or evidential information. Worse: in a web where credence propagates through edges, noisy edges do not merely fail to help — they *actively degrade* the signal. If belief A (high credence, well-supported) is connected to belief B (low credence, poorly supported) via a noise edge, A's credence will pull B upward and B's uncertainty will pull A downward. The net effect is **entropy injection**: the overall web becomes more uncertain, not more coherent.

### Coherence Impact (Thagard)

> I want to quantify Pearl's concern. In my coherence theory (Thagard, 2000), coherence is the ratio of satisfied to total constraints. Adding 1,726 edges, most of which are noise, will increase the denominator (total constraints) dramatically while adding very few genuinely satisfied constraints to the numerator. The coherence score will almost certainly *decrease*, not increase. The orphan rate will drop — because orphans are defined as beliefs with no edges — but the coherence of the non-orphan web will degrade.
>
> This is a well-known trap in network analysis: optimising for connectivity (reducing orphans) while ignoring edge quality reduces the information content of the network. The AESHI improvement from 49 to 53-55 is driven entirely by the orphan metric. If the health scoring also measures coherence (and it should), the coherence component will likely decrease, partially or fully offsetting the orphan improvement.

### Scope Concerns (Cartwright)

> Many of these bridges will connect beliefs tested in specific contexts to beliefs about different contexts — because the keyword match is context-blind. A belief about "ceiling height in creative workspaces" might be bridged to a belief about "acoustic privacy in healthcare settings" because both match the keyword "spatial." This creates false scope generalisations: the web would now assert that these beliefs are explanatorily related, when in fact they concern different populations, different environments, and different outcomes. This is precisely the overgeneralisation that the scope distance computation in the credibility testing framework (§134) is designed to prevent.

### Severe Testing (Mayo)

> Has this script been probed for ways it could fail? The dry-run mode tells you *how many* edges it would add, but not *how many of those edges are warranted*. A proper severe test would be: sample 100 edges, have a domain expert classify each as WARRANTED, MARGINAL, or NOISE, and compute the precision. If the precision is below, say, 50%, the script is adding more noise than signal. I strongly suspect the precision would be 10–20% given the substring matching on 2-character abbreviations.

### Edge Strength Calibration (Cooke)

> The uniform strength of 0.3 is a calibration error. Even if we accept that some keyword bridges are genuine, the strength should vary with keyword specificity. A bridge through "circadian" (a precise scientific term matching 7 templates) should be stronger than a bridge through "spatial" (a generic architectural term matching 41 templates). The inverse document frequency (IDF) of the keyword in the template corpus is a reasonable prior for strength. Setting everything to 0.3 treats a precise mechanistic connection and a random substring match as equally informative.

### Argumentation Semantics (Prakken, Dung)

> The 5 contradiction edges from Strategy 3 are methodologically sounder. They use structured pattern matching (environment→outcome direction parsing), not substring matching, and they assert a specific, falsifiable relationship (these beliefs explicitly disagree on the direction of an effect). These edges should be accepted.
>
> However, for the 1,726 template bridges, I note that once added, these edges become part of the argumentation graph and affect the grounded extension. Noisy edges can shift the grounded extension by creating spurious support paths that shield weak beliefs from defeat. This is an underappreciated risk: adding "defensive noise" around poorly-supported beliefs makes them harder to dislodge even when legitimate attacks are mounted.

### Systems Engineering (Lampson)

> The script has a well-documented architecture and clear provenance tagging (each edge records `safe_template_bridge:{template_id}`), which enables rollback. This is good engineering practice. However, the failure modes are not documented. The script does not log or report *which keywords* triggered each edge, making post-hoc quality assessment expensive. I recommend adding keyword-level provenance: `safe_template_bridge:{template_id}:{keyword}` so that edges triggered by known-bad keywords (pp, nm, ic, etc.) can be identified and removed in bulk.

---

## III. PANEL RECOMMENDATIONS

### Unanimous Consensus (9/9)

**1. Do NOT run the script as-is. The substring matching on 2-character T1 framework abbreviations (pp, nm, ic, dt, sn, ms, ec, cb) is a critical defect that would inject noise into the web.** These 8 keywords collectively match 315 template entries and would trigger false-positive edges for essentially any belief containing common English words. This is not an edge case — it is the dominant failure mode.

**2. The 5 contradiction edges (Strategy 3) are acceptable.** Approve these for insertion. They use structured pattern matching with explicit direction parsing, not substring matching.

### Supermajority Consensus (8/9, Cooke abstains)

**3. The template-bridge strategy (Strategy 1) is salvageable with five specific fixes:**

| Fix | Description | Expected Effect |
|-----|-------------|-----------------|
| **Fix A: Exclude 2-char keywords** | Skip all T1 framework abbreviations from the keyword index. They are too short and match too many templates. | Eliminates ~315 of the ~2,260 keyword entries (the most promiscuous ones) |
| **Fix B: Whole-word matching** | Replace `if kw in content_lower` with word-boundary matching (`re.search(r'\b' + re.escape(kw) + r'\b', content_lower)`). This prevents "happiness" from matching "pp". | Eliminates virtually all substring false positives |
| **Fix C: Exclude stopword-level keywords** | Add a blocklist for generic terms: "without", "between", "generates", "through", "response", "features", "signals", "channel", "environmental". | Eliminates ~10–15 more noise sources |
| **Fix D: Minimum keyword length ≥ 5 for mechanism chain tokens** | Change the threshold from >6 to ≥8 for mechanism chain tokens, or better yet, use an explicit construct vocabulary rather than tokenising descriptions. | Removes short generic words from mechanism descriptions |
| **Fix E: IDF-weighted strength** | Set edge strength proportional to keyword specificity: `strength = min(0.5, 0.3 * (1 / len(matched_templates)))` so edges through "circadian" (7 templates, strength ≈ 0.30) are stronger than edges through "spatial" (41 templates, strength ≈ 0.007). | Downgrades noisy edges and upgrades precise ones |

### Split Vote (5/4)

**4. After applying Fixes A–E, recount the predicted edges.**

- **Majority (Haack, Pearl, Cartwright, Mayo, Dung)**: Predict the edge count will drop from 1,726 to 300–500 high-quality edges. Recommend running the fixed script and accepting the smaller but cleaner set.
- **Minority (Thagard, Prakken, Cooke, Lampson)**: Recommend a further manual review of 50 edges from the fixed output before bulk insertion. Even after fixing the worst matching defects, keyword bridges are inherently heuristic and should be validated.

### Unanimous Recommendation on Process (9/9)

**5. Add keyword-level provenance.** Change the provenance string from `safe_template_bridge:{template_id}` to `safe_template_bridge:{template_id}:{keyword}` so that if a keyword is later found to be noisy, all edges triggered by that keyword can be identified and removed in O(1) time.

**6. Post-insertion coherence check.** After inserting the cleaned edges, run the coherence metric (Algorithm 3 from §129) and compare against the pre-insertion baseline. If coherence *decreases* despite the orphan reduction, the edges are harming the web and should be rolled back.

---

## IV. EXPECTED OUTCOME AFTER FIXES

| Metric | Before | After (as-is script) | After (fixed script) |
|--------|--------|---------------------|---------------------|
| Total edges | ~1,731 | ~1,731 | ~300–500 (estimated) |
| Estimated precision | — | 10–20% | 60–80% |
| Orphan rate | 49.6% | ~25% | ~35–40% |
| AESHI | 49 | 53–55 | 51–53 |
| Coherence | Baseline | Likely decreases | Likely stable or slightly increases |

The fixed script will produce a smaller AESHI improvement but a *genuine* one — fewer orphans will be connected, but those connections will be epistemically warranted. The as-is script would produce a numerically larger improvement that masks web degradation.

---

## V. IMPLEMENTATION GUIDANCE

The five fixes (A–E) should be applied to `scripts/safe_improve_web_health.py` before running. The changes are localised to two functions:

1. **`build_template_keyword_index()`**: Apply Fixes A, C, D (filter keywords by length, exclude blocklist)
2. **`strategy_template_bridge()`**: Apply Fixes B, E (whole-word matching, IDF-weighted strength)

Estimated development time: 30–60 minutes. No changes to data structures, database schema, or other modules required.

---

*Panel convened: February 26, 2026*
*Prepared by Claude (Antigravity) for David Kirsh*
*Status: UNANIMOUS on recommendations 1, 2, 5, 6. SUPERMAJORITY on 3. SPLIT on 4.*
