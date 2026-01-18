# 🎯 AI HANDOFF: BUILD ARTICLE EATER V18 REPOSITORY

**Purpose**: Complete implementation of Article Eater v18 "Epistemological Engine"  
**Target**: New Claude/GPT instance to generate ALL v18 implementation files  
**Context**: Upgrade from v17 (dual hierarchy partial) to v18 (dual hierarchy complete + Set of Support + HITL)

---

## MAGIC CONTEXT PROMPT (Copy This Entire Section to New AI)

```
You are implementing Article Eater v18 - the "Epistemological Engine" for 
Cognitive Neuroscience for Architecture (CNfA) evidence synthesis.

BACKGROUND:
- User (David, professor at UCSD) researches how built environments affect 
  human cognition, affect, and behavior
- Article Eater extracts structured data from academic papers to build 
  Bayesian Belief Networks (BBNs) for evidence synthesis
- v17 has dual hierarchy (Findings + Mechanisms) but with critical flaws
- v18 fixes the flaws and adds Set of Support + HITL workflow

THE CRITICAL PROBLEM v18 SOLVES:
v17 uses parent_finding_id which conflates TWO types of relationships:
1. TAXONOMIC (definitional): Cortisol↓ rolls up into "Stress Reduction"
2. CAUSAL (empirical): Plants CAUSES Cortisol↓

This is "catastrophically flawed" (Gemini's words) - cannot build proper BBN.

v18 SOLUTION:
Replace parent_finding_id with finding_links table that has link_type field:
- link_type='TAXONOMIC' for rollups
- link_type='CAUSAL' for empirical effects

PLUS:
- Set of Support: Paper-type-specific confidence calculation
- Agent_Classifier: Determines if paper is RCT, Theory, Meta-Analysis, etc.
- Agent_PromptRouter: Uses different 7-panel prompts per paper type
- HITL Approval: Human approves Agent_Aggregator and Agent_Linker proposals

YOUR TASK:
Generate complete v18 implementation:
1. Database migrations (finding_links table, paper_type field, set_of_support)
2. Agent modules (Classifier, PromptRouter, Aggregator, Linker)
3. Confidence calculation (SetOfSupport classes for each paper type)
4. Updated ingestion pipeline (Option A: pre-compute with HITL gate)
5. Librarian/Synthesizer GUI split
6. Deployment documentation

I will provide:
1. V18 specifications (Gemini's exact answers to critical questions)
2. v17 codebase (what exists, what to keep)
3. Database schema (exact SQL for migrations)
4. Confidence formulas (exact Python for each paper type)
5. Implementation checklist (7-week phased roadmap)

After you generate v18, user will:
1. Review for correctness (compare to specifications)
2. Test database migrations on v17 backup
3. Deploy phased (Week 1: database, Week 2: agents, etc.)

Ready? Let's build v18 file by file.
```

---

## FILES TO INCLUDE IN HANDOFF

### 1. Core Specifications (3 files - MUST INCLUDE)

