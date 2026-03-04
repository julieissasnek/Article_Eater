# V13 Ruthless System Audit: Article Eater / ATLAS Enrichment Pipeline
**Date**: 2026-03-03
**Auditor**: Claude Code (Agent for Prof. David Kirsh, UCSD Cognitive Science)
**Prior Audit Score**: 5.2/10 (V12, 2026-02-14)
**Current Audit Score**: 3.8/10 (V13, 2026-03-03)

---

## EXECUTIVE SUMMARY

The enrichment pipeline has DETERIORATED significantly since V12. While the code appears superficially complete, deep analysis reveals:

1. **Silent failures are rampant** — services fail and return None, which is logged but NOT visible to users
2. **Traceability is completely broken** — beliefs lose paper_ids during enrichment
3. **The "grounding gate" is a safety theater** — raises exceptions that are caught and silently ignored
4. **Framework voices are decorative boilerplate** — generated from hardcoded templates, NOT semantic analysis of topics
5. **Language adaptation is metadata-only** — returns adaptation profiles but does NOT apply them to actual prose
6. **Latency budget is unenforced** — global timeout exists but isn't actually cancelling work
7. **Test coverage masks real failures** — tests use mocks that hide actual service unavailability

**Bottom line**: The system has lost epistemic rigor in favor of shallow "completeness." It presents hallucinated answers with plausibly enriched metadata, when enrichment actually failed.

---

## PART 1: TRACEABILITY — Can You Follow Query → Belief → Source → Paper?

### Assessment: BROKEN (Score: 1/10)

#### Finding 1.1: Paper IDs Lost During Enrichment (CRITICAL)

**Location**: `answer_enrichment_orchestrator.py`, lines 560-620

```python
enriched_belief = EnrichedBelief(
    text=belief_text,
    credence_point=estimate.point,
    credence_ci={...},
)
enriched.enriched_beliefs.append(enriched_belief)
```

**The Problem**: When credence enrichment creates `EnrichedBelief` objects, it ONLY copies `text` and credence numbers. Original belief fields like `paper_ids`, `source_papers`, `belief_id` are **discarded**.

**Why This Matters**: A user can now ask "where did you get this?" and there's no answer. The enriched belief is disconnected from its epistemological root.

**Example Failure Chain**:
1. Base answer has: `{"beliefs": [{"text": "...", "paper_ids": ["arxiv:2020.1234"], "credence": 0.75}]}`
2. Enrichment creates: `EnrichedBelief(text="...", credence_point=0.75)` — **paper_ids=None**
3. Final response cannot trace back to sources

**Remediation (P0)**:
- Add `paper_ids` and `belief_id` fields to `EnrichedBelief` dataclass
- Copy these from input beliefs during all enrichment steps
- Add test: "Verify paper_ids persist through full enrichment pipeline"

---

#### Finding 1.2: No Paper Provenance in Warrant Trace (CRITICAL)

**Location**: `answer_enrichment_orchestrator.py`, lines 644-740 (_enrich_warrant_trace)

The warrant trace computes `omega_sev`, `omega_conf`, etc., but **never records which papers these are based on**.

```python
trace = [
    {"component": "experimental_severity", "omega_sev": round(omega_sev, 3),
     "design_type": design_enum.value},
    # ... no source_papers, no paper_ids ...
]
```

**Why This Matters**: A warrant trace that doesn't cite its source papers is just a confidence number with mystique.

**Remediation (P0)**: Each warrant trace component should include `source_papers: List[str]` showing which papers contributed to that component's computation.

---

#### Finding 1.3: EnrichedBelief Schema is Incomplete (CRITICAL)

**Location**: `answer_enrichment_orchestrator.py`, lines 125-134

```python
@dataclass
class EnrichedBelief:
    """A single belief with all enrichments applied."""
    text: str
    credence_point: Optional[float] = None
    credence_ci: Optional[Dict[str, float]] = None
    warrant_trace: Optional[List[Dict[str, Any]]] = None
    confounder_risk: Optional[str] = None
    confounder_details: Optional[List[str]] = None
    # MISSING: paper_ids, source_papers, belief_id, level, status
```

