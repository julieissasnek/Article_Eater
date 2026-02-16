-- Migration 019: Add argumentation scheme fields to theory_claims
-- Sprint 1.1 / Task 1.1
-- Per Canonical Decisions Record (02-15_09), Decision 1
--
-- New fields support GapType.CRITICAL_QUESTION and GapType.ARGUMENT_ATTACK
-- gap detection by storing:
--   - argument_scheme: Walton argumentation scheme used (e.g., "argument from expert opinion")
--   - critical_questions: JSON array of CQs applicable to this scheme
--   - critical_questions_addressed: CQs that have been addressed in the paper
--   - critical_questions_unaddressed: CQs that remain open (gap candidates)

ALTER TABLE theory_claims ADD COLUMN argument_scheme TEXT;
ALTER TABLE theory_claims ADD COLUMN critical_questions TEXT;  -- JSON array
ALTER TABLE theory_claims ADD COLUMN critical_questions_addressed TEXT;  -- JSON array
ALTER TABLE theory_claims ADD COLUMN critical_questions_unaddressed TEXT;  -- JSON array

-- Index for querying claims by argumentation scheme
CREATE INDEX IF NOT EXISTS idx_theory_claims_scheme ON theory_claims(argument_scheme)
WHERE argument_scheme IS NOT NULL;

-- Also add to findings table for empirical claims that use argumentation
ALTER TABLE findings ADD COLUMN argument_scheme TEXT;
ALTER TABLE findings ADD COLUMN critical_questions TEXT;  -- JSON array

CREATE INDEX IF NOT EXISTS idx_findings_scheme ON findings(argument_scheme)
WHERE argument_scheme IS NOT NULL;
