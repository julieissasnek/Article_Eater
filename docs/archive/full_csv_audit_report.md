# Sprint D.4: Full CSV Audit Report

## 1. Overview
- **Total Rows:** 171840
- **Total Papers:** 386
- **Source File:** `data/production/realtime_pdf_confirmed_rows.csv`

## 2. Source Breakdown
- **pdf_discourse_scan:** 159456 (92.8%)
- **codex_pdfplumber:** 12384 (7.2%)

## 3. Table Extraction Health
- **Unique Tables Detected:** 2607
- **Avg Rows Per Table:** 4.75
- **Tables with ≥1 Resolved Env Variable:** 2607
- **Papers WITHOUT Extracted Tables:** 154

## 4. Data Quality Issues
- **Rows where Env Var == Outcome Var:** 7142
- **Low Confidence Env Resolutions (<0.3):** 6258
- **Domain Inferred Resolutions:** 6248

## 5. Discourse Classification
- **inter_article_relation:** 96817
- **theory_link:** 62639
- **finding:** 12175
- **sample:** 178
- **methodology:** 29
- **effect:** 2

## 6. High Confidence Variable Pairs (Sample)
Total High Confidence Pairs (both > 0.5): 682
Top 20 frequent pairs:
- social -> social: 53
- cognitive emotional -> cognitive: 42
- cognitive -> cognitive: 29
- working -> working memory: 20
- architecture -> wellbeing: 18
- city mental health -> health: 16
- natural light -> health: 14
- construction -> cognitive: 12
- wood -> wood: 11
- wood -> plant wood: 9
- affecting -> affecting: 8
- light -> sleep: 8
- open plan -> stress: 8
- table -> pleasant: 8
- light level -> performance: 7
- spatial memory -> memory: 6
- yellowish green -> attention: 6
- good -> good: 5
- natural light -> wellbeing: 5
- cognitive score -> cognitive: 4
