
PHASE 1 IMPLEMENTATION PACKAGE

Article Eater v16.0 → v17.0 "Dual-Hierarchy" Upgrade

Date: November 9, 2025

Implementation Time: 18-24 hours

Deliverables: 4 SQL Migrations, 1 Enhanced Prompt, 2 Updated Python Modules

PACKAGE CONTENTS

SQL Database Migrations - Destructive refactor from rules to findings and creation of mechanisms and links tables.

Enhanced 7-Panel Extraction (v17) - New Panel 6 prompt for bifurcated extraction.

Meta-Review Module (v17) - meta_review.py updated for new model.

Explanation Processing Module - tasks.py logic to populate new tables.

COMPONENT 1: DATABASE SCHEMA MIGRATIONS

CRITICAL WARNING: This is a destructive migration. Run 001_... before 003_... and 004_.... A data backfill script is required (see v17_Deployment_Plan.md).

File: migrations/001_refactor_rules_to_findings.sql

-- ============================================================================
-- Migration 001: Refactor 'rules' to 'findings'
-- Article Eater v17.0 (Dual-Hierarchy)
-- This is a DESTRUCTIVE migration.
-- It removes the v16 'mechanism' columns to prepare for the new model.
-- ============================================================================

-- 1. Rename the table from 'rules' to 'findings'
ALTER TABLE rules RENAME TO findings;

-- 2. Rename columns
ALTER TABLE findings RENAME COLUMN rule_level TO finding_level;
ALTER TABLE findings RENAME COLUMN parent_rule_id TO parent_finding_id;

-- 3. (Optional but Recommended) Create a temporary backup of mechanism data
--    This data will be migrated to the new tables by a Python script.
CREATE TABLE _temp_v16_mechanism_backup AS
SELECT 
    id AS finding_id, 
    mechanism, 
    mechanism_description, 
    theoretical_framework, 
    framework_references
FROM findings
WHERE mechanism IS NOT NULL OR theoretical_framework IS NOT NULL;

-- 4. Drop the conflated mechanism columns (DESTRUCTIVE)
--    These columns are moving to the new 'mechanisms' and 'links' tables.
ALTER TABLE findings DROP COLUMN mechanism;
ALTER TABLE findings DROP COLUMN mechanism_description;
ALTER TABLE findings DROP COLUMN theoretical_framework;
ALTER TABLE findings DROP COLUMN framework_references;

-- 5. Update indexes
DROP INDEX idx_rules_level;
DROP INDEX idx_rules_parent;
DROP INDEX idx_rules_measure;
DROP INDEX idx_rules_framework;
CREATE INDEX idx_findings_level ON findings(finding_level);
CREATE INDEX idx_findings_parent ON findings(parent_finding_id);
CREATE INDEX idx_findings_measure ON findings(operational_measure);

-- 6. Update v16 constraints (if they exist)
ALTER TABLE findings DROP CONSTRAINT check_micro_has_measure;
ALTER TABLE findings ADD CONSTRAINT check_micro_has_measure
  CHECK (finding_level != 'micro' OR operational_measure IS NOT NULL);

PRAGMA foreign_keys=off; -- SQLite specific
-- Recreate table to drop columns if 'DROP COLUMN' is not supported
CREATE TABLE findings_new (
    id INTEGER PRIMARY KEY,
    finding_level VARCHAR(10),
    parent_finding_id INTEGER REFERENCES findings(id),
    consequent VARCHAR(255),
    antecedents TEXT,
    weight REAL,
    operational_measure VARCHAR(100),
    measure_type VARCHAR(50),
    measure_direction VARCHAR(20),
    construct_measured VARCHAR(100),
    p_value REAL,
    effect_size REAL,
    effect_size_type VARCHAR(20),
    sample_size INTEGER,
    statistical_test VARCHAR(100),
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,
    confidence_triangulation REAL,
    confidence_effect_strength REAL,
    confidence_sample_size REAL,
    confidence_consistency REAL,
    num_child_rules INTEGER DEFAULT 0,
    operational_measures_used TEXT,
    total_sample_size INTEGER,
    CONSTRAINT check_micro_has_measure CHECK (finding_level != 'micro' OR operational_measure IS NOT NULL)
);

