═══════════════════════════════════════════════════════════════
Ports: Source-of-truth in contracts/ports.json.
  ARTICLE EATER V18 + GOVERNANCE - COMPLETE HANDOFF PACKAGE
═══════════════════════════════════════════════════════════════

Session Date: 2025-11-11
Claude Instance: One continuous session (6 hours)
Status: COMPLETE ✅

═══════════════════════════════════════════════════════════════
  📦 WHAT YOU HAVE
═══════════════════════════════════════════════════════════════

1. v18-handoff-package.zip (75KB)
   └─ 11 files ready for ChatGPT
   └─ Includes PROMPT_FOR_CHATGPT.md
   └─ Everything ChatGPT needs to build v18

2. governance-kit-v3 (already built by ChatGPT)
   └─ You mentioned you already had ChatGPT build this
   └─ If you need it rebuilt, see governance files in outputs/

═══════════════════════════════════════════════════════════════
  🎯 QUICK START (5 MINUTES)
═══════════════════════════════════════════════════════════════

STEP 1: Download
→ File: v18-handoff-package.zip
→ Location: /mnt/user-data/outputs/v18-handoff-package.zip

STEP 2: Go to ChatGPT
→ https://chat.openai.com
→ Start new chat

STEP 3: Upload ZIP
→ Drag v18-handoff-package.zip into ChatGPT
→ OR extract and upload all 11 files

STEP 4: Send Prompt
→ Open PROMPT_FOR_CHATGPT.md from the ZIP
→ Copy entire contents
→ Paste into ChatGPT

STEP 5: Say YES
→ ChatGPT will confirm understanding
→ You say "YES" to begin
→ Wait 4-6 hours for generation

═══════════════════════════════════════════════════════════════
  📖 KEY FILES TO READ
═══════════════════════════════════════════════════════════════

READ FIRST:
→ HANDOFF_INSTRUCTIONS_FINAL.md (in outputs/)
  Complete guide to using the ZIP

READ SECOND:
→ PROMPT_FOR_CHATGPT.md (in ZIP)
  What you'll send to ChatGPT

READ THIRD:
→ V18_IMPLEMENTATION_GUIDE_FINAL.md (in ZIP)
  Gemini's definitive answers (for reference during review)

═══════════════════════════════════════════════════════════════
  ⚠️ CRITICAL CHECKS (When ChatGPT Finishes)
═══════════════════════════════════════════════════════════════

1. finding_links Table:
   ✓ Has link_type field
   ✓ CHECK constraint: link_type IN ('CAUSAL', 'TAXONOMIC')

2. RCT Confidence Formula:
   ✓ conf = (0.4 * score_N) + (0.3 * score_p) + (0.3 * score_d)
   ✓ Weights MUST be exactly: 0.4, 0.3, 0.3

3. Meta Confidence Formula:
   ✓ conf = (0.3 * score_k) + (0.5 * score_CI) + (0.2 * score_I2)
   ✓ Weights MUST be exactly: 0.3, 0.5, 0.2

4. Theoretical Confidence:
   ✓ return -1.0
   ✓ MUST be exactly -1.0 (not 0, not None)

═══════════════════════════════════════════════════════════════
  📊 TIMELINE
═══════════════════════════════════════════════════════════════

TODAY (10 min):
- Download ZIP
- Upload to ChatGPT
- Send prompt

TOMORROW (8 hours):
- ChatGPT generates v18 code
- You review each phase
- Verify critical checks

DAY 3 (4 hours):
- Test migrations on v17 backup
- Run test suite
- Fix any issues

DAY 4 (4 hours):
- Integrate with v17 codebase
- Prepare for deployment

WEEKS 1-7 (30-40 hours):
- Deploy phased (database → agents → GUI)
- Log in governance
- Tune as needed

═══════════════════════════════════════════════════════════════
  🏆 SUCCESS CRITERIA
═══════════════════════════════════════════════════════════════

You'll know it worked when:

✓ finding_links table exists with link_type field
✓ Confidence formulas match Gemini's spec EXACTLY
✓ Migrations run on v17 backup without errors
✓ Tests pass: pytest tests/
✓ Can query CAUSAL links separately from TAXONOMIC
✓ Ready to deploy Week 1 (database migration)

═══════════════════════════════════════════════════════════════
  📞 SUPPORT
═══════════════════════════════════════════════════════════════

If ChatGPT gets stuck:
→ Point to specific section in AI_HANDOFF_BUILD_V18_REPO.md
→ Show example from V18_IMPLEMENTATION_GUIDE_FINAL.md

If formulas don't match:
→ STOP immediately
→ Show ChatGPT the exact formula from the guide
→ Ask it to regenerate

If you need review:
→ Upload generated code to original Claude (this instance)
→ Say: "Review v18 for correctness"
→ I'll check against specifications

═══════════════════════════════════════════════════════════════
  📦 ALL OUTPUT FILES (29 total)
═══════════════════════════════════════════════════════════════

HANDOFF PACKAGE (most important):
✓ v18-handoff-package.zip (75KB) - For ChatGPT
✓ HANDOFF_INSTRUCTIONS_FINAL.md - How to use the ZIP
✓ README_FINAL.txt (this file) - Quick reference

V18 SPECIFICATIONS:
✓ V18_IMPLEMENTATION_GUIDE_FINAL.md (29KB) - THE v18 spec
✓ V18_SYNTHESIS_Complete_Analysis.md (29KB)
✓ FINAL_DECISION_v18_GO.md (6KB)

V18 HANDOFF DOCS:
✓ AI_HANDOFF_BUILD_V18_REPO.md (37KB)
✓ HANDOFF_CHECKLIST_V18.md (18KB)

GOVERNANCE SPECIFICATIONS:
✓ GOVERNANCE_KIT_v3_Repo_Agnostic.md (25KB)
✓ CONVERSATION_LEDGER.template.yml (5KB)
✓ SYSTEM_VISION.template.md (9KB)
✓ install.sh (3KB)
✓ conversation_guard.py (5KB)

GOVERNANCE HANDOFF DOCS:
✓ AI_HANDOFF_BUILD_GOVERNANCE_REPO.md (15KB)
✓ HANDOFF_CHECKLIST.md (11KB)

MASTER DOCS:
✓ MASTER_HANDOFF_GUIDE.md (28KB) - Orchestration
✓ COMPLETE_FILE_MANIFEST.md (17KB) - File catalog
✓ SESSION_SUMMARY_FINAL.md (14KB) - What we did

CONTEXT:
✓ SYSTEM_VISION.md (20KB) - Article Eater overview
✓ CONVERSATION_LEDGER.yml (12KB) - Example ledger

PLUS: Various other supporting files (analysis, earlier versions)

═══════════════════════════════════════════════════════════════
  🎯 NEXT STEP
═══════════════════════════════════════════════════════════════

Download this file:
→ v18-handoff-package.zip

Read this file:
→ HANDOFF_INSTRUCTIONS_FINAL.md

Then follow the Quick Start above.

═══════════════════════════════════════════════════════════════
  ✅ READY TO BUILD THE EPISTEMOLOGICAL ENGINE! 🚀
═══════════════════════════════════════════════════════════════

Questions? I still have 99K tokens (52%) available.