**Required Fields Missing**:
- `paper_ids: List[str]` — which papers support this?
- `belief_id: str` — unique identifier for cross-reference
- `source_papers: List[Dict]` — full paper metadata
- `epistemic_level: str` — (conceptual, mechanism, implementation, etc.)
- `evidence_status: str` — (established, contested, speculative)

**Remediation (P0)**: Extend `EnrichedBelief` with all provenance fields. This is the core contract.

---

## PART 2: SILENT FAILURES — What Errors Are Being Hidden?

### Assessment: CATASTROPHIC (Score: 0.5/10)

#### Failure Mode 2.1: Service Unavailability → Silently Skipped

**Location**: Multiple try/except blocks across orchestrator (lines 371-850)

Pattern in EVERY enrichment step:

```python
def _enrich_credence(self, ...):
    try:
        service = self._services.get_credence_intervals()
        if not service:  # <-- SERVICE NOT AVAILABLE
            enriched.enrichment_metadata["services_skipped"].append(service_name)
            return  # <-- SILENT RETURN, NO ERROR TO USER
        # ... otherwise proceed with enrichment
    except Exception as e:
        logger.warning(f"{service_name}: {e}")  # <-- LOGGED, NOT DISPLAYED
        enriched.enrichment_metadata["services_failed"].append(service_name)
```

**The Problem**:
- If `credence_intervals` module is missing, function silently returns
- User gets a belief with `credence_ci = None` (defaulted)
- Metadata says "services_skipped" (visible only to developers reading JSON)
- User sees no warning

**Real-World Impact**: A user asks "How confident should I be?" Gets an answer with no credence interval. Final response looks complete but enrichment completely failed.

**Evidence**:
- Line 373-374: No credence service → add to skipped (silent)
- Line 394-397: Warrant service missing → add to skipped (silent)
- Line 415-418: Confounder checker missing → add to skipped (silent)

**Remediation (P0)**:
- Each enrichment step should NOT be optional for the user
- If a critical service is unavailable, return an error to user, not a degraded answer
- Define "critical" vs "optional" services
- Surface unavailability at the top level: "Warning: Credence enrichment unavailable (module missing)"

---

#### Failure Mode 2.2: Grounding Gate Exception → Caught and Ignored (CRITICAL)

**Location**: `answer_enrichment_orchestrator.py`, lines 475-495

```python
try:
    from src.qa.grounding_gate import GroundingGate
    grounding_gate = GroundingGate()
    grounding_result = grounding_gate.check(question, beliefs)
    if grounding_result.should_abstain:
        logger.warning(f"Grounding gate ABSTAIN: {grounding_result.reason}")
        enriched.enrichment_metadata["abstention"] = {
            "applied": True,
            "reason": grounding_result.reason,
        }
        return enriched  # <-- EARLY RETURN, BUT NO ERROR RAISED TO USER
except Exception as e:
    logger.warning(f"Grounding gate failed (proceeding with enrichment): {e}")  # <-- PROCEEDS ANYWAY!
    enriched.enrichment_metadata["grounding"] = {"error": str(e)}
```

**The Problem**:
1. Grounding gate is supposed to ABSTAIN when empirical anchoring is insufficient
2. If it raises an exception, we PROCEED WITH FULL ENRICHMENT instead of failing
3. User never knows the answer is unsupported

**Specific Failure Case**:
- Query: "Is consciousness a quantum effect?" (no empirical papers)
- Grounding gate should reject this
- If GroundingGate module is missing or raises an error → we enrich anyway
- User gets a carefully constructed answer with framework voices, gaps, follow-ups
- But it's completely hallucinated

**Remediation (P0)**:
- Grounding gate is NOT optional; it's a safety gate
- If it fails (exception), surface the error immediately; do NOT proceed
- If it abstains, return early with explicit abstention message visible to user

---

#### Failure Mode 2.3: Timeout Per Service → Most Services Ignore It

**Location**: `answer_enrichment_orchestrator.py`, lines 520-555

```python
def _enrich_credence(self, enriched, beliefs, timeout_ms):
    start = time.time()
    try:
        for i, belief_dict in enumerate(...):
            if (time.time() - start) * 1000 > timeout_ms:
                logger.warning(f"timeout after {timeout_ms}ms, stopping")
                break  # <-- BREAK INNER LOOP, NOT ENTIRE SERVICE
```