INSERT INTO findings_new (id, finding_level, parent_finding_id, consequent, antecedents, weight, operational_measure, measure_type, measure_direction, construct_measured, p_value, effect_size, effect_size_type, sample_size, statistical_test, confidence_interval_lower, confidence_interval_upper, confidence_triangulation, confidence_effect_strength, confidence_sample_size, confidence_consistency, num_child_rules, operational_measures_used, total_sample_size)
SELECT id, finding_level, parent_finding_id, consequent, antecedents, weight, operational_measure, measure_type, measure_direction, construct_measured, p_value, effect_size, effect_size_type, sample_size, statistical_test, confidence_interval_lower, confidence_interval_upper, confidence_triangulation, confidence_effect_strength, confidence_sample_size, confidence_consistency, num_child_rules, operational_measures_used, total_sample_size
FROM findings;

DROP TABLE findings;
ALTER TABLE findings_new RENAME TO findings;

CREATE INDEX idx_findings_level ON findings(finding_level);
CREATE INDEX idx_findings_parent ON findings(parent_finding_id);
CREATE INDEX idx_findings_measure ON findings(operational_measure);
CREATE INDEX idx_findings_construct ON findings(construct_measured);

PRAGMA foreign_keys=on; -- SQLite specific


File: migrations/002_add_paper_table.sql

-- ============================================================================
-- Migration 002: Add 'papers' table
-- Article Eater v17.0 (Dual-Hierarchy)
-- Required for linking findings and mechanisms to provenance.
-- ============================================================================

CREATE TABLE papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doi VARCHAR(255) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT, -- JSON array
    year INTEGER,
    journal VARCHAR(255),
    abstract TEXT,
    -- Internal reference to the job that ingested this paper
    ingested_by_job_id VARCHAR(255)
);

CREATE INDEX idx_papers_doi ON papers(doi);
CREATE INDEX idx_papers_year ON papers(year);

-- This migration must be run *before* 004, which references it.
-- A data backfill script will be needed to populate this table from
-- existing `findings` provenance and `shortlist.json` files.


File: migrations/003_add_mechanism_hierarchy.sql

-- ============================================================================
-- Migration 003: Create 'mechanisms' table
-- Article Eater v17.0 (Dual-Hierarchy)
-- This NEW table stores the "Why" (explanatory hierarchy).
-- ============================================================================

CREATE TABLE mechanisms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- The name of the mechanism
    name VARCHAR(255) NOT NULL UNIQUE, -- e.g., "Perceptual Fluency"
    
    -- A clear definition
    description TEXT,
    
    -- The level in the hierarchy
    mechanism_level VARCHAR(50) NOT NULL, -- 'theory', 'framework', 'mechanism', 'process'
    
    -- Self-referencing key for hierarchy
    parent_mechanism_id INTEGER REFERENCES mechanisms(id) ON DELETE SET NULL,
    
    -- Key citations that *define* this mechanism
    defining_citations TEXT -- JSON array of APA citations
);

CREATE INDEX idx_mechanisms_parent ON mechanisms(parent_mechanism_id);
CREATE INDEX idx_mechanisms_level ON mechanisms(mechanism_level);
CREATE UNIQUE INDEX idx_mechanisms_name ON mechanisms(name);


File: migrations/004_add_explanation_links.sql

-- ============================================================================
-- Migration 004: Create 'finding_mechanism_links' table
-- Article Eater v17.0 (Dual-Hierarchy)
-- This NEW table is the "Bridge" connecting "What" to "Why".
-- ============================================================================

