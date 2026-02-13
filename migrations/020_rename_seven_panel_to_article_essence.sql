-- Migration: Rename seven_panel to article_essence
-- Date: 2026-02-11
-- Rationale: "seven_panel" is outdated naming from when extraction
-- focused on 7 specific fields. Now we have 16+ extraction templates
-- for different article types. "article_essence" better captures
-- the purpose: extracting the essential structured information from articles.

-- Rename the table
ALTER TABLE seven_panel RENAME TO article_essence;

-- Note: Column names remain the same as they describe content, not structure:
--   hypothesis, population_context, manipulations_measures,
--   findings_effect, limitations_confounds, design_type, stats_effect_sizes
-- These columns may be extended or made nullable for different article types.