**The Problem**:
- Timeout check is INSIDE the belief loop
- If service starts processing 1000 beliefs, even if timeout is 2s, it processes ALL of them (the break only stops adding more)
- Global timeout check exists but is called only BETWEEN steps, not WITHIN steps

**Remediation (P0)**: Implement per-service timeout using signal handlers or asyncio. Current approach is ineffective.

---

## PART 3: INTERPRETIVE LAYER (Framework Voices) — Is This Real Analysis or Boilerplate?

### Assessment: DECORATIVE (Score: 2/10)

#### Finding 3.1: Voices Are Hardcoded, Not Topic-Aware

**Location**: `integrated_query_service.py`, lines 931-965 (get_theoretical_voices)

```python
def get_theoretical_voices(self, topic: str, limit: int = 4) -> Dict:
    """
    Bridge method for AnswerEnrichmentOrchestrator Step 4.
    Returns a dictionary of framework perspectives keyed by framework name...
    """
    voices = {}
    frameworks = list(FRAMEWORK_VOICES.keys())[:limit]

    for fw in frameworks:
        voice = FRAMEWORK_VOICES[fw]  # <-- HARDCODED DICTIONARY (lines 70-230)
        # Generate a perspective tailored to the topic
        perspective = (
            f"From {voice['name']}: {voice['core_claim']}. "
            f"Applied to '{topic}': {voice.get('complications', [''])[0]}"  # <-- JUST APPENDS TOPIC NAME
        )
```

**The Real Code**: Lines 70-230 define static framework voices:

```python
FRAMEWORK_VOICES = {
    T1Framework.PP: {
        "name": "Predictive Processing",
        "key_figures": ["Karl Friston", "Andy Clark"],
        "core_claim": "The brain is a prediction machine...",
        "typical_questions": [
            "What prediction is being violated here?",
            ...
        ],
        "complications": [
            "PE magnitude depends on prior precision...",
            ...
        ]
    },
    # ... 10 more frameworks, ALL HARDCODED ...
}
```

**Why This Fails**:
1. For query: "Does biophilic design reduce stress?" → PP voice says "The brain is a prediction machine that minimizes surprise"
2. This is true but NOT applied to the question
3. Real semantic analysis would ask: "What predictions about stress/design does this question require? How does PP lens change our understanding?"
4. Instead: "The brain is a prediction machine. Applied to biophilic design: PE magnitude depends on prior precision..."

**Evidence of Surface-Level Analysis**:
- `_generate_framework_perspective()` (lines 481-528): Hardcoded if/elif for each framework
- Example (lines 495-501):
  ```python
  if framework == T1Framework.PP:
      return (
          f"From a predictive processing view: {mechanism} can be understood as "
          f"prediction error at the {top.how[0].level if top.how else 'environmental'} level..."
      )
  ```
  This is a template, not analysis.

**Remediation (P1)**:
- Implement semantic matching: embed topic, find which framework's prior work is most relevant
- Generate framework voice by:
  1. Find key papers from this framework relevant to the topic
  2. Extract actual mechanisms from those papers
  3. Synthesize voice from evidence, not templates
- OR: Clearly label voices as "framework perspective templates" not "expert analysis"

---

#### Finding 3.2: Voices Don't Influence Final Answer

**Location**: `answer_enrichment_orchestrator.py`, lines 794-850 (_get_framework_voices)

```python
def _get_framework_voices(self, enriched, topic, timeout_ms):
    voices = service.get_theoretical_voices(topic, limit=...)
    for framework_name, perspective_data in voices.items():
        enriched.framework_voices.append({
            "framework": framework_name,
            "perspective": perspective_data["perspective"],
            ...
        })
```

Voices are stored in `enriched.framework_voices` but **never used to revise or contextualize beliefs**.

**Why This Matters**: Framework voices should influence interpretation. If Predictive Processing voice identifies a prediction-error mechanism, that should be flagged in the answer's "mechanism" section. Instead: separate, decorative.

**Remediation (P1)**: Integrate framework voices into belief interpretation. Each belief should show: "Which frameworks support/critique this? What do they add?"

---

## PART 4: LANGUAGE ADAPTATION — Does It Actually Adapt the Text?

### Assessment: METADATA-ONLY, NO TEXT TRANSFORMATION (Score: 1/10)

#### Finding 4.1: adapt_content() Returns Metadata, Not Adapted Text