CREATE TABLE finding_mechanism_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign key to the empirical finding
    finding_id INTEGER NOT NULL,
    
    -- Foreign key to the theoretical mechanism
    mechanism_id INTEGER NOT NULL,
    
    -- Foreign key to the *paper* that makes this claim
    paper_id INTEGER NOT NULL,
    
    -- How strongly does the paper claim this link?
    evidence_strength VARCHAR(50) NOT NULL, -- 'strong', 'moderate', 'speculative'
    
    -- The exact quote from the paper proposing this link
    snippet TEXT,

    FOREIGN KEY(finding_id) REFERENCES findings(id) ON DELETE CASCADE,
    FOREIGN KEY(mechanism_id) REFERENCES mechanisms(id) ON DELETE CASCADE,
    FOREIGN KEY(paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    
    -- A paper should only link a finding to a mechanism once
    UNIQUE(finding_id, mechanism_id, paper_id)
);

CREATE INDEX idx_links_finding ON finding_mechanism_links(finding_id);
CREATE INDEX idx_links_mechanism ON finding_mechanism_links(mechanism_id);
CREATE INDEX idx_links_paper ON finding_mechanism_links(paper_id);


COMPONENT 2: ENHANCED 7-PANEL EXTRACTION (v17)

File: prompts/7_panel_extraction_v17_dual_hierarchy.txt

ARTICLE EATER v17.0: DUAL-HIERARCHY EXTRACTION
(Findings & Mechanisms)

================================================================================
CRITICAL INSTRUCTIONS: DUAL-HIERARCHY EXTRACTION
================================================================================

Your task is to extract structured data for a "Dual-Hierarchy" model.
This model separates:
1.  **FINDINGS (Panel 5):** The "What." Empirical, observable results.
    (e.g., "Plants -> Cortisol ↓")
2.  **MECHANISMS (Panel 6):** The "Why." Theoretical explanations for those findings.
    (e.g., "Biophilia Hypothesis," "Perceptual Fluency")

**Panel 5 and Panel 6 are now independent and must be populated separately.**

================================================================================
PANEL 1: CITATION INFORMATION (No Change)
PANEL 2: RESEARCH FOCUS (No Change)
PANEL 3: STUDY CONTEXT (No Change)
PANEL 4: METHODOLOGY (No Change)
================================================================================
... (Panels 1-4 are identical to the v16 prompt [cite: 217-220]) ...
================================================================================

================================================================================
PANEL 5: FINDINGS (THE "WHAT")
================================================================================

*** CRITICAL: Extract EVERY operational measure separately ***
This panel populates the `findings` table.
DO NOT include theoretical explanations or mechanisms here.

For EACH outcome variable measured, provide:
1.  The CONSTRUCT being assessed (stress, anxiety, attention, mood, etc.)
2.  The OPERATIONAL MEASURE (cortisol, heart_rate, STAI score, etc.)
3.  The MEASURE TYPE (physiological, behavioral, self_report)
4.  The DIRECTION of effect (increase, decrease, stable)
5.  COMPLETE STATISTICAL DETAILS (p-value, effect size, N, etc.)

OUTPUT FORMAT:
{
  "main_finding_summary": "Curved walls reduced anxiety compared to angular walls",
  "operational_findings": [
    {
      "antecedent": "curved_walls",
      "consequent_construct": "anxiety",
      "operational_measure": "salivary_cortisol",
      "measure_type": "physiological",
      "measure_direction": "decrease",
      "statistical_details": {
        "p_value": 0.03,
        "effect_size": 0.52,
        "effect_size_type": "cohen_d",
        "sample_size": 68
      }
    },
    {
      "antecedent": "curved_walls",
      "consequent_construct": "anxiety",
      "operational_measure": "state_anxiety_inventory",
      "measure_type": "self_report",
      "measure_direction": "decrease",
      "statistical_details": {
        "p_value": 0.01,
        "effect_size": 0.64,
        "effect_size_type": "cohen_d",
        "sample_size": 68
      }
    }
  ]
}

================================================================================
PANEL 6: MECHANISMS & EXPLANATIONS (THE "WHY")
================================================================================

*** CRITICAL: This panel is completely new. ***
It populates the `mechanisms` and `finding_mechanism_links` tables.
Identify all theoretical constructs used to EXPLAIN the findings from Panel 5.

Provide two separate JSON arrays:

**Part 1: `mechanisms_identified`**
List all unique theoretical constructs mentioned in the paper.
Define parent-child relationships if the paper specifies them.

