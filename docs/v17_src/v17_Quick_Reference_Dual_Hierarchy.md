
Quick Reference: The v17 Dual-Hierarchy Model

Article Eater v16.0 → v17.0 Upgrade Requirements

Date: November 9, 2025
Concept: Separating Findings (The "What") from Mechanisms (The "Why")

THE CORE PROBLEM (in v16)

The v16 model [cite: 1-788] conflates causal findings with theoretical explanations. A "rule" for "Plants -> Stress Reduction" would have a mechanism field set to "Biophilia Hypothesis." This is a category error. Biophilia is the proposed explanation for the observed finding.

v16 Model (Conflated):

[RULE: Plants -> Stress Reduction]
  - confidence: 0.89
  - mechanism: "Biophilia Hypothesis"  <-- PROBLEM: Conflates finding with explanation
  - children: [micro-rule-1, micro-rule-2]


THE v17 SOLUTION: DUAL-HIERARCHY

v17 separates this into two distinct hierarchies, connected by a "bridge" table.

The Finding Hierarchy (The "What")

The Mechanism Hierarchy (The "Why")

The Explanation Link (The "Bridge")

1. THE FINDING HIERARCHY (The "What")

This is the repurposed rules table (now findings), which only tracks empirical observations and their aggregations.

Level 1: Micro-Finding (Operational/Sensor Level)

Definition: Single study, single operational measure.

Example: "Indoor plants → ↓ salivary cortisol (p<.05, d=0.42, N=32)" [cite: 75]

Database: findings table, finding_level='micro'

Level 2: Meso-Finding (Construct Level)

Definition: Aggregated from multiple Micro-Findings measuring the same construct.

Example: "Indoor plants → stress reduction (confidence: 0.89)" [cite: 75]

Database: findings table, finding_level='meso', with parent_finding_id pointing from Micro-Findings.

Level 3: Macro-Finding (Principle Level)

Definition: High-level empirical principles aggregated from Meso-Findings.

Example: "Biophilic design → improved wellbeing"

Database: findings table, finding_level='macro', with parent_finding_id pointing from Meso-Findings.

Database Schema: findings (Formerly rules)

CREATE TABLE findings (
    id INTEGER PRIMARY KEY,
    finding_level VARCHAR(10), -- 'micro', 'meso', 'macro'
    parent_finding_id INTEGER REFERENCES findings(id),
    consequent VARCHAR(255),
    antecedents TEXT, -- JSON array
    weight REAL, -- Confidence score
    
    -- Micro-Finding Details
    operational_measure VARCHAR(100),
    p_value REAL,
    effect_size REAL,
    sample_size INTEGER,
    
    -- Meso-Finding Details
    confidence_triangulation REAL,
    confidence_sample_size REAL
    -- ... etc
    -- CRITICALLY, 'mechanism' and 'theoretical_framework' are REMOVED
);


2. THE MECHANISM HIERARCHY (The "Why")

This is a new table (mechanisms) that only tracks theoretical constructs and their relationships.

Level 1: Theory (High-Level Framework)

Definition: A broad, overarching explanatory framework.

Example: "Predictive Processing (Friston)"

Database: mechanisms table, mechanism_level='theory'

Level 2: Mechanism (Mid-Level Construct)

Definition: A specific explanatory process derived from a theory.

Example: "Perceptual Fluency"

Database: mechanisms table, mechanism_level='mechanism', parent_mechanism_id points to "Predictive Processing".

Level 3: Process (Low-Level / Specific)

Definition: A concrete, often neuro-cognitive, process.

Example: "Reduced Prediction Error"

Database: mechanisms table, mechanism_level='process', parent_mechanism_id points to "Perceptual Fluency".

Database Schema: mechanisms (New)

CREATE TABLE mechanisms (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE, -- "Perceptual Fluency"
    description TEXT,
    mechanism_level VARCHAR(50), -- 'theory', 'mechanism', 'process'
    parent_mechanism_id INTEGER REFERENCES mechanisms(id),
    defining_citations TEXT -- JSON array of key papers
);


3. THE EXPLANATION LINK (The "Bridge")

This is a new many-to-many join table that connects Findings to Mechanisms. This is where provenance for claims is stored.

Definition: A record stating "Paper X claims that Finding Y is explained by Mechanism Z."
Example: "Paper A (Smith, 2020) links 'Plants -> Stress Reduction' to 'Statistical Fractal Detection' with 'speculative' strength."

Database Schema: finding_mechanism_links (New)

CREATE TABLE finding_mechanism_links (
    id INTEGER PRIMARY KEY,
    finding_id INTEGER NOT NULL REFERENCES findings(id),
    mechanism_id INTEGER NOT NULL REFERENCES mechanisms(id),
    paper_id INTEGER NOT NULL REFERENCES papers(id), -- Provenance!
    evidence_strength VARCHAR(50) NOT NULL, -- 'strong', 'moderate', 'speculative'
    snippet TEXT -- The quote from the paper making this link
);


(This model also requires a papers table, added in migrations/002_...)

VISUALIZATION: COMPLETE v17 MODEL

This model allows for competing explanations for the same finding.

                  +--------------------------+
                  |  THEORY:                |
                  |  Predictive Processing  |
                  +-----------+--------------+
                              | (explains)
                              v
+-----------------------+   +--------------------------+   +------------------------+
| MESO-FINDING:         |   | MECHANISM:               |   | THEORY:                |
| Curved Forms ->       |   | Perceptual Fluency       |   | Biophilia Hypothesis   |
| Anxiety Reduction     |   +--------------------------+   +-----------+------------+
| (Confidence: 0.91)    |                                              | (explains)
+----------+------------+                                              v
           |                                             +------------------------+
 (links)   | <---(Link 1: "speculative")---+               | MECHANISM:             |
           |   (Paper: Jones 2021)       |               | Statistical Fractals   |
           |                               |               +------------------------+
           +-----(Link 2: "moderate")----> |
               (Paper: Smith 2022)       |
                                         |
+-----------------------+                  |
| MESO-FINDING:         |                  |
| Plants ->             |                  |
| Stress Reduction      |                  |
| (Confidence: 0.89)    |                  |
+----------+------------+                  |
           |                               |
           +---(Link 3: "strong")--------> +
               (Paper: Smith 2022)


Key Insights from this Model:

The Curved Forms -> Anxiety Reduction finding is very strong (Conf: 0.91).

Its explanation is weak and contested. Jones (2021) speculates it's "Perceptual Fluency," while Smith (2022) provides moderate evidence it's also "Perceptual Fluency."

Smith (2022) also proposes that "Plants -> Stress Reduction" is strongly explained by "Statistical Fractals."

The system now correctly models the scientific debate, separating the reliability of the finding from the speculation about its cause.