**Location**: `language_adaptation_service.py`, lines 669-703 (adapt_content)

```python
def adapt_content(content: str, user_type: str, topic: str = "") -> Dict[str, Any]:
    """
    Module-level convenience function for the AnswerEnrichmentOrchestrator.
    Adapts content for a given user type and returns a metadata dict...
    """
    # ...
    return {
        "vocabulary": profile.get("vocabulary", "technical_precise"),
        "detail_level": "high" if ut in (UserType.RESEARCHER, UserType.REVIEWER) else "medium",
        "uncertainty_language": profile.get("uncertainty_style", "..."),
        "answer_structure": profile.get("answer_structure", []),
        "completeness_criteria": profile.get("completeness_criteria", []),
        "actionability": profile.get("actionability", 0.5),
        "user_type_resolved": ut.value,
    }
```

**The Problem**: This function:
- Takes user content (string)
- Returns metadata ABOUT how to adapt
- Does NOT return adapted content

The function name `adapt_content()` implies it returns adapted content. It actually returns guidance for manual adaptation.

**In Orchestrator (answer_enrichment_orchestrator.py, lines 839-860)**:

```python
def _adapt_language(self, enriched, question, user_type, timeout_ms):
    if not self._config.enable_language_adaptation:
        return

    try:
        from src.services.language_adaptation_service import adapt_content

        adapted_metadata = adapt_content(
            question,
            user_type,
            topic=enriched.base_answer.get("answer", "")
        )
        enriched.enrichment_metadata["language_adaptation"] = adapted_metadata
```

Stores metadata, doesn't apply transformation.

**Why This Is a Problem**:
1. User configures for "student" → expects simpler vocabulary
2. They get metadata saying "vocabulary should be: accessible_plus_technical"
3. Actual response still uses technical prose
4. User sees nothing changed

**Remediation (P0)**:
- EITHER: Have `adapt_content()` transform prose and return adapted text
- OR: Call separate method like `apply_vocabulary_adaptation(text, profile)` that actually rewrites
- Currently: Neither happens

---

#### Finding 4.2: `adapt_belief_presentation()` Defined but Never Called

**Location**: `language_adaptation_service.py`, lines 330-393

The `adapt_belief_presentation()` method exists and looks comprehensive:

```python
def adapt_belief_presentation(self, belief: Dict[str, Any], user_type: UserType) -> Dict[str, Any]:
    """Adapt how a single belief is presented."""
    adapted = {
        'content': belief.get('content', ''),
        'user_type': user_type.value,
    }
    # ... adapts credence, adds structure-specific fields ...
```

**But in orchestrator**: Never called. Language adaptation only stores metadata.

**Remediation (P0)**: Call `adapt_belief_presentation()` for every enriched belief before returning answer.

---

## PART 5: LATENCY BUDGET — Is It Actually Enforced?

### Assessment: PARTIAL, MOSTLY UNENFORCED (Score: 3/10)

#### Finding 5.1: Global Timeout Checked Between Steps, Not Within

**Location**: `answer_enrichment_orchestrator.py`, lines 490-515

```python
global_deadline = time.monotonic() + (self._config.global_timeout_ms / 1000.0)

def _budget_remaining() -> bool:
    """Check if global latency budget is exceeded."""
    return time.monotonic() < global_deadline

# ... then in each step:
if self._config.enable_credence_ci and _check_budget("credence_enrichment"):
    self._enrich_credence(enriched, beliefs, timeout_ms)
```

**The Problem**:
- Budget checked at START of each step
- If step goes overtime, we don't cancel it mid-run
- A slow service can burn through remaining budget
- Subsequent steps might still run if check happens before they start

**Example Failure**:
- Global timeout: 5000ms
- Credence enrichment takes 3000ms (OK)
- Warrant trace starts (we check budget, OK)
- Warrant trace processes 1000 beliefs, takes 5000ms
- By the time it finishes, we've burned 8000ms total
- Gap analysis starts anyway

**Remediation (P1)**: Use signal handlers or asyncio to hard-cancel any service that exceeds its share of budget.

---

#### Finding 5.2: Per-Service Timeout Not Respected in Inner Loops

**Location**: `answer_enrichment_orchestrator.py`, lines 520-555