**Part 2: `explanation_links`**
This is the "Bridge." For each mechanism, state which FINDING (from Panel 5) it
is used to explain.

OUTPUT FORMAT:
{
  "discussion_main_points": [
    "Curved forms reduce anxiety through reduced prediction error",
    "Results align with evolutionary preferences for natural, organic shapes",
    "Limitations: Lab setting..."
  ],

  "mechanisms_identified": [
    {
      "name": "Predictive Processing",
      "level": "theory",
      "parent": null,
      "definition": "A unified brain theory where the brain minimizes prediction error."
    },
    {
      "name": "Perceptual Fluency",
      "level": "mechanism",
      "parent": "Predictive Processing",
      "definition": "The ease with which a stimulus is processed."
    },
    {
      "name": "Biophilia Hypothesis",
      "level": "theory",
      "parent": null,
      "definition": "The innate human affinity for natural forms."
    },
    {
      "name": "Statistical Fractal Detection",
      "level": "process",
      "parent": "Biophilia Hypothesis",
      "definition": "Subconscious visual processing of fractal geometries."
    }
  ],
  
  "explanation_links": [
    {
      "finding_consequent": "anxiety_reduction",
      "explained_by_mechanism": "Perceptual Fluency",
      "evidence_strength": "moderate",
      "snippet": "We propose this reduction in anxiety is due to the high perceptual fluency of curved forms, which reduces prediction error (Friston, 2010)."
    },
    {
      "finding_consequent": "anxiety_reduction",
      "explained_by_mechanism": "Biophilia Hypothesis",
      "evidence_strength": "speculative",
      "snippet": "Alternatively, this effect could be explained by an innate biophilic preference for non-angular, organic shapes (Wilson, 1984)."
    }
  ]
}

================================================================================
PANEL 7: KEY REFERENCES (No Change)
================================================================================
... (Identical to v16 prompt [cite: 224]) ...
================================================================================

FINAL OUTPUT FORMAT:
Return a SINGLE JSON object with all 7 panels:
{
  "panel_1_citation": { ... },
  "panel_2_research_focus": { ... },
  "panel_3_study_context": { ... },
  "panel_4_methodology": { ... },
  "panel_5_findings": { ... },
  "panel_6_discussion": { ... },
  "panel_7_references": { ... }
}


COMPONENT 3: META-REVIEW MODULE (v17)

File: meta_review.py (Modified)

The core logic of aggregate_to_meso is unchanged, but it now operates on findings instead of rules and no longer contains any logic related to mechanisms.

"""
Meta-Review Aggregation Module (v17)
=====================================
Aggregates micro-findings into meso-findings.
Mechanism processing is now handled in tasks.py.
"""

from typing import List, Dict, Set, Tuple, Optional
from models import Finding  # <-- Renamed from Rule
from database import session_scope
import json
import logging

logger = logging.getLogger(__name__)

# Construct Mapping (Unchanged) [cite: 249-251]
STRESS_MEASURES = {'cortisol', 'heart_rate', 'blood_pressure', ...}
ATTENTION_MEASURES = {'reaction_time', 'accuracy', ...}
MOOD_MEASURES = {'panas_positive', 'panas_negative', ...}
CONSTRUCT_MAP = {
    'stress_reduction': STRESS_MEASURES,
    'attention_performance': ATTENTION_MEASURES,
    'affective_state': MOOD_MEASURES
}

def find_aggregation_opportunities() -> List[List[Finding]]:
    """
    Identify groups of micro-findings that should be aggregated.
    """
    with session_scope() as session:
        # Query 'findings' table for 'micro' level
        micro_findings = session.query(Finding).filter_by(finding_level='micro').all()
        
        # ... (Grouping logic by antecedent is identical to v16) [cite: 254]
        
        grouped_by_antecedent = {}
        for finding in micro_findings:
            key = finding.antecedents
            if key not in grouped_by_antecedent:
                grouped_by_antecedent[key] = []
            grouped_by_antecedent[key].append(finding)
        
        opportunities = []
        for rules in grouped_by_antecedent.values():
            if len(rules) >= 2:
                construct = infer_construct_from_measures(rules)
                if construct and construct != "unknown_construct":
                    opportunities.append(rules)
        
        return opportunities