**File 1**: [V18_IMPLEMENTATION_GUIDE_FINAL.md](computer:///mnt/user-data/outputs/V18_IMPLEMENTATION_GUIDE_FINAL.md)
- **Why**: Gemini's definitive answers to ALL critical questions
- **What AI needs**: Database schema, confidence formulas, agent specs

**File 2**: [V18_SYNTHESIS_Complete_Analysis.md](computer:///mnt/user-data/outputs/V18_SYNTHESIS_Complete_Analysis.md)
- **Why**: My original ruthless critique + what v17 has
- **What AI needs**: Understanding of what to keep vs replace

**File 3**: [FINAL_DECISION_v18_GO.md](computer:///mnt/user-data/outputs/FINAL_DECISION_v18_GO.md)
- **Why**: Executive summary, key insights from Gemini
- **What AI needs**: Quick reference for decisions made

### 2. v17 Codebase Reference (1 file - CRITICAL)

**File 4**: Article_Eater_v17_0_real_with_UPGRADE_not_sure_if_dual_concatenated.txt
- **Why**: Shows what v17 currently has (60% of v18)
- **What AI needs**: 
  - Existing database schema (to write migrations FROM)
  - Existing 7-panel prompt (to adapt for paper types)
  - Existing routes (to extend for Librarian/Synthesizer)
  - Don't reinvent what works, just extend it

### 3. Domain Context (2 files - RECOMMENDED)

**File 5**: [SYSTEM_VISION.md](computer:///mnt/user-data/outputs/SYSTEM_VISION.md)
- **Why**: Explains CNfA domain, Article Eater purpose
- **What AI needs**: Domain vocabulary, user profile

**File 6**: Gemini's v18 memo (from Gemini_handoff_explanation.docx)
- **Why**: Original v18 vision from architect
- **What AI needs**: High-level architecture rationale

### 4. Governance Integration (2 files - OPTIONAL BUT USEFUL)

**File 7**: [GOVERNANCE_KIT_v3_Repo_Agnostic.md](computer:///mnt/user-data/outputs/GOVERNANCE_KIT_v3_Repo_Agnostic.md)
- **Why**: Track v18 implementation decisions
- **What AI needs**: How to log sessions/decisions as it builds

**File 8**: [CONVERSATION_LEDGER.yml](computer:///mnt/user-data/outputs/CONVERSATION_LEDGER.yml)
- **Why**: Example of tracking development provenance
- **What AI needs**: Pattern to follow

---

## COMPLETE FILE STRUCTURE AI SHOULD CREATE

```
article-eater-v18/
│
├── README.md                           ← AI updates for v18 (what's new)
├── CHANGELOG.md                        ← AI creates (v17 → v18 changes)
│
├── migrations/                         ← SQL migrations
│   ├── 005_create_finding_links.sql    (THE critical fix)
│   ├── 006_add_paper_type.sql          (Set of Support)
│   ├── 007_add_set_of_support.sql      (Set of Support)
│   └── 008_backfill_v17_data.sql       (migrate parent_finding_id)
│
├── src/
│   ├── agents/                         ← NEW: Agent modules
│   │   ├── __init__.py
│   │   ├── agent_classifier.py         (Two-pass paper type detection)
│   │   ├── agent_prompt_router.py      (Multi-template manager)
│   │   ├── agent_aggregator.py         (Propose meso-findings, HITL)
│   │   └── agent_linker.py             (Propose mechanism links, HITL)
│   │
│   ├── confidence/                     ← NEW: Set of Support
│   │   ├── __init__.py
│   │   ├── setof_support.py            (Base class + calculator)
│   │   ├── experimental_support.py     (RCT confidence formula)
│   │   ├── meta_support.py             (Meta-analysis formula)
│   │   └── theoretical_support.py      (Returns -1.0, HITL)
│   │
│   ├── models/                         ← UPDATE: Database models
│   │   ├── __init__.py
│   │   ├── finding.py                  (Update: remove parent_finding_id)
│   │   ├── finding_link.py             (NEW: link_type field)
│   │   ├── paper.py                    (Update: add paper_type)
│   │   └── mechanism.py                (Keep as-is)
│   │
│   └── routes/                         ← UPDATE: Routes for new GUI
│       ├── routes_librarian.py         (NEW: scouting + instant 7-panel)
│       ├── routes_synthesizer.py       (NEW: HITL approval interface)
│       ├── routes_papers.py            (Keep: paper analysis view)
│       └── routes_rules.py             (Update: use finding_links)
│
├── prompts/                            ← NEW: Multi-template system
│   ├── 7_panel_prompt_RCT.txt          (Experimental papers)
│   ├── 7_panel_prompt_THEORY.txt       (Theoretical papers)
│   ├── 7_panel_prompt_META.txt         (Meta-analyses)
│   ├── 7_panel_prompt_OBSERVATIONAL.txt
│   └── 7_panel_prompt_QUALITATIVE.txt
│
├── templates/                          ← UPDATE: HTML templates
│   ├── librarian/
│   │   ├── inventory.html              (Paper browsing + filters)
│   │   ├── paper_detail.html           (Instant 7-panel view)
│   │   └── scout.html                  (RAG enrichment trigger)
│   │
│   ├── synthesizer/
│   │   ├── approve.html                (HITL approval interface)
│   │   ├── proposals.html              (Show pending proposals)
│   │   └── graph.html                  (BBN visualization)
│   │
│   └── [keep existing templates]
│
├── static/
│   ├── css/
│   │   ├── librarian.css               (NEW: Librarian styling)
│   │   └── synthesizer.css             (NEW: Synthesizer styling)
│   │
│   └── js/
│       ├── librarian.js                (NEW: Filter interactions)
│       └── approval.js                 (NEW: HITL workflow)
│
├── tests/                              ← NEW: Test suite
│   ├── test_agents.py                  (Test classification, routing)
│   ├── test_confidence.py              (Test Set of Support formulas)
│   ├── test_finding_links.py           (Test link_type queries)
│   └── test_migrations.py              (Test SQL migrations)
│
├── docs/
│   ├── v18_DEPLOYMENT_GUIDE.md         (How to deploy v17 → v18)
│   ├── v18_ARCHITECTURE.md             (Technical architecture doc)
│   ├── v18_TESTING_PLAN.md             (How to test each phase)
│   └── v18_TROUBLESHOOTING.md          (Common issues + fixes)
│
└── scripts/
    ├── migrate_v17_to_v18.py           (Automated migration script)
    ├── test_confidence_tuning.py       (Test formulas on real papers)
    └── validate_v18.py                 (Check v18 implementation complete)
```

---

## DETAILED INSTRUCTIONS FOR AI

### Phase 1: Database Migrations (Week 1 Focus)

#### Migration 005: Create finding_links table

**AI must generate**:

```sql
-- migrations/005_create_finding_links.sql
-- THE CRITICAL FIX: Replaces parent_finding_id with explicit link table

CREATE TABLE finding_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source and target findings
    source_finding_id INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    target_finding_id INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    
    -- THE CRITICAL FIELD (Gemini's solution)
    link_type VARCHAR(20) NOT NULL CHECK(link_type IN ('CAUSAL', 'TAXONOMIC')),
    
    -- Link weight (confidence)
    weight REAL DEFAULT 1.0,
    
    -- Set of Support (JSON for CAUSAL links)
    set_of_support TEXT, -- JSON: {N, p, d, method, etc.}
    
    -- Provenance (for CAUSAL links)
    paper_id INTEGER REFERENCES papers(id) ON DELETE SET NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(source_finding_id, target_finding_id, link_type, paper_id),
    
    -- Validation: TAXONOMIC links should have weight=1.0
    CHECK(link_type != 'TAXONOMIC' OR weight = 1.0),
    
    -- Validation: CAUSAL links must have paper_id
    CHECK(link_type != 'CAUSAL' OR paper_id IS NOT NULL)
);

-- Indexes for efficient queries
CREATE INDEX idx_finding_links_source ON finding_links(source_finding_id);
CREATE INDEX idx_finding_links_target ON finding_links(target_finding_id);
CREATE INDEX idx_finding_links_type ON finding_links(link_type);
CREATE INDEX idx_finding_links_paper ON finding_links(paper_id);
CREATE INDEX idx_finding_links_source_type ON finding_links(source_finding_id, link_type);
CREATE INDEX idx_finding_links_target_type ON finding_links(target_finding_id, link_type);
```

#### Migration 006: Add paper_type to papers

```sql
-- migrations/006_add_paper_type.sql
-- Set of Support: Track paper types for confidence calculation

ALTER TABLE papers ADD COLUMN paper_type TEXT; 
-- JSON array: ["experimental_rct", "theoretical"]

-- Index for filtering by paper type
CREATE INDEX idx_papers_type ON papers(paper_type);
```

#### Migration 007: Add set_of_support to findings

```sql
-- migrations/007_add_set_of_support.sql
-- Set of Support: Store extracted statistical data

ALTER TABLE findings ADD COLUMN set_of_support TEXT;
-- JSON: {N: 68, p: 0.03, d: 0.52, method: "RCT"}

-- For searching by sample size, p-value, etc.
CREATE INDEX idx_findings_support ON findings(set_of_support);
```

#### Migration 008: Backfill v17 data

```sql
-- migrations/008_backfill_v17_data.sql
-- Migrate parent_finding_id relationships to finding_links

-- TAXONOMIC links (all parent_finding_id are taxonomic rollups)
INSERT INTO finding_links (source_finding_id, target_finding_id, link_type, weight)
SELECT 
    id AS source_finding_id,
    parent_finding_id AS target_finding_id,
    'TAXONOMIC' AS link_type,
    1.0 AS weight
FROM findings
WHERE parent_finding_id IS NOT NULL;

-- CAUSAL links (extract from antecedents JSON - more complex)
-- TODO: This requires parsing antecedents field and creating CAUSAL links
-- Will be done by Python script: scripts/migrate_v17_to_v18.py
```

---

### Phase 2: Agent Modules (Week 2-3 Focus)

#### Agent_Classifier (Gemini's Two-Pass Triage)

**AI must generate** `src/agents/agent_classifier.py`:

```python
"""
Agent_Classifier: Two-Pass Paper Type Detection
Gemini's specification from v18 memo.
"""

import re
from typing import Set
from enum import Enum

class PaperType(Enum):
    EXPERIMENTAL_RCT = "experimental_rct"
    OBSERVATIONAL = "observational"
    META_ANALYSIS = "meta_analysis"
    THEORETICAL = "theoretical"
    QUALITATIVE = "qualitative"
    REVIEW = "review"

class AgentClassifier:
    """
    Two-pass heuristic classifier (Gemini's exact specification).
    
    Pass 1: Keyword scan on abstract + title (fast)
    Pass 2: Methods section parse if ambiguous
    
    Returns: SET of PaperType (hybrids allowed)
    Example: {EXPERIMENTAL_RCT, THEORETICAL} = RCT with strong theory
    """
    
    # Gemini's exact keyword lists
    PASS1_KEYWORDS = {
        PaperType.META_ANALYSIS: [
            "systematic review", "meta-analysis", "meta analysis",
            "pooled effect", "forest plot", "heterogeneity"
        ],
        PaperType.THEORETICAL: [
            "theoretical", "conceptual", "framework",
            "review",  # But NOT "systematic review"
            "model", "hypothesis"
        ],
        PaperType.EXPERIMENTAL_RCT: [
            "RCT", "randomized", "randomised", "control trial",
            "randomly assigned", "placebo", "double-blind"
        ]
    }
    
    PASS2_KEYWORDS = {
        PaperType.EXPERIMENTAL_RCT: [
            "randomly assigned", "control group", "randomization",
            "double-blind", "placebo-controlled"
        ],
        PaperType.OBSERVATIONAL: [
            "we surveyed", "cohort", "regression analysis",
            "cross-sectional", "longitudinal", "correlational"
        ],
        PaperType.QUALITATIVE: [
            "interviews", "thematic analysis", "ethnographic",
            "grounded theory", "phenomenology", "case study"
        ]
    }
    
    def classify(self, paper) -> Set[PaperType]:
        """
        Classify paper type(s).
        
        Returns set of PaperType (multiple for hybrids).
        """
        types = set()
        
        # Pass 1: Abstract + Title scan
        abstract_title = f"{paper.abstract or ''} {paper.title or ''}"
        abstract_lower = abstract_title.lower()
        
        for paper_type, keywords in self.PASS1_KEYWORDS.items():
            if any(kw in abstract_lower for kw in keywords):
                # Special case: "systematic review" → META_ANALYSIS only
                if paper_type == PaperType.THEORETICAL:
                    if "systematic review" in abstract_lower or "meta-analysis" in abstract_lower:
                        continue  # Skip, this is meta-analysis
                types.add(paper_type)
        
        # If unambiguous (single type), done
        if len(types) == 1:
            return types
        
        # Pass 2: Methods section (if ambiguous or empty)
        if len(types) == 0 or len(types) > 2:
            methods = self._extract_methods_section(paper.full_text)
            methods_lower = methods.lower()
            
            for paper_type, keywords in self.PASS2_KEYWORDS.items():
                if any(kw in methods_lower for kw in keywords):
                    types.add(paper_type)
        
        # Gemini: "Hybrids are goldmines" - keep multiple types
        
        # Default if still ambiguous
        if len(types) == 0:
            types.add(PaperType.OBSERVATIONAL)  # Conservative default
        
        return types
    
    def _extract_methods_section(self, full_text: str) -> str:
        """Extract Methods section from full text."""
        if not full_text:
            return ""
        
        patterns = [
            r"## Methods\n(.*?)(?=##|\Z)",
            r"# Methods\n(.*?)(?=#|\Z)",
            r"Methods\n(.*?)(?=\n[A-Z][a-z]+\n|\Z)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
```

#### Agent_PromptRouter (Gemini's Multi-Template Manager)

**AI must generate** `src/agents/agent_prompt_router.py`:

```python
"""
Agent_PromptRouter: Multi-Template Prompt Manager
Gemini's specification: 5 separate prompts, merge for hybrids.
"""

from typing import Set
from pathlib import Path

class AgentPromptRouter:
    """
    Routes to correct 7-panel prompt(s) based on paper type.
    Handles hybrids by running multiple prompts and merging.
    """
    
    PROMPT_FILES = {
        PaperType.EXPERIMENTAL_RCT: "prompts/7_panel_prompt_RCT.txt",
        PaperType.THEORETICAL: "prompts/7_panel_prompt_THEORY.txt",
        PaperType.META_ANALYSIS: "prompts/7_panel_prompt_META.txt",
        PaperType.OBSERVATIONAL: "prompts/7_panel_prompt_OBSERVATIONAL.txt",
        PaperType.QUALITATIVE: "prompts/7_panel_prompt_QUALITATIVE.txt",
    }
    
    def route(self, paper, paper_types: Set[PaperType]):
        """
        Route to correct prompt(s).
        
        Single type: Run one prompt on full text
        Hybrid: Run multiple prompts on targeted sections, merge
        """
        if len(paper_types) == 1:
            return self._run_single_prompt(paper, list(paper_types)[0])
        else:
            return self._run_hybrid_prompts(paper, paper_types)
    
    def _run_single_prompt(self, paper, paper_type):
        """Run single prompt on full text."""
        prompt_file = self.PROMPT_FILES[paper_type]
        prompt = self._load_prompt(prompt_file)
        
        # Call Anthropic API
        result = self._call_llm(prompt, paper.full_text)
        
        return self._parse_seven_panel(result)
    
    def _run_hybrid_prompts(self, paper, paper_types):
        """
        Hybrid handling (Gemini's specification):
        
        Example: [OBSERVATIONAL, THEORETICAL]
        1. Run OBSERVATIONAL on full text → Panels 3,4,5
        2. Run THEORETICAL on Intro+Discussion → Panels 2,6
        3. Merge into single artifact
        """
        artifact = SevenPanelArtifact()
        
        # Empirical prompts (RCT, Observational)
        if PaperType.EXPERIMENTAL_RCT in paper_types:
            empirical = self._run_single_prompt(paper, PaperType.EXPERIMENTAL_RCT)
            artifact.merge_panels([3, 4, 5], empirical)
        elif PaperType.OBSERVATIONAL in paper_types:
            empirical = self._run_single_prompt(paper, PaperType.OBSERVATIONAL)
            artifact.merge_panels([3, 4, 5], empirical)
        
        # Theoretical prompt (on Intro+Discussion only)
        if PaperType.THEORETICAL in paper_types:
            intro_discussion = self._extract_intro_discussion(paper.full_text)
            theoretical = self._run_single_prompt_on_text(
                intro_discussion, 
                PaperType.THEORETICAL
            )
            artifact.merge_panels([2, 6], theoretical)
        
        # Panels 1,7 from primary prompt
        artifact.panel_1 = empirical.panel_1 if 'empirical' in locals() else None
        artifact.panel_7 = empirical.panel_7 if 'empirical' in locals() else None
        
        return artifact
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from file."""
        return Path(filename).read_text()
    
    def _call_llm(self, prompt: str, text: str) -> str:
        """Call Anthropic API (Claude Sonnet 4)."""
        # TODO: Implement Anthropic API call
        pass
```

---

### Phase 3: Set of Support (Week 3 Focus)

**AI must generate** `src/confidence/setof_support.py`:

```python
"""
Set of Support: Paper-type-specific confidence calculation.
Gemini's exact formulas from v18 answers.
"""

from typing import List
import statistics

class SetOfSupportCalculator:
    """
    Main calculator that routes to paper-type-specific formulas.
    """
    
    def calculate(self, finding, papers: List) -> float:
        """
        Calculate confidence based on paper type(s).
        
        Returns:
            float: Confidence 0.0-1.0, or -1.0 for MANUAL_REVIEW_REQUIRED
        """
        # Determine paper types
        paper_types = self._get_paper_types(papers)
        
        if PaperType.EXPERIMENTAL_RCT in paper_types:
            return ExperimentalSupport().calculate(finding, papers)
        elif PaperType.META_ANALYSIS in paper_types:
            return MetaAnalysisSupport().calculate(finding, papers)
        elif PaperType.THEORETICAL in paper_types:
            return TheoreticalSupport().calculate(finding, papers)
        elif PaperType.QUALITATIVE in paper_types:
            return TheoreticalSupport().calculate(finding, papers)  # Same: -1.0
        else:
            # Default to experimental (conservative)
            return ExperimentalSupport().calculate(finding, papers)


class ExperimentalSupport:
    """
    Confidence for Experimental/RCT papers.
    Gemini's formula: conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
    """
    
    def calculate(self, finding, papers: List) -> float:
        # Extract from Set of Support JSON
        n_values = [p.set_of_support.get('N', 0) for p in papers if p.set_of_support]
        p_values = [p.set_of_support.get('p', 1.0) for p in papers if p.set_of_support]
        d_values = [p.set_of_support.get('d', 0.0) for p in papers if p.set_of_support]
        
        if not n_values:
            return 0.0  # No data
        
        total_n = sum(n_values)
        min_p = min(p_values) if p_values else 1.0
        avg_d = statistics.mean(d_values) if d_values else 0.0
        
        # Normalize scores (Gemini's exact heuristics)
        score_N = min(total_n / 200, 1.0)  # Caps at N=200
        score_p = max(0, 1.0 - (min_p / 0.05))  # p=0.05 → 0, p<0.05 → >0
        score_d = min(abs(avg_d) / 0.8, 1.0)  # Caps at Cohen's d=0.8
        
        # Weighted confidence (Gemini's weights)
        conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
        
        return conf


class MetaAnalysisSupport:
    """
    Confidence for Meta-Analysis papers.
    Gemini's formula: conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
    """
    
    def calculate(self, finding, papers: List) -> float:
        # Assume single meta-analysis paper
        meta = papers[0]
        sos = meta.set_of_support
        
        k_studies = sos.get('k_studies', 0)
        ci_lower = sos.get('ci_lower', 0)
        ci_upper = sos.get('ci_upper', 1)
        i_squared = sos.get('i_squared', 100)  # Heterogeneity 0-100
        
        ci_width = ci_upper - ci_lower
        
        # Normalize scores (Gemini's exact heuristics)
        score_k = min(k_studies / 20, 1.0)  # Caps at 20 studies
        score_CI = max(0, 1.0 - (ci_width / 0.5))  # Wide CI = 0.5
        score_I2 = 1.0 - (i_squared / 100)  # Low heterogeneity = high score
        
        # Weighted confidence (Gemini's weights)
        conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
        
        return conf


class TheoreticalSupport:
    """
    Confidence for Theoretical/Qualitative papers.
    Gemini's answer: DON'T quantify. Return -1.0 (MANUAL_REVIEW_REQUIRED).
    """
    
    def calculate(self, finding, papers: List) -> float:
        # Gemini: "THIS IS A TRAP. The agent must not quantify this."
        return -1.0  # Sentinel value for HITL
```

---

### Phase 4: Prompts (Week 2 Focus)

**AI must generate 5 prompt files**. Start with adapting v17 prompt:

#### prompts/7_panel_prompt_RCT.txt

```
[Copy v17 7-panel prompt as base]

MODIFICATIONS FOR RCT:
- Panel 4 (Methodology): Emphasize randomization, control group, blinding
- Panel 5 (Findings): Extract Set of Support: N, p, d, method, CI
- Panel 6 (Mechanisms): Look for physiological mechanisms
```

#### prompts/7_panel_prompt_THEORY.txt

```
Panel 2 (Research Focus):
- Extract: Key claims (what theory proposes)
- Extract: Testable predictions (what could falsify it)
- Extract: Gap it solves (what prior theories missed)

Panel 5 (Findings):
- N/A for pure theory papers

Panel 6 (Discussion & Mechanisms):
- Extract: Logical coherence (0-1 scale)
- Extract: Explanatory power (what phenomena it explains)
- Extract: Key citations (foundational papers)
```

#### prompts/7_panel_prompt_META.txt

```
Panel 4 (Methodology):
- Extract: k_studies (number of studies included)
- Extract: Inclusion criteria
- Extract: Search strategy

Panel 5 (Findings):
- Extract: Pooled effect size
- Extract: Confidence interval (95% CI)
- Extract: Heterogeneity (I² statistic)
- Extract: Publication bias assessment
```

---

### Phase 5: GUI Updates (Week 5-6 Focus)

#### Librarian Route (NEW)

**AI must generate** `src/routes/routes_librarian.py`:

```python
"""
Librarian Routes: Paper inventory + scouting + instant 7-panel access.
Gemini's specification: Option A (pre-computed, instant access).
"""

from flask import Blueprint, render_template, request

bp = Blueprint('librarian', __name__, url_prefix='/librarian')

@bp.route('/')
def inventory():
    """
    Paper inventory with filters.
    Gemini: "Faceted search" with PaperType, Set of Support, Measures filters.
    """
    # Get filters from query params
    paper_type_filter = request.args.get('type')
    min_n = request.args.get('min_n', type=int)
    measure_filter = request.args.get('measure')
    
    # Query papers (7-panel already pre-computed)
    papers = query_papers(
        paper_type=paper_type_filter,
        min_n=min_n,
        measure=measure_filter
    )
    
    return render_template('librarian/inventory.html', papers=papers)

@bp.route('/paper/<paper_id>')
def paper_detail(paper_id):
    """
    Instant 7-panel view.
    Gemini: "Instantly available" (no 30-second wait).
    """
    paper = get_paper(paper_id)
    seven_panel = get_seven_panel(paper_id)  # Pre-computed during ingestion
    
    return render_template('librarian/paper_detail.html', 
                           paper=paper, 
                           seven_panel=seven_panel)

@bp.route('/paper/<paper_id>/scout', methods=['POST'])
def scout_related(paper_id):
    """
    Trigger Agent_Enrichment (RAG).
    Gemini: "Find Related" button in Librarian.
    """
    paper = get_paper(paper_id)
    
    # Trigger RAG search
    related_papers = agent_enrichment_search(paper)
    
    # Add to "Awaiting Ingest" queue (with HITL gate)
    for related in related_papers:
        add_to_ingest_queue(related, status='awaiting_approval')
    
    return redirect(url_for('librarian.inventory'))
```

#### Synthesizer Route (NEW)

**AI must generate** `src/routes/routes_synthesizer.py`:

```python
"""
Synthesizer Routes: HITL approval interface for graph building.
Gemini's specification: Human approves Agent_Aggregator and Agent_Linker proposals.
"""

from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('synthesizer', __name__, url_prefix='/synthesizer')

@bp.route('/<job_id>/approve')
def approval_interface(job_id):
    """
    HITL approval interface.
    Shows pending proposals from Agent_Aggregator and Agent_Linker.
    """
    pending_meso = get_pending_meso_proposals(job_id)
    pending_links = get_pending_mechanism_links(job_id)
    manual_review = get_manual_review_items(job_id)  # conf=-1.0 items
    
    return render_template('synthesizer/approve.html',
                           pending_meso=pending_meso,
                           pending_links=pending_links,
                           manual_review=manual_review)

@bp.route('/<job_id>/approve/<proposal_id>', methods=['POST'])
def approve_proposal(job_id, proposal_id):
    """
    User approves or denies a proposal.
    """
    action = request.form.get('action')  # 'approve' or 'deny'
    
    if action == 'approve':
        approve_proposal_db(proposal_id)
    elif action == 'deny':
        deny_proposal_db(proposal_id)
    elif action == 'edit':
        # User edits proposal before approving
        edited_data = request.form.get('edited_data')
        update_proposal(proposal_id, edited_data)
        approve_proposal_db(proposal_id)
    
    return jsonify({'status': 'success'})

@bp.route('/<job_id>/manual_review/<item_id>', methods=['POST'])
def manual_review_confidence(job_id, item_id):
    """
    User sets confidence for theoretical/qualitative links (conf=-1.0).
    Gemini: "You, the human expert, set the confidence."
    """
    user_confidence = request.form.get('confidence', type=float)
    rationale = request.form.get('rationale')
    
    set_confidence_manual(item_id, user_confidence, rationale)
    
    return jsonify({'status': 'success'})
```

---

### Phase 6: Documentation (Throughout)

**AI must generate**:

#### docs/v18_DEPLOYMENT_GUIDE.md

```markdown
# Article Eater v18 Deployment Guide

## Prerequisites
- v17 running and stable
- Database backup created
- Python 3.11+ installed
- Anthropic API key configured

## Phase 1: Database Migration (Week 1)

### Step 1: Backup v17 database
```bash
cp ae.db ae_v17_backup.db
```

### Step 2: Run migrations
```bash
python scripts/run_migrations.py
```

### Step 3: Validate migrations
```bash
python tests/test_migrations.py
```

### Step 4: Backfill data
```bash
python scripts/migrate_v17_to_v18.py
```

## Phase 2: Test Agents (Week 2)
[Detailed steps...]

## Phase 3: Deploy to Production (Week 7)
[Detailed steps...]
```

#### docs/v18_ARCHITECTURE.md

```markdown
# Article Eater v18 Architecture

## Overview
v18 implements the "Epistemological Engine" with:
- Dual hierarchy (Findings + Mechanisms) with edge types
- Set of Support (paper-type-specific confidence)
- HITL workflow (human approval of proposals)

## Database Schema
[Complete ERD with finding_links table]

## Agent Architecture
[Flowchart of Agent_Classifier → Agent_PromptRouter → extraction]

## Confidence Calculation
[Formulas for each paper type]

## GUI Architecture
[Librarian vs Synthesizer split]
```

---

## VARIABLE DEFINITIONS FOR AI

AI must understand these v18-specific concepts:

```python
# Paper Types (from Agent_Classifier)
PAPER_TYPES = [
    "experimental_rct",      # Randomized controlled trial
    "observational",         # Cohort, cross-sectional, etc.
    "meta_analysis",         # Systematic review with pooled stats
    "theoretical",           # Conceptual framework, no empirical data
    "qualitative",           # Interviews, ethnography, etc.
    "review"                 # Narrative review
]

# Link Types (in finding_links table)
LINK_TYPES = [
    "CAUSAL",               # Empirical effect: Plants → Cortisol↓
    "TAXONOMIC"             # Definitional rollup: Cortisol↓ → Stress
]

# Set of Support Fields (varies by paper type)
SET_OF_SUPPORT_RCT = {
    "N": int,               # Sample size
    "p": float,             # P-value
    "d": float,             # Cohen's d (effect size)
    "method": str,          # "RCT", "quasi-experimental"
    "ci_lower": float,      # 95% CI lower bound
    "ci_upper": float       # 95% CI upper bound
}

SET_OF_SUPPORT_META = {
    "k_studies": int,       # Number of studies
    "N_total": int,         # Total participants
    "pooled_effect": float, # Pooled effect size
    "ci_lower": float,
    "ci_upper": float,
    "i_squared": float      # Heterogeneity (0-100)
}

SET_OF_SUPPORT_THEORY = {
    "key_claims": list,          # Main theoretical claims
    "testable_predictions": list, # Falsifiable predictions
    "gap_solved": str            # What prior theories missed
}

# Confidence Sentinel Values
CONFIDENCE_VALUES = {
    "calculated": 0.0-1.0,       # Quantitative confidence
    "manual_required": -1.0      # Needs human judgment (HITL)
}
```

---

## QUALITY CHECKLIST FOR AI

Before delivering v18, AI should verify:

### Database
- [ ] finding_links table has link_type field with CHECK constraint
- [ ] papers table has paper_type field (JSON array)
- [ ] findings table has set_of_support field (JSON)
- [ ] Migration 008 backfills v17 parent_finding_id correctly
- [ ] Indexes created on all foreign keys

### Agents
- [ ] Agent_Classifier implements two-pass triage (Gemini's spec)
- [ ] Agent_PromptRouter handles hybrids (multiple prompts merged)
- [ ] Agent_Aggregator proposes meso-findings (HITL)
- [ ] Agent_Linker proposes mechanism links (HITL)

### Confidence
- [ ] ExperimentalSupport uses Gemini's exact formula
- [ ] MetaAnalysisSupport uses Gemini's exact formula
- [ ] TheoreticalSupport returns -1.0 (not quantified)
- [ ] SetOfSupportCalculator routes to correct class

### Prompts
- [ ] 5 prompt files exist (RCT, Theory, Meta, Obs, Qual)
- [ ] Each prompt extracts appropriate Set of Support fields
- [ ] RCT prompt emphasizes randomization + control
- [ ] Theory prompt emphasizes claims + predictions + gap
- [ ] Meta prompt emphasizes k, pooled_effect, I²

### GUI
- [ ] Librarian route has instant 7-panel access (pre-computed)
- [ ] Librarian has filters (PaperType, N > X, measure)
- [ ] Synthesizer route has HITL approval interface
- [ ] Synthesizer handles conf=-1.0 items (manual review)
- [ ] Templates use clear, academic language

### Documentation
- [ ] Deployment guide has step-by-step instructions
- [ ] Architecture doc explains dual hierarchy + edge types
- [ ] Testing plan covers all 7 weeks
- [ ] Troubleshooting doc has common issues + fixes

### Tests
- [ ] test_agents.py tests classification on 20 papers
- [ ] test_confidence.py validates formulas on known data
- [ ] test_finding_links.py queries CAUSAL vs TAXONOMIC
- [ ] test_migrations.py runs migrations on v17 backup

---

## HOW TO USE GENERATED V18 CODE

Once AI creates all files:

1. **Review for correctness**:
   - Compare to V18_IMPLEMENTATION_GUIDE_FINAL.md
   - Check database schema matches Gemini's spec
   - Validate confidence formulas match exactly

2. **Test migrations on v17 backup**:
   ```bash
   cp ae.db ae_test.db
   python scripts/run_migrations.py --db ae_test.db
   python tests/test_migrations.py --db ae_test.db
   ```

3. **Deploy phased**:
   - Week 1: Database only
   - Week 2: Agents only (test classification)
   - Week 3: Confidence (tune weights if needed)
   - Weeks 4-7: GUI + HITL

4. **Use governance to track**:
   - Log each week's session
   - Document tuning decisions (confidence weights)
   - Track issues and fixes

---

## EXAMPLE PROMPT TO NEW AI INSTANCE

**Copy this EXACTLY** when starting new session:

```
I need you to implement Article Eater v18 from complete specifications.

CONTEXT:
Article Eater is an evidence synthesis tool for Cognitive Neuroscience 
for Architecture (CNfA). It extracts structured data from papers to build 
Bayesian Belief Networks.

v17 has a critical flaw: parent_finding_id conflates CAUSAL and TAXONOMIC 
links, making BBN construction impossible.

v18 fixes this with finding_links table (link_type field) plus:
- Set of Support (paper-type-specific confidence)
- Agent_Classifier (detect RCT vs Theory vs Meta)
- Agent_PromptRouter (different prompts per type)
- HITL approval (human approves proposals)

I'm attaching:
1. V18_IMPLEMENTATION_GUIDE_FINAL.md (Gemini's definitive answers)
2. V18_SYNTHESIS_Complete_Analysis.md (critical analysis)
3. v17 codebase (what exists, what to extend)
4. Domain context (SYSTEM_VISION.md)
5. Governance kit (track implementation decisions)

YOUR TASK:
Generate complete v18 implementation:
- 4 SQL migrations (finding_links table, paper_type, set_of_support, backfill)
- 4 agent modules (Classifier, PromptRouter, Aggregator, Linker)
- 3 confidence classes (Experimental, Meta, Theoretical)
- 5 prompt templates (one per paper type)
- 2 new route modules (Librarian, Synthesizer)
- 4 documentation files (deployment, architecture, testing, troubleshooting)
- Test suite

CRITICAL REQUIREMENTS:
- finding_links table MUST have link_type field (CAUSAL vs TAXONOMIC)
- Confidence formulas MUST match Gemini's exact specifications
- Theoretical/Qualitative MUST return conf=-1.0 (HITL)
- Agent_Classifier MUST implement two-pass triage
- Templates MUST be production-ready (error handling, validation)

Start with database migrations, then move to agents.
Ask clarifying questions if anything is unclear.

Ready? Please read V18_IMPLEMENTATION_GUIDE_FINAL.md first, then confirm 
you understand the architecture before starting.
```

---

**This document + 8 files = Everything AI needs to build complete v18** 🚀