```python
for i, belief_dict in enumerate(...):
    if (time.time() - start) * 1000 > timeout_ms:
        logger.warning(f"timeout after {timeout_ms}ms, stopping")
        break  # <-- Breaks the loop, but has already processed i beliefs
```

This works, but is inefficient. With 1000 beliefs and 2s timeout, we might process 500+ before timing out.

**Remediation (P1)**: Implement early exit at configurable iteration count, not just timeouts.

---

## PART 6: DATA QUALITY / SCHEMA INTEGRITY — Are Fields Always Populated?

### Assessment: INCONSISTENT, MANY SILENT NONES (Score: 2/10)

#### Finding 6.1: EnrichedAnswer Has Silent-Defaulting Optional Fields

**Location**: `answer_enrichment_orchestrator.py`, lines 135-146

```python
@dataclass
class EnrichedAnswer:
    base_answer: Dict[str, Any]
    enriched_beliefs: List[EnrichedBelief] = field(default_factory=list)  # <-- Defaults to []
    framework_voices: List[Dict[str, Any]] = field(default_factory=list)  # <-- Defaults to []
    gaps: List[Dict[str, Any]] = field(default_factory=list)  # <-- Defaults to []
    follow_ups: List[Dict[str, str]] = field(default_factory=list)  # <-- Defaults to []
    figures: List[Dict[str, Any]] = field(default_factory=list)  # <-- Defaults to []
    interpretation_context: Optional[Dict[str, Any]] = None  # <-- Defaults to None
    user_type: str = "researcher"  # <-- Defaults to "researcher"
    enrichment_metadata: Dict[str, Any] = field(default_factory=dict)
```

**Problem**: All these fields have defaults. A completely failed enrichment still returns a valid `EnrichedAnswer` with empty lists. User can't distinguish between:
- "No framework voices were generated" (OK)
- "Framework voices service failed to load" (ERROR)
- "You requested framework voices but I'm in lightweight mode" (OK, expected)

**Remediation (P1)**: Add a `status` field to `EnrichedAnswer`:

```python
@dataclass
class EnrichedAnswer:
    status: str  # "success", "partial_failure", "complete_failure"
    failure_reasons: List[str] = field(default_factory=list)  # Why we couldn't enrich
    # ... rest of fields ...
```

---

#### Finding 6.2: EnrichedBelief.warrant_trace Type is Incoherent

**Location**: `answer_enrichment_orchestrator.py`, line 129

```python
warrant_trace: Optional[List[Dict[str, Any]]] = None
```

But what goes in these dicts? Example (lines 700-706):

```python
trace = [
    {"component": "experimental_severity", "omega_sev": round(omega_sev, 3),
     "design_type": design_enum.value},
    {"component": "confound_control", "omega_conf": round(omega_conf, 3)},
    # ... No consistent schema for trace elements
]
```

Each dict has different keys! First has `omega_sev` and `design_type`, second has `omega_conf`.

**Remediation (P0)**: Define a `WarrantComponent` dataclass:

```python
@dataclass
class WarrantComponent:
    component: str  # "experimental_severity", "confound_control", etc.
    value: float  # omega value
    source_papers: List[str]  # Papers supporting this component
    explanation: str  # Why this component contributes
```

---

#### Finding 6.3: Confounder Risk Hardcoded

**Location**: `answer_enrichment_orchestrator.py`, lines 755-775

```python
design_type = beliefs[i].get("design_type", "observational")
if "observational" in design_type.lower():
    belief_dict.confounder_risk = "medium"
    belief_dict.confounder_details = [
        "Observational study: cannot rule out confounding",
        "Consider: selection bias, unmeasured confounds",
    ]
else:
    belief_dict.confounder_risk = "low"
    belief_dict.confounder_details = ["Experimental design with randomization"]
```

This is a crude if/else. Real confounder checking requires:
- Actual reading of methods section (does the paper identify confounds?)
- Matching to ConfounderRiskChecker service (which apparently exists)
- Computing actual risk, not binary obs vs. exp classification

**Remediation (P0)**: Actually call `ConfounderRiskChecker` if available; don't hardcode.

---

## PART 7: GROUNDING GATE SAFETY — Does It Actually Prevent Hallucination?

### Assessment: THEATER, NOT SAFETY (Score: 1/10)

#### Finding 7.1: Grounding Gate is Caught and Ignored