def aggregate_to_meso(micro_findings: List[Finding]) -> Finding:
    """
    Create a meso-finding by aggregating multiple micro-findings.
    """
    if not micro_findings:
        raise ValueError("Cannot aggregate empty micro-finding list")
    
    construct = infer_construct_from_measures(micro_findings)
    antecedents = micro_findings[0].antecedents
    
    # Calculate confidence (identical to v16) [cite: 257-258]
    confidence_scores = calculate_meta_confidence(micro_findings)
    total_confidence = sum(confidence_scores.values())
    
    measures_used = list(set(r.operational_measure for r in micro_findings if r.operational_measure))
    total_n = sum(r.sample_size or 0 for r in micro_findings)
    
    # Create meso-finding (NO mechanism fields)
    meso_finding = Finding(
        consequent=construct,
        antecedents=antecedents,
        weight=total_confidence,
        finding_level='meso',
        rule_type='meta_aggregated', # Kept for compatibility
        num_child_rules=len(micro_findings),
        operational_measures_used=json.dumps(measures_used),
        total_sample_size=total_n,
        confidence_triangulation=confidence_scores['triangulation'],
        confidence_effect_strength=confidence_scores['effect_strength'],
        confidence_sample_size=confidence_scores['sample_size'],
        confidence_consistency=confidence_scores['consistency']
    )
    
    logger.info(f"Created meso-finding: {antecedents} -> {construct} (conf={total_confidence:.2f})")
    
    # Note: Linking children (setting parent_finding_id) is done
    # by the calling function in the deployment plan's script.
    
    return meso_finding

def infer_construct_from_measures(rules: List[Finding]) -> Optional[str]:
    # ... (Identical to v16) [cite: 256]
    measures = {r.operational_measure.lower() for r in rules if r.operational_measure}
    for construct, measure_set in CONSTRUCT_MAP.items():
        if len(measures & measure_set) >= 2:
            return construct
    return "unknown_construct"


def calculate_meta_confidence(rules: List[Finding]) -> Dict[str, float]:
    # ... (Identical to v16) [cite: 257-258]
    unique_measures = len(set(r.operational_measure for r in rules if r.operational_measure))
    triangulation = min(unique_measures / 4.0, 1.0) * 0.4
    effect_sizes = [r.effect_size for r in rules if r.effect_size]
    avg_effect = sum(effect_sizes) / len(effect_sizes) if effect_sizes else 0.5
    effect_strength = min(avg_effect / 0.8, 1.0) * 0.3
    total_n = sum(r.sample_size or 0 for r in rules)
    sample_strength = min(total_n / 200.0, 1.0) * 0.2
    directions = [r.measure_direction for r in rules if r.measure_direction]
    direction_consistent = len(set(directions)) == 1 if directions else False
    consistency = 0.1 if direction_consistent else 0.0
    
    return {
        'triangulation': triangulation,
        'effect_strength': effect_strength,
        'sample_size': sample_strength,
        'consistency': consistency
    }


COMPONENT 4: EXPLANATION PROCESSING MODULE

File: tasks.py (New Logic)

This new logic runs after Panel 5 (Findings) have been created. It processes Panel 6 to populate the new tables.

"""
tasks.py (v17 - Excerpt)
New logic for processing Panel 6 and populating
the mechanism and link tables.
"""

from models import Finding, Mechanism, FindingMechanismLink, Paper
from database import session_scope
import logging

logger = logging.getLogger(__name__)

