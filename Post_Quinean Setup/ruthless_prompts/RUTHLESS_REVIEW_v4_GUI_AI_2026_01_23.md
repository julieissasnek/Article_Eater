# Ruthless System Review v4: GUI, Visual Evidence & AI Assistance

**Date**: January 23, 2026
**Version**: V22.0.0 (Post-Quinean)
**Focus**: Complete repository review with emphasis on GUIs and AI-assisted workflows

---

## Mission

You are conducting a **ruthless external review** of the Article Eater V22.0.0 system. Your task is to identify:

1. **GUI/Visual Deficiencies**: What's missing, broken, or confusing in the user interfaces?
2. **AI Assistance Gaps**: How could AI better help users understand and use the system?
3. **Integration Holes**: Where do components fail to work together?
4. **Usability Failures**: What blocks real users from accomplishing real tasks?
5. **Technical Debt**: What shortcuts will cause problems later?

**Be brutal. Be specific. Prioritize ruthlessly.**

---

## System Overview

Article Eater is a research tool that:
1. Extracts evidence-based design principles from academic literature
2. Organizes knowledge in a Quinean "web of belief" (coherentist epistemology)
3. Provides visual evidence galleries for claims (NEW in Sprint G1)
4. Targets architects, students, and researchers studying neuroarchitecture (CNFA)

---

## Files Included for Review

### Core Services
- `src/services/claim_gallery_builder.py` - Visual evidence gallery builder
- `src/services/web_of_belief.py` - Coherentist knowledge engine
- `src/services/bridge_warrants.py` - Knowledge transfer validation
- `src/services/extraction_to_web.py` - Claims to beliefs mapper

### API Routes
- `app/routes/galleries.py` - Gallery API endpoints
- `app/routes/query.py` - Natural language query processing
- `app/main.py` - FastAPI application

### Frontend (GUIs)
- `frontend/claim-gallery.html` - ClaimGallery visual evidence viewer
- `frontend/evidence-explorer.html` - Evidence network explorer
- `frontend/css/gallery-streamlit.css` - Streamlit-style theme
- `frontend/css/main.css` - Main application styles
- `frontend/js/api.js` - API client

### Schemas
- `contracts/ae_af/schemas/claim_gallery.v1.schema.json`
- `contracts/ae_af/schemas/image_feedback.v1.schema.json`
- `contracts/ae_af/schemas/gallery_selection_config.v1.schema.json`
- `contracts/ae_af/schemas/selection_log.v1.schema.json`

### Documentation
- `CLAUDE.md` - Project instructions
- `docs/ARCHITECTURE.md` - System architecture
- Panel review documents

### Tests
- `tests/test_claim_gallery_builder.py` - 25 tests, all passing

---

## Review Questions

### 1. GUI Completeness

**For each GUI file, assess:**

1. **Does it actually work?** Can a user complete their task end-to-end?
2. **Is it connected?** Does it integrate with the backend APIs?
3. **Is it discoverable?** Can users find features they need?
4. **Is it responsive?** Does it work on different screen sizes?
5. **Is it accessible?** Keyboard navigation? Screen readers? Color contrast?

**Specific questions:**

- Does `claim-gallery.html` actually load real galleries or just demo data?
- Does `evidence-explorer.html` connect to the web of belief?
- Are the CSS styles consistent across all GUIs?
- What happens on error? Are error states handled?
- Is there any loading state indication?

### 2. AI Assistance Opportunities

**Where could AI help users:**

1. **Understanding claims**: Can AI explain what a claim means in plain language?
2. **Interpreting evidence**: Can AI summarize why images were selected?
3. **Finding related content**: Can AI suggest related claims or studies?
4. **Catching mistakes**: Can AI flag when user feedback contradicts expert consensus?
5. **Onboarding**: Can AI guide new users through the system?

**Specific questions:**

- Is there any chat interface for asking questions about claims?
- Can users ask "why was this image excluded?"
- Is there natural language search over the claim gallery?
- Can AI generate human-readable summaries of selection logs?
- Is there AI-assisted feedback validation?

### 3. User Workflow Gaps

**For each user persona, trace their workflow:**