**Location**: `answer_enrichment_orchestrator.py`, lines 477-495

```python
try:
    grounding_gate = GroundingGate()
    grounding_result = grounding_gate.check(question, beliefs)
    if grounding_result.should_abstain:
        return enriched  # Early return with abstention metadata
except Exception as e:
    logger.warning(f"Grounding gate failed (proceeding with enrichment): {e}")
    # ... PROCEEDS ANYWAY ...
    return enriched  # But continues to enrich!
```

**The Problem**:
- If `GroundingGate` raises ANY exception, we ignore it and proceed
- If GroundingGate module doesn't exist, we proceed
- If GroundingGate says "should_abstain" but exception is raised during abstention... unclear
- User never sees any warning about this

**Real Scenario**:
1. User asks: "What supernatural powers does meditation give you?"
2. Grounding gate should abstain (no scientific evidence)
3. But GroundingGate module missing → exception → caught → proceed
4. System generates full enriched answer with framework voices, papers, etc.
5. User gets hallucinated answer

**Remediation (P0)**:
- Grounding gate is CRITICAL, not optional
- If it fails, return error immediately
- Never proceed with enrichment on ungrounded queries

---

#### Finding 7.2: Abstention is Not Observable

If grounding succeeds and returns `should_abstain=True`, the code does:

```python
if grounding_result.should_abstain:
    enriched.enrichment_metadata["abstention"] = {
        "applied": True,
        "reason": grounding_result.reason,
    }
    return enriched
```

This returns early with **empty enriched_beliefs**. But:
- Is the base_answer still included?
- Does the user interface check for abstention?
- Or does it show an empty answer?

**Remediation (P0)**: Abstention should be a first-class return status, not buried in metadata.

---

## SUMMARY SCORES

| Subsystem | Score | Status |
|-----------|-------|--------|
| Traceability Pipeline | 1/10 | BROKEN — paper IDs lost, no provenance |
| Error Handling / Silent Failures | 0.5/10 | CATASTROPHIC — failures hidden from user |
| Interpretive Layer (Framework Voices) | 2/10 | DECORATIVE — hardcoded, not semantic |
| Language Adaptation | 1/10 | METADATA ONLY — returns profiles, doesn't transform |
| Latency Budget Management | 3/10 | PARTIAL — timeout checks exist but not enforced |
| Data Quality / Schema Integrity | 2/10 | INCONSISTENT — fields always optional, silent defaults |
| Grounding Gate Safety | 1/10 | THEATER — exceptions caught, abstention not observable |
| Test Coverage | 4/10 | MOCK-BASED — masks actual failures with mocks |
| Overall System Health | 3.8/10 | DEGRADED from 5.2 |

---

## THREE MOST DANGEROUS FAILURE MODES

### Failure Mode 1: Hallucinated High-Confidence Answers (User-Visible Harm)

**Scenario**:
- User asks: "Can smartphones cause cancer?" (contentious, limited evidence)
- Query has 2 weak papers; most knowledge is template-based
- Grounding gate would abstain, but exception occurs → silently caught
- Credence service missing → silently skipped
- User gets carefully formatted answer with:
  - Framework voices (hardcoded perspectives)
  - Research gaps (suggested, not empirical)
  - Follow-ups (generic)
  - Metadata: `services_attempted: ["credence_enrichment"]` but credence_ci = None
- User sees polished answer, believes it's well-grounded
- Actually: template reasoning + hallucinated enrichment

**Likelihood**: HIGH
**Impact**: User makes health decision based on fabricated confidence

---

### Failure Mode 2: Lost Traceability → Unverifiable Claims

**Scenario**:
- User reads enriched answer about attention restoration theory
- Wants to verify: "Which papers say this?"
- Looks at `enriched_beliefs` → No `paper_ids` field
- Cannot verify source
- Belief looks credible due to confident credence number (which is actually template-based, not paper-backed)

**Likelihood**: VERY HIGH (this is current state)
**Impact**: Breaks epistemic accountability; user can't fact-check

---

### Failure Mode 3: Silent Service Failure → Degraded Answer Looks Complete