def process_v17_extraction(panel_data: dict, job_id: str):
    """
    Main task to process the full 7-panel v17 extraction.
    """
    
    # --- 1. Get or Create Paper ---
    # This logic must be robust. Assumes a helper function.
    paper = get_or_create_paper(panel_data['panel_1_citation'], job_id)
    
    # --- 2. Process Panel 5 (Findings) ---
    # This creates the Micro-Findings
    panel_5 = panel_data.get('panel_5_findings', {})
    created_findings = []
    
    with session_scope() as session:
        for finding_data in panel_5.get('operational_findings', []):
            new_finding = Finding(
                finding_level='micro',
                consequent=finding_data['consequent_construct'],
                antecedents=json.dumps([finding_data['antecedent']]),
                operational_measure=finding_data['operational_measure'],
                measure_type=finding_data['measure_type'],
                measure_direction=finding_data['measure_direction'],
                p_value=finding_data['statistical_details'].get('p_value'),
                effect_size=finding_data['statistical_details'].get('effect_size'),
                sample_size=finding_data['statistical_details'].get('sample_size'),
                # ... etc ...
            )
            session.add(new_finding)
            created_findings.append(new_finding)
        
        session.commit()
        
        # --- 3. Process Panel 6 (Mechanisms & Links) ---
        # This is the new, critical v17 logic
        panel_6 = panel_data.get('panel_6_discussion', {})
        
        # Use a new session to handle mechanism creation and linking
        process_panel_6_explanations(
            session=session,
            panel_6_data=panel_6,
            paper_id=paper.id,
            job_findings=created_findings
        )
        session.commit()

    # --- 4. Run Meso-Finding Aggregation ---
    # This is the call to meta_review.py, which now runs
    # on the micro-findings just created.
    # ... (call aggregate_all_micro_findings() here) ...


def process_panel_6_explanations(session, panel_6_data: dict, paper_id: int, job_findings: List[Finding]):
    """
    Parses Panel 6 to populate 'mechanisms' and 'finding_mechanism_links'.
    """
    
    # 1. Create/Update Mechanisms
    mechanisms_in_paper = {} # Cache {name: id}
    
    for mech_data in panel_6_data.get('mechanisms_identified', []):
        name = mech_data.get('name')
        if not name:
            continue
            
        # Find existing or create new
        mechanism = session.query(Mechanism).filter_by(name=name).first()
        if not mechanism:
            mechanism = Mechanism(
                name=name,
                description=mech_data.get('definition'),
                mechanism_level=mech_data.get('level', 'mechanism')
            )
            session.add(mechanism)
            session.flush() # Get ID
        
        mechanisms_in_paper[name] = mechanism.id
    
    # Handle parent-child links (second pass)
    for mech_data in panel_6_data.get('mechanisms_identified', []):
        parent_name = mech_data.get('parent')
        if parent_name:
            child_id = mechanisms_in_paper.get(mech_data.get('name'))
            parent_id = mechanisms_in_paper.get(parent_name)
            
            if child_id and parent_id:
                child_mech = session.query(Mechanism).get(child_id)
                if child_mech and not child_mech.parent_mechanism_id:
                    child_mech.parent_mechanism_id = parent_id
    
    # 2. Create Explanation Links
    for link_data in panel_6_data.get('explanation_links', []):
        finding_consequent = link_data.get('finding_consequent')
        mechanism_name = link_data.get('explained_by_mechanism')
        
        if not finding_consequent or not mechanism_name:
            continue
            
        # Find the mechanism ID
        mechanism_id = mechanisms_in_paper.get(mechanism_name)
        if not mechanism_id:
            logger.warning(f"Paper {paper_id} links to unknown mechanism: {mechanism_name}")
            continue
            
        # Find all findings from this job that match the consequent
        matching_findings = [f for f in job_findings if f.consequent == finding_consequent]
        
        for finding in matching_findings:
            # Create the link
            new_link = FindingMechanismLink(
                finding_id=finding.id,
                mechanism_id=mechanism_id,
                paper_id=paper_id,
                evidence_strength=link_data.get('evidence_strength', 'speculative'),
                snippet=link_data.get('snippet')
            )
            session.add(new_link)
            logger.info(f"Linking Finding {finding.id} to Mechanism {mechanism_id} (Paper {paper_id})")

# ... (Helper function get_or_create_paper) ...
def get_or_create_paper(citation_data: dict, job_id: str) -> Paper:
    # ... (Logic to find paper by DOI or create new one) ...
    pass