**Architect Workflow:**
1. Search for a design principle (e.g., "refuge edges")
2. View visual evidence supporting the principle
3. Understand when it applies and when it doesn't
4. Export for design documents

**Student Workflow:**
1. Learn about a construct (e.g., "what is prospect-refuge?")
2. See examples and counter-examples
3. Test understanding through comparison
4. Track learning progress

**Researcher Workflow:**
1. Explore the evidence base for a claim
2. Identify gaps and conflicts in the literature
3. Contribute feedback and corrections
4. Export for papers

**Questions:**

- Can each persona complete their workflow end-to-end?
- Where do workflows break down?
- What's the minimum viable path for each persona?

### 4. Integration Quality

**Check connections between:**

- Claim gallery builder ↔ Web of belief
- Gallery viewer ↔ Gallery API
- Feedback submission ↔ Active learning
- Evidence explorer ↔ Bridge warrants
- Query processing ↔ Gallery search

**Questions:**

- Does feedback actually update anything?
- Can you navigate from a belief to its visual evidence?
- Does the selection log display in the UI?
- Are bridge warrants shown in context_shift images?

### 5. Production Readiness

**Assess:**

- Error handling completeness
- Logging adequacy
- Performance under load
- Security vulnerabilities
- Data validation
- Documentation completeness

---

## Response Format

Please provide your review in this structure:

```markdown
## Executive Summary
[3-5 bullet points of most critical issues]

## GUI Review

### claim-gallery.html
**Status**: [Working/Partial/Broken]
**Critical Issues**:
- [Issue 1]
- [Issue 2]
**Missing Features**:
- [Feature 1]
**Recommendations**:
- [Rec 1]

### evidence-explorer.html
[Same structure]

### Other GUIs
[Same structure]

## AI Assistance Review

### Current State
[What AI assistance exists?]

### Critical Gaps
[What's missing?]

### Recommended Additions
| Priority | Feature | Benefit | Effort |
|----------|---------|---------|--------|
| HIGH | | | |

## Workflow Analysis

### Architect
**Can complete workflow?**: [Yes/No/Partial]
**Blockers**:
**Recommendations**:

### Student
[Same structure]

### Researcher
[Same structure]

## Integration Issues

### Critical Disconnects
| Component A | Component B | Issue | Impact |
|-------------|-------------|-------|--------|
| | | | |

## Production Concerns

### Blocking Issues
- [Issue 1]

### High Priority
- [Issue 1]

### Medium Priority
- [Issue 1]

## Prioritized Action Plan

### Must Fix Before User Testing
1. [Issue]
2. [Issue]

### Should Fix for v1.0
1. [Issue]

### Nice to Have
1. [Issue]
```

---

## Evaluation Criteria

Rate each area 1-5:

| Area | Score | Justification |
|------|-------|---------------|
| GUI Functionality | | |
| GUI Aesthetics | | |
| AI Assistance | | |
| User Workflow Support | | |
| Backend Integration | | |
| Documentation | | |
| Error Handling | | |
| Production Readiness | | |

**Overall Assessment**: [Not Ready / Needs Work / Acceptable / Good / Excellent]

---

## Additional Context

### What's New in V22.0.0

1. **ClaimGallery System** (Sprint G1)
   - Visual evidence galleries with 5 slot types
   - Deterministic, auditable selection
   - Persona-based configurations
   - Active learning feedback loop

2. **Panel-Validated Fixes**
   - Outcome status validation (Pearl)
   - Web snapshot traceability (Ng)
   - Input validation (ChatGPT-4)

### Known Limitations

- Demo uses placeholder images (not real architectural photos)
- Feedback doesn't yet trigger model retraining
- No chat interface implemented
- Export features are stubs

### User Personas

| Persona | Primary Task | Key Need |
|---------|--------------|----------|
| Architect | Apply principles to designs | Quick answers, visual examples |
| Student | Learn CNFA constructs | Clear explanations, self-testing |
| Researcher | Evaluate evidence quality | Full audit trail, export |

---

## Final Instruction

**Be the user who just paid for this software and found it didn't work.**

What would make you angry? What would make you return it? What would you tell your colleagues?

**Then be the developer who has to fix it.**

What's the fastest path to a usable product? What can be deferred? What's truly blocking?

---

*Prepared for external review, January 23, 2026*