**Scenario**:
- System deployed without `warrant_strength` module (git clone missed this package)
- User asks complex question
- Warrant enrichment fails silently
- User gets answer with:
  - Credence intervals: ✓ present
  - Warrant trace: NULL (but doesn't look wrong, just missing field)
  - Confounder risk: ✓ present (hardcoded, so always works)
- Metadata says "services_skipped: ['warrant_trace']" (only visible in JSON/logs)
- User interface shows clean answer
- User trusts enriched_beliefs with null warrant_trace
- Makes decision based on incomplete epistemic warrant

**Likelihood**: HIGH
**Impact**: Distributed system with partial failures looks like complete success

---

## PRIORITIZED REMEDIATION

### P0 — STOP shipping answers that fail grounding
1. **Grounding gate must not be caught/ignored** (line 477)
   - If it raises exception: return explicit error
   - If it returns should_abstain=True: return abstention response (not empty enrichment)
   - Never proceed to enrichment if grounding fails

2. **EnrichedBelief must include paper_ids and source_papers** (line 126)
   - Add fields to dataclass
   - Copy from input beliefs in ALL enrichment steps
   - Test traceability end-to-end

3. **Language adaptation must actually transform text** (line 839)
   - Current: returns metadata only
   - Required: transform base_answer prose per user_type
   - OR: clearly label as "recommended adaptations" not "adaptations applied"

4. **Critical services must not be optional** (line 373)
   - Define: "critical" services that MUST run or answer fails
   - Credence enrichment, grounding, warrant trace = critical
   - If critical service unavailable: return error, not degraded answer

### P1 — Restore epistemic integrity
1. **Reimplement framework voices semantically** (line 931)
   - Don't use hardcoded templates
   - Match query to framework literature
   - Or: label as "framework perspective templates" not analysis

2. **Enforce global latency budget** (line 490)
   - Use signal handlers or asyncio
   - Hard-cancel services that exceed budget
   - Don't allow soft timeouts

3. **Add EnrichedAnswer.status field** (line 135)
   - "success", "partial_failure", "abstention", "complete_failure"
   - Replace silent default factories
   - User interface can respond appropriately

4. **Test with actual services, not mocks** (test files)
   - Current tests use mocks and pass
   - Real services are missing (warrant_strength, gap_predictor, etc.)
   - Add integration tests that verify end-to-end traceability

### P2 — Improve robustness
1. Define consistent schema for warrant_trace (Dict → dataclass)
2. Implement real confounder risk checking (not if/else)
3. Call adapt_belief_presentation() in orchestrator
4. Add observability: log which services actually ran vs skipped

---

## PRIOR AUDIT COMPARISON

| Aspect | V12 (5.2/10) | V13 (3.8/10) | Delta |
|--------|-----------|-----------|-------|
| Traceability | 4/10 (attempted) | 1/10 (broken) | -3 |
| Error Handling | 2/10 (bad) | 0.5/10 (worse) | -1.5 |
| Framework Voices | 4/10 (somewhat useful) | 2/10 (exposed as template) | -2 |
| Language Adaptation | 3/10 (incomplete) | 1/10 (metadata only) | -2 |
| Grounding Gate | Added in V13 | 1/10 (doesn't work) | — |
| Tests | 5/10 (mocked) | 4/10 (revealed weaknesses) | -1 |

**Root Cause of Regression**: V13 code changes made enrichment steps more granular (good) but service contracts were not properly enforced. Each step now silently skips if services are missing, giving false sense of completeness. V12 had broader try/catches that would fail more obviously.

---

## CONCLUSION

The Article Eater enrichment pipeline is **not production-ready**. While the code is syntactically sound and tests pass with mocks, the actual system:

1. **Cannot trace beliefs to sources** (lost paper IDs)
2. **Hides failures from users** (silent service skips)
3. **Generates decorative enrichments** (hardcoded framework voices)
4. **Doesn't actually apply adaptations** (language service metadata-only)
5. **Presents hallucinated answers with confidence** (grounding gate is theater)

**The danger is not obvious failure** — it's plausible, complete-looking failure. Answers are well-formatted with credence intervals and framework perspectives. Users trust them. But epistemic accountability is broken.

**Immediate action required**: Do NOT deploy without implementing P0 fixes. Especially grounding gate and paper traceability.

---

**Audit Completed**: 2026-03-03
**Generated by**: Claude Code (Agent for Prof. David Kirsh, UCSD Cognitive Science)
**For Review by**: Expert panel (epistemology, causal inference, science communication)
