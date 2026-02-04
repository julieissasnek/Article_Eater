David — this is exactly right. For CNfA, many “findings” are *image-grounded* categories (fluency, refuge edges, glare, clutter, biophilic cues), so a text-only explanation is often inadequate. What you want is a **visual evidence layer**: exemplars, counter-exemplars, and near misses, tied to claims with scope and confidence.



Below is a structured proposal: (1) the core “exemplar logic,” (2) the UI objects, (3) what else researchers/architects will want that is best answered with pictures, and (4) how AI should curate these without faking certainty.



------





## **1) Exemplar logic: show the claim as a visual set, not a sentence**





For each **claim / hypothesis** (e.g., “high perceptual fluency reduces stress” or “prospect+refuge improves perceived safety”), the system should present a **visual constellation**:





### **A. Central positive cases (prototypical instantiations)**





- Images where the feature is unambiguous and matches the claim’s “intended” definition.
- These are the “teaching” cases.







### **B. Central negative cases (clear counterexamples)**





Two kinds:



1. **Feature absent**: claim should not apply (e.g., no refuge edges).
2. **Feature present but outcome doesn’t follow**: “failure” under a boundary condition (e.g., fluency present but stress still high due to crowding/noise).







### **C. Near misses and edge cases**





- Borderline cases that reveal the *decision boundary*:

  

  - almost-refuge but not quite,
  - biophilic material present but synthetic cues dominate,
  - “organized complexity” that reads as clutter.

  







### **D. “Same feature, different context” (portability checks)**





- Same visual feature in different building types / cultures / tasks:

  

  - classroom vs hospital vs retail,
  - North American office vs Indian market,
  - short exposure vs long occupation (proxy via context).

  







### **E. Confound-controlled comparisons**





- Pairs that differ in one salient feature while holding others stable:

  

  - same room, different lighting,
  - same layout, different acoustic treatment,
  - same geometry, different surface reflectance.

  





This constellation is what lets an architect *see* what the finding means and a researcher *see* where it breaks.



------





## **2) UI objects that make this work (and make it “two-sided” by design)**







### **1) Claim Card → “Visual Gallery” tab**





A Claim Card should have:



- **Claim statement**
- **Evidence quality bars** (design/consistency/portability)
- **Scope box** (population/setting/measurement)
- **Visual Gallery tab** with fixed slots:





**Slots (always shown)**



- ✅ 4 “central positives”
- ❌ 4 “central negatives”
- ⚠️ 4 “near misses”
- 🔁 4 “context shifts” (optional if available)





Each thumbnail has a tooltip:



- tags present,
- why included (feature evidence),
- (if known) outcome proxy and boundary condition notes.







### **2) Failure-mode panel (counterfactual explanation)**





When a user clicks a “failure” image:



- “Claim would predict X, but we observe Y / or evidence suggests non-X.”
- Show **likely moderators** (crowding, noise, lack of control, safety cues).
- Offer “closest successful neighbors” (nearest positives).





This is where the epistemic engine earns its keep: failures become *structured boundary conditions*, not embarrassing exceptions.





### **3) “Decision boundary slider” for near misses**





A researcher/architect should be able to drag a slider from “strict definition” → “loose definition” and watch which images flip category.

This makes category definitions explicit and debuggable.





### **4) Pairwise comparison mode (“what changed?”)**





Select two images → the system highlights:



- feature differences,
- predicted outcome shifts,
- evidence support (with citations),
- a warning if the inference is weak.





This is excellent for architects: “Change one thing and see the predicted effect.”





### **5) “Show me analogs” (case-based reasoning)**





From an image, ask:



- “Show 10 most similar images where the claim held”
- “Show 10 most similar where it failed”
- “Show the hardest confusable cases”





That is exactly the “central / less central / near miss” set you described.



------





## **3) Things users will ask that are best answered with pictures (beyond exemplars)**







### **A) “What does this construct** 

### **look like**

### **?”**





Many constructs are hard to define verbally:



- perceptual fluency / organized complexity
- legibility / coherence / mystery
- refuge edges / enclosure gradients
- glare risk / contrast hot spots
- visual clutter vs richness
- biophilic cues vs “biophilic decoration”





**Best answer:** a small *visual dictionary* (positive/negative/near miss).





### **B) “What are good design moves that implement this finding?”**





Architects don’t just want classification; they want **design patterns**:



- “increase refuge without killing prospect”
- “reduce clutter without making it sterile”
- “add nature cues without kitsch”





**Best answer:** before/after exemplars, pattern galleries, and annotated images.





### **C) “What are the common confusions?”**





Researchers and students need to know what is confusable:



- complexity vs clutter
- refuge vs obstruction
- natural materials vs natural *forms*
- daylight vs glare
- open plan sociability vs crowding stress





**Best answer:** “confusion sets” — pairs of images that look similar but map to different outcomes.





### **D) “Where does this finding generalize?”**





Generalization is easiest to show visually:



- show the same claim across building types, cultures, and tasks.
- show “known-good” vs “known-bad” contexts.





**Best answer:** facet filters (building type, culture region, task) that reshuffle exemplars.





### **E) “What’s the minimum change that flips the prediction?”**





This is near-perfect for images:



- identify a micro-change (lighting, partitions, material reflectance) that flips predicted stress/comfort.





**Best answer:** counterfactual image edits are tempting, but if you avoid synthetic images initially, you can still do this via nearest-neighbor exemplars and paired datasets.





### **F) “What is the evidence anchored to?”**





Users want to know if a claim is anchored to:



- VR studies (rendered environments),
- lab photos,
- field studies in real buildings.





**Best answer:** show the exemplar’s provenance and “study modality” visually (badges).



------





## **4) How AI should curate these sets (without pretending it “knows outcomes” from a photo)**





This is crucial.





### **Principle: images are** 

### **evidence of construct instantiation**

### **, not direct evidence of outcome**





Unless you have measured outcomes tied to the image, the system must label:



- “**Construct present** (high confidence)” vs
- “**Outcome evidence exists in literature** (separately).”





So each exemplar should be tagged along two axes:



1. **Visual construct confidence** (does the image instantiate the construct?)
2. **Outcome support strength** (does literature support the construct→outcome link in the relevant scope?)







### **Selection algorithm (simple and transparent)**





For a claim C: feature F → outcome O:



- pick images where **F-confidence is high** (central positives)
- pick images where **¬F-confidence is high** (central negatives)
- pick images near F threshold (near misses)
- pick images where F is high but moderators suggest failure risk (likely failures)





And always show *why each image was selected* (“selected because strong refuge edges + low clutter + moderate enclosure”).



------





## **5) A few extra “picture-first” features worth adding**







### **1) Visual boundary-condition explorer**





Click “Failure drivers” and see mini-galleries:



- “fails under crowding”

- “fails under glare”

- “fails under low control”

  Each gallery shows representative images.







### **2) Mechanism visualization**





For mechanism-heavy claims (e.g., “fluency reduces cognitive load”), show:



- examples of high fluency vs low fluency,
- plus the *task context* images (where relevant).







### **3) Study-method lens**





Toggle:



- “Show only field-study exemplars”

- “Show only VR/lab-study exemplars”

  So users can judge ecological validity visually.







### **4) “Teach me this construct” mode**





A student-facing mini-tutorial:



- 12 images (positives/negatives/near misses)
- short quiz (“which has higher refuge?”)
- immediate feedback and why





This also produces training labels for your model.



------



If you want, I can turn this into a **spec**: a JSON schema for ClaimGallery (slots, provenance, selection reasons, confidence axes), plus UI wireframe text and a set of acceptance tests (“every claim must have >=4 positives/negatives/near-misses or explicitly say ‘insufficient image coverage’”).



David — below is a concrete spec you can hand to Codex/Claude: **ClaimGallery data model + JSON Schema + selection algorithm + UI wireframe text + acceptance tests + governance notes**.



------





# **ClaimGallery Spec v0.1**







## **Purpose**





For each **claim/hypothesis** (e.g., *F → O under scope S*), present a **balanced visual constellation**:



- central positives (F clearly present),
- central negatives (F clearly absent),
- near misses (borderline F),
- failures (F present but likely to fail due to moderators),
- context shifts (portability checks),
- optionally: confusions and controlled comparisons.





The gallery is **not** “proof by pictures.” It is a *visual grounding layer* for (a) what the construct looks like, (b) where it breaks, and (c) what to test next.



------





# **1) Data model**







## **1.1 Core object: ClaimGallery**





A ClaimGallery binds:



- **claim metadata** (claim_id, statement, feature F, outcome O),
- **scope & evidence quality** (design/consistency/portability),
- **slots** (images grouped by role),
- **selection justification** for every image,
- **guardrails** (what is known from measurements vs inferred from appearance).







### **Slot types (required)**





- central_positive (>=4)
- central_negative (>=4)
- near_miss (>=4)







### **Slot types (recommended)**





- likely_failure (>=2 if known moderators exist)
- context_shift (>=4 if multiple contexts exist)
- confusion_set (>=2 pairs)
- controlled_comparison (>=2 pairs)





Each image entry must include:



- construct_confidence (how clearly it instantiates feature F),
- outcome_evidence_link (whether *outcome* is measured for this image, or only literature-backed generally),
- selection_reason (human-readable short string),
- provenance (source, license, local id),
- moderator_flags (crowding/glare/noise/low-control/etc.).





------





# **2) JSON Schema**





Save as: schemas/claim_gallery.v1.schema.json

```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/claim_gallery.v1.schema.json",
  "title": "ClaimGallery v1",
  "type": "object",
  "required": [
    "schema_version",
    "gallery_id",
    "claim",
    "evidence_quality",
    "scope",
    "slots",
    "generated_at",
    "provenance_summary"
  ],
  "properties": {
    "schema_version": { "type": "string", "const": "claim_gallery.v1" },
    "gallery_id": { "type": "string", "minLength": 8 },
    "generated_at": { "type": "string", "format": "date-time" },

    "claim": {
      "type": "object",
      "required": ["claim_id", "statement", "feature", "outcome"],
      "properties": {
        "claim_id": { "type": "string" },
        "statement": { "type": "string", "minLength": 10 },

        "feature": {
          "type": "object",
          "required": ["feature_id", "feature_name"],
          "properties": {
            "feature_id": { "type": "string" },
            "feature_name": { "type": "string" },
            "feature_definition": { "type": "string" },
            "feature_aliases": { "type": "array", "items": { "type": "string" } }
          }
        },

        "outcome": {
          "type": "object",
          "required": ["outcome_id", "outcome_name"],
          "properties": {
            "outcome_id": { "type": "string" },
            "outcome_name": { "type": "string" },
            "outcome_definition": { "type": "string" },
            "valence": {
              "type": "string",
              "enum": ["higher_is_better", "higher_is_worse", "neutral_or_contextual", "unknown"]
            }
          }
        },

        "moderators_expected": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["moderator_id", "moderator_name"],
            "properties": {
              "moderator_id": { "type": "string" },
              "moderator_name": { "type": "string" },
              "notes": { "type": "string" }
            }
          }
        }
      }
    },

    "evidence_quality": {
      "type": "object",
      "required": ["design_strength", "consistency", "portability"],
      "properties": {
        "design_strength": { "type": "number", "minimum": 0, "maximum": 1 },
        "consistency": { "type": "number", "minimum": 0, "maximum": 1 },
        "portability": { "type": "number", "minimum": 0, "maximum": 1 },
        "notes": { "type": "string" },
        "top_citations": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["citation_id", "title"],
            "properties": {
              "citation_id": { "type": "string" },
              "title": { "type": "string" },
              "doi": { "type": "string" },
              "year": { "type": "integer" }
            }
          }
        }
      }
    },

    "scope": {
      "type": "object",
      "required": ["population", "setting", "task_context", "measurement_context"],
      "properties": {
        "population": { "type": "string" },
        "setting": { "type": "string" },
        "task_context": { "type": "string" },
        "measurement_context": { "type": "string" },
        "duration": { "type": "string" },
        "exclusions": { "type": "array", "items": { "type": "string" } }
      }
    },

    "slots": {
      "type": "object",
      "required": ["central_positive", "central_negative", "near_miss"],
      "properties": {
        "central_positive": { "$ref": "#/$defs/image_list" },
        "central_negative": { "$ref": "#/$defs/image_list" },
        "near_miss": { "$ref": "#/$defs/image_list" },

        "likely_failure": { "$ref": "#/$defs/image_list" },
        "context_shift": { "$ref": "#/$defs/image_list" },

        "confusion_set": {
          "type": "array",
          "items": { "$ref": "#/$defs/image_pair" }
        },
        "controlled_comparison": {
          "type": "array",
          "items": { "$ref": "#/$defs/image_pair" }
        }
      },
      "additionalProperties": false
    },

    "provenance_summary": {
      "type": "object",
      "required": ["image_sources", "license_notes", "selection_method"],
      "properties": {
        "image_sources": { "type": "array", "items": { "type": "string" } },
        "license_notes": { "type": "string" },
        "selection_method": { "type": "string" },
        "model_versions": { "type": "array", "items": { "type": "string" } }
      }
    }
  },

  "$defs": {
    "image_list": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/image_entry" }
    },

    "image_pair": {
      "type": "object",
      "required": ["a", "b", "pair_type", "pair_explanation"],
      "properties": {
        "pair_type": {
          "type": "string",
          "enum": ["confusable_but_different", "controlled_difference", "near_boundary_flip"]
        },
        "pair_explanation": { "type": "string", "minLength": 10 },
        "a": { "$ref": "#/$defs/image_entry" },
        "b": { "$ref": "#/$defs/image_entry" }
      }
    },

    "image_entry": {
      "type": "object",
      "required": [
        "image_id",
        "uri_or_path",
        "selection_reason",
        "construct_confidence",
        "outcome_evidence",
        "tags",
        "provenance"
      ],
      "properties": {
        "image_id": { "type": "string" },
        "uri_or_path": { "type": "string" },

        "selection_reason": { "type": "string", "minLength": 10 },

        "construct_confidence": {
          "type": "object",
          "required": ["score", "basis"],
          "properties": {
            "score": { "type": "number", "minimum": 0, "maximum": 1 },
            "basis": {
              "type": "string",
              "enum": ["human_label", "model_prediction", "hybrid"]
            },
            "explanatory_cues": { "type": "array", "items": { "type": "string" } }
          }
        },

        "outcome_evidence": {
          "type": "object",
          "required": ["status"],
          "properties": {
            "status": {
              "type": "string",
              "enum": [
                "measured_on_this_image",
                "measured_on_similar_context",
                "literature_link_only",
                "unknown"
              ]
            },
            "measured_outcomes": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["outcome_id", "measure", "direction"],
                "properties": {
                  "outcome_id": { "type": "string" },
                  "measure": { "type": "string" },
                  "direction": {
                    "type": "string",
                    "enum": ["increase", "decrease", "no_effect", "mixed", "unknown"]
                  }
                }
              }
            },
            "citations": {
              "type": "array",
              "items": { "type": "string" }
            }
          }
        },

        "tags": {
          "type": "object",
          "properties": {
            "feature_tags": { "type": "array", "items": { "type": "string" } },
            "context_tags": { "type": "array", "items": { "type": "string" } },
            "moderator_flags": { "type": "array", "items": { "type": "string" } }
          }
        },

        "provenance": {
          "type": "object",
          "required": ["source", "license", "attribution"],
          "properties": {
            "source": { "type": "string" },
            "license": { "type": "string" },
            "attribution": { "type": "string" },
            "study_id": { "type": "string" },
            "paper_doi": { "type": "string" }
          }
        }
      }
    }
  }
}
```



------





# **3) Selection algorithm (deterministic and auditable)**







## **Inputs**





- Claim: F → O with scope S and expected moderators M

- Image pool with feature scores and tags:

  

  - P(F|image) (construct confidence)
  - context facets (building type, culture region, task proxy, modality)
  - moderator proxies (crowding, glare, noise proxy, control proxy, etc.)

  

- Optional measured outcome links: OutcomeEvidence(status, citations)







## **Deterministic selection steps**





1. **Stratify by context facets** (building_type, indoor/outdoor, culture_region if available, task proxy). Keep a balanced mix unless user filters.

2. **Central positives**: choose top-N images maximizing P(F) while minimizing redundancy (diversity constraint via clustering).

3. **Central negatives**: choose top-N images maximizing 1-P(F) with the same diversity constraint.

4. **Near misses**: choose images with P(F) near threshold τ (e.g., |P(F) − τ| small), plus high diversity.

5. **Likely failures**: choose images with high P(F) and high predicted “failure risk” based on moderators:

   

   - FailureRisk = max_j P(M_j|image) for moderators known to flip effect or shrink it.
   - Label as “likely failure (moderator: crowding)” not as “false.”

   

6. **Context shifts**: for a fixed “feature-high” subset, select images across different facets (hospital/office/classroom), so users see portability boundaries.

7. **Confusion sets**: pick pairs where embeddings are similar but P(F) differs (or where a competing feature G is high).

8. **Controlled comparisons** (only if available): matched pairs differing primarily in one feature (requires either curated dataset or strong matching features).







## **Required justification fields per image**





- selection_reason must mention:

  

  - slot role (e.g., “central_positive”)
  - key cues (“strong refuge edges,” “low glare,” “high enclosure gradient”)
  - any moderator flags used.

  





------





# **4) UI wireframe text (no graphics, implementable)**







## **Claim Page Layout**





**Header**



- Claim statement (editable canonical phrasing)
- Evidence quality widget: 3 bars (design / consistency / portability)
- Scope chip row: population | setting | task | modality | duration





**Tabs**



1. Summary
2. Evidence
3. Visual Gallery
4. Failures & Moderators
5. Export







### **Visual Gallery tab**





Sections (each shows thumbnails; clicking opens image drawer):



- **Central positives (this is what F looks like)**
- **Central negatives (this is what not-F looks like)**
- **Near misses (borderline cases)**
- (Optional) **Likely failures (F present, but moderators suggest the effect may not hold)**
- (Optional) **Context shifts (same feature, different contexts)**





**Image drawer (right panel)**



- Large image

- Construct confidence (with basis)

- “Why selected” (selection_reason)

- Feature cues (bullets from explanatory_cues)

- Moderator flags

- Outcome evidence status:

  

  - Measured on this image / measured on similar context / literature-link-only

  

- Links: provenance, DOI/PDF if available

- Buttons:

  

  - “Find similar where claim holds”
  - “Find similar where claim fails”
  - “Add to confusion set”
  - “Mark as misclassified” (feeds active learning)

  







### **Failures & Moderators tab**





- Moderator list ranked by “risk of failure”

- Clicking a moderator shows:

  

  - gallery subset of likely failures tagged with that moderator
  - “closest successful neighbors”
  - short text: “why this moderator plausibly breaks the link”

  







### **Export tab**





- Export ClaimGallery JSON

- Export PDF/HTML report that includes:

  

  - small grids for each slot
  - captions (selection_reason + scope)

  





------





# **5) Acceptance tests (UX + governance)**







## **Minimum coverage**





- **AT1:** Every claim with evidence_quality.design_strength >= 0.3 must have:

  

  - ≥ 4 central_positive

  - ≥ 4 central_negative

  - ≥ 4 near_miss

    If not possible, system must show: “Insufficient image coverage” + which slot is missing + why.

  







## **Two-sided presentation**





- **AT2:** UI must always show *both* positives and negatives for any displayed claim (no “positives only” mode in default view).







## **Honest outcome labeling**





- **AT3:** Every image must display outcome_evidence.status.

  If literature_link_only, UI must show a fixed warning: “Outcome not measured on this image; link is literature-level.”







## **Reproducibility**





- **AT4:** Given the same claim + same image pool + same thresholds, gallery selection is deterministic (same image_ids in the same slots), except where randomization is explicitly enabled and logged.







## **Provenance**





- **AT5:** Every image drawer shows source + license + attribution; export includes them.







## **Diversity constraint**





- **AT6:** Central slots must satisfy a diversity rule (e.g., no more than 2 images from the same building/project/study unless user filters). Failing this must be flagged.







## **Workflow integration**





- **AT7:** From any image, user can click:

  

  - “show similar where claim holds”

  - “show similar where claim fails”

    and get non-empty results or an explicit “insufficient negatives/positives” notice.

  







## **Active learning**





- **AT8:** “Mark as misclassified” must write a structured feedback record:

  

  - image_id, claim_id, slot_role, correction, reason, timestamp, actor

  





------





# **6) Related picture-first researcher/architect questions to support**



These should be first-class UI actions because text answers are inferior:

1. **“Show prototypical examples of F in hospitals/offices/classrooms.”**
2. **“Show the closest counterexamples: spaces that look like this but don’t have F.”**
3. **“Show failure modes for this claim (crowding, glare, low control).”**
4. **“Show confusion sets: pairs that people mix up (complexity vs clutter).”**
5. **“Show the smallest visual difference that changes the classification.”** (near-boundary flip pairs)
6. **“Show portability: same feature across cultures/building types/tasks.”**
7. **“Show mechanism anchors: images that illustrate the proposed mechanism.”** (e.g., “refuge edges → reduced vigilance demand”)

------

# **7) Implementation notes (minimal but crucial)**



- Do **not** require outcome ground truth for images to be useful.

  Instead, treat images as **construct instantiation evidence** + separate literature-level outcome link.

- When you *do* have measured outcomes tied to images (rare but valuable), elevate those in the gallery and badge them (“measured here”).

- Store galleries as versioned artifacts (hash + timestamp) so a report can be reproduced exactly.



------



If you want the next step, I can also give you a companion schema for **ImageFeedback** (active learning labels) and a **GallerySelectionConfig** (thresholds, diversity rules, facet weights) so selection is fully configurable and audit-friendly.



Great — here are the two companion specs you asked for: **ImageFeedback** (active learning) and **GallerySelectionConfig** (deterministic, audit-friendly selection controls). They’re designed to plug directly into the ClaimGallery workflow and to support governance (append-only logging, reproducible rebuilds).



------





# **1) ImageFeedback Spec v0.1**







## **Purpose**





Capture user corrections and judgments about:



- whether an image truly instantiates feature **F**,
- whether the image belongs in a given slot (positive/negative/near miss/failure),
- what cues or moderators were overlooked,
- whether the system’s selection rationale was misleading.





This is the backbone for:



- improving construct detectors,
- improving boundary definitions,
- improving diversity/coverage and “failure mode” labeling.







## **Object model**







### **Event types**





- construct_label (user says F is present/absent/uncertain)
- slot_reassignment (this image shouldn’t be in this slot; move to slot X)
- moderator_annotation (user says a moderator is present or absent)
- rationale_correction (system’s “why selected” explanation is wrong/misleading)
- provenance_issue (license/source/attribution problem)
- duplicate_or_redundant (too similar to another image in slot)







### **Required governance fields**





- feedback_id, timestamp, actor_id, actor_role, session_id
- claim_id, image_id, gallery_id, slot_role
- before and after (what changed)
- confidence and free_text_reason
- audit_hash (optional but recommended) linking to the web snapshot / gallery build.





------





## **1.1 JSON Schema:** 

## **schemas/image_feedback.v1.schema.json**



```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/image_feedback.v1.schema.json",
  "title": "ImageFeedback v1",
  "type": "object",
  "required": [
    "schema_version",
    "feedback_id",
    "timestamp",
    "actor",
    "target",
    "event_type",
    "before",
    "after",
    "confidence",
    "reason"
  ],
  "properties": {
    "schema_version": { "type": "string", "const": "image_feedback.v1" },
    "feedback_id": { "type": "string", "minLength": 10 },
    "timestamp": { "type": "string", "format": "date-time" },

    "actor": {
      "type": "object",
      "required": ["actor_id", "role"],
      "properties": {
        "actor_id": { "type": "string" },
        "role": {
          "type": "string",
          "enum": ["student", "architect", "researcher", "maintainer", "admin", "unknown"]
        },
        "session_id": { "type": "string" }
      }
    },

    "target": {
      "type": "object",
      "required": ["gallery_id", "claim_id", "image_id", "slot_role"],
      "properties": {
        "gallery_id": { "type": "string" },
        "claim_id": { "type": "string" },
        "image_id": { "type": "string" },
        "slot_role": {
          "type": "string",
          "enum": [
            "central_positive",
            "central_negative",
            "near_miss",
            "likely_failure",
            "context_shift",
            "confusion_set",
            "controlled_comparison",
            "unknown"
          ]
        },
        "web_snapshot_id": { "type": "string" }
      }
    },

    "event_type": {
      "type": "string",
      "enum": [
        "construct_label",
        "slot_reassignment",
        "moderator_annotation",
        "rationale_correction",
        "provenance_issue",
        "duplicate_or_redundant"
      ]
    },

    "before": { "$ref": "#/$defs/state_patch" },
    "after": { "$ref": "#/$defs/state_patch" },

    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },

    "reason": {
      "type": "object",
      "required": ["free_text"],
      "properties": {
        "free_text": { "type": "string", "minLength": 3 },
        "cue_terms": { "type": "array", "items": { "type": "string" } },
        "moderator_flags": { "type": "array", "items": { "type": "string" } }
      }
    },

    "attachments": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "value"],
        "properties": {
          "type": { "type": "string", "enum": ["note", "url", "screenshot_ref"] },
          "value": { "type": "string" }
        }
      }
    }
  },

  "$defs": {
    "state_patch": {
      "type": "object",
      "properties": {
        "construct_confidence_score": { "type": "number", "minimum": 0, "maximum": 1 },
        "construct_label": { "type": "string", "enum": ["present", "absent", "uncertain", "unknown"] },
        "slot_role": {
          "type": "string",
          "enum": [
            "central_positive",
            "central_negative",
            "near_miss",
            "likely_failure",
            "context_shift",
            "confusion_set",
            "controlled_comparison",
            "unknown"
          ]
        },
        "moderator_flags": { "type": "array", "items": { "type": "string" } },
        "selection_reason": { "type": "string" },
        "provenance_ok": { "type": "boolean" }
      },
      "additionalProperties": false
    }
  }
}
```



## **Storage & governance**





- Store feedback events as **append-only JSONL**: data/feedback/image_feedback.jsonl
- Never overwrite; apply feedback by generating a derived “labels view.”
- Every gallery build should record which feedback snapshot it used.





------





# **2) GallerySelectionConfig Spec v0.1**







## **Purpose**





Make gallery generation:



- deterministic,
- explainable,
- tunable per persona (architect vs student vs researcher),
- and auditable (a gallery is reproducible from config + image pool snapshot).







## **Key controls**





1. **Thresholds**







- feature_threshold_tau for classifying F present/absent
- near_miss_band width around τ







1. **Slot sizes**







- desired counts per slot (min/max)
- fallback behavior if insufficient images exist







1. **Diversity constraints**







- max per source/project/study
- clustering method and target diversity







1. **Facet balancing**







- building type, culture region, modality (photo/VR), indoor/outdoor
- weights for balance vs “best exemplars”







1. **Failure risk model**







- moderator list + weights
- rule-based or learned risk score







1. **Pair mining settings** (confusion/controlled)







- similarity metric + thresholds
- what “controlled” means (matching constraints)





------





## **2.1 JSON Schema:** 

## **schemas/gallery_selection_config.v1.schema.json**



```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/gallery_selection_config.v1.schema.json",
  "title": "GallerySelectionConfig v1",
  "type": "object",
  "required": [
    "schema_version",
    "config_id",
    "feature_threshold_tau",
    "near_miss_band",
    "slot_targets",
    "diversity",
    "facet_balance",
    "failure_risk",
    "pair_mining",
    "determinism"
  ],
  "properties": {
    "schema_version": { "type": "string", "const": "gallery_selection_config.v1" },
    "config_id": { "type": "string", "minLength": 8 },

    "persona_profile": {
      "type": "string",
      "enum": ["architect", "student", "researcher", "default"]
    },

    "feature_threshold_tau": { "type": "number", "minimum": 0, "maximum": 1 },
    "near_miss_band": { "type": "number", "minimum": 0, "maximum": 0.5 },

    "slot_targets": {
      "type": "object",
      "required": ["central_positive", "central_negative", "near_miss"],
      "properties": {
        "central_positive": { "$ref": "#/$defs/slot_target" },
        "central_negative": { "$ref": "#/$defs/slot_target" },
        "near_miss": { "$ref": "#/$defs/slot_target" },
        "likely_failure": { "$ref": "#/$defs/slot_target" },
        "context_shift": { "$ref": "#/$defs/slot_target" }
      },
      "additionalProperties": false
    },

    "diversity": {
      "type": "object",
      "required": ["dedupe_key", "max_per_dedupe_key", "clustering"],
      "properties": {
        "dedupe_key": {
          "type": "string",
          "enum": ["project_id", "source_id", "study_id", "none"]
        },
        "max_per_dedupe_key": { "type": "integer", "minimum": 1, "maximum": 10 },
        "clustering": {
          "type": "object",
          "required": ["method", "k", "min_cluster_distance"],
          "properties": {
            "method": { "type": "string", "enum": ["kmeans", "hdbscan", "none"] },
            "k": { "type": "integer", "minimum": 1, "maximum": 200 },
            "min_cluster_distance": { "type": "number", "minimum": 0, "maximum": 1 }
          }
        }
      }
    },

    "facet_balance": {
      "type": "object",
      "required": ["enabled", "facets"],
      "properties": {
        "enabled": { "type": "boolean" },
        "facets": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["facet_name", "weight", "max_skew"],
            "properties": {
              "facet_name": {
                "type": "string",
                "enum": ["building_type", "culture_region", "modality", "indoor_outdoor", "task_proxy"]
              },
              "weight": { "type": "number", "minimum": 0, "maximum": 1 },
              "max_skew": { "type": "number", "minimum": 0, "maximum": 1 }
            }
          }
        }
      }
    },

    "failure_risk": {
      "type": "object",
      "required": ["enabled", "moderators"],
      "properties": {
        "enabled": { "type": "boolean" },
        "moderators": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["moderator_id", "weight", "risk_threshold"],
            "properties": {
              "moderator_id": { "type": "string" },
              "weight": { "type": "number", "minimum": 0, "maximum": 5 },
              "risk_threshold": { "type": "number", "minimum": 0, "maximum": 1 }
            }
          }
        },
        "method": {
          "type": "string",
          "enum": ["rule_based", "logistic", "unknown"],
          "default": "rule_based"
        }
      }
    },

    "pair_mining": {
      "type": "object",
      "required": ["enabled", "similarity_metric", "confusion", "controlled"],
      "properties": {
        "enabled": { "type": "boolean" },
        "similarity_metric": { "type": "string", "enum": ["cosine_embedding", "tag_jaccard", "hybrid"] },

        "confusion": {
          "type": "object",
          "required": ["min_similarity", "max_pairs"],
          "properties": {
            "min_similarity": { "type": "number", "minimum": 0, "maximum": 1 },
            "max_pairs": { "type": "integer", "minimum": 0, "maximum": 200 }
          }
        },

        "controlled": {
          "type": "object",
          "required": ["match_facets", "max_pairs"],
          "properties": {
            "match_facets": {
              "type": "array",
              "items": {
                "type": "string",
                "enum": ["building_type", "culture_region", "modality", "task_proxy", "indoor_outdoor"]
              }
            },
            "max_pairs": { "type": "integer", "minimum": 0, "maximum": 200 },
            "max_feature_diff_for_controls": { "type": "number", "minimum": 0, "maximum": 1 }
          }
        }
      }
    },

    "determinism": {
      "type": "object",
      "required": ["random_seed", "stable_sort_keys"],
      "properties": {
        "random_seed": { "type": "integer" },
        "stable_sort_keys": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["feature_score", "failure_risk", "diversity_rank", "image_id"]
          }
        }
      }
    }
  },

  "$defs": {
    "slot_target": {
      "type": "object",
      "required": ["min", "target", "max", "fallback_policy"],
      "properties": {
        "min": { "type": "integer", "minimum": 0, "maximum": 50 },
        "target": { "type": "integer", "minimum": 0, "maximum": 50 },
        "max": { "type": "integer", "minimum": 0, "maximum": 50 },
        "fallback_policy": {
          "type": "string",
          "enum": ["shrink_slot", "borrow_from_near_miss", "borrow_from_context_shift", "emit_insufficient_coverage"]
        }
      }
    }
  }
}
```



------





# **3) Minimal default configs (persona-tuned)**







## **Architect**





- fewer but clearer exemplars; prioritize centrality over edge cases:
- τ = 0.65, near band = 0.10
- central slots target 6 each, near_miss 4
- failure_risk enabled, show likely failures prominently
- facet balance mild (don’t overwhelm)







## **Student**





- emphasize learning boundaries:
- τ = 0.60, near band = 0.15
- central slots 6 each, near_miss 8
- confusion sets enabled (teach confusions)
- facet balance stronger (show variety)







## **Researcher**





- emphasize discrimination and portability:
- τ = 0.55, near band = 0.20
- near_miss 10, controlled comparisons prioritized
- context shift required (if available)
- facet balance strong + explicit modality toggles





------





# **4) How these connect to your existing governance**





Add to your “GO/NO-GO UX checklist”:



- **UX-AT9:** every generated ClaimGallery includes the GallerySelectionConfig id and a hash of the image pool snapshot used.
- **UX-AT10:** every ImageFeedback event references gallery_id and web_snapshot_id (or explicitly unknown) and is append-only.





------



If you want the *next* concrete thing: I can draft a tiny “gallery builder” interface contract (Python class + inputs/outputs) that takes (claim_id, image_pool_snapshot, config) and emits a validated ClaimGallery JSON plus a selection_log.json explaining every inclusion/exclusion decision.











David — here is a concrete **Gallery Builder interface contract** you can hand to Codex/Claude. It’s designed to be:



- deterministic and auditable,
- schema-validated (ClaimGallery, GallerySelectionConfig),
- capable of emitting a human-readable **selection log** explaining every include/exclude decision,
- easy to wrap behind an API route and/or a CLI.





------





# **Gallery Builder Contract v0.1**







## **1) Public surface**







### **1.1 Python interface**





Module: src/services/claim_gallery_builder.py

```
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Protocol

JsonDict = Dict[str, Any]


class ImagePoolProvider(Protocol):
    """Provides a deterministic snapshot of images and their computed fields."""
    def load_snapshot(self, snapshot_id: str) -> JsonDict:
        """
        Returns an ImagePoolSnapshot object (JSON dict) containing:
        - snapshot metadata (id, created_at, hash)
        - list of images with features, tags, facets, embeddings refs
        """
        ...


class ClaimProvider(Protocol):
    """Provides claim metadata needed to build a gallery."""
    def load_claim(self, claim_id: str) -> JsonDict:
        """
        Returns Claim object with:
        - claim_id, statement, feature, outcome, expected moderators, scope defaults
        - evidence_quality (design/consistency/portability) and top citations
        """
        ...


class SchemaValidator(Protocol):
    def validate(self, schema_id: str, obj: JsonDict) -> None:
        """Raises an exception on schema validation failure."""
        ...


@dataclass(frozen=True)
class BuildRequest:
    claim_id: str
    image_pool_snapshot_id: str
    selection_config: JsonDict  # must validate against gallery_selection_config.v1
    persona_profile: str = "default"
    constraints: Optional[JsonDict] = None
    # constraints can include:
    # - required_facets (e.g. building_type in [...])
    # - excluded_sources
    # - only_measured_outcomes = True/False
    # - max_total_images


@dataclass(frozen=True)
class BuildResult:
    claim_gallery: JsonDict               # must validate against claim_gallery.v1
    selection_log: JsonDict               # selection explanation, deterministic
    stats: JsonDict                       # counts, coverage, diversity, warnings


class ClaimGalleryBuilder:
    def __init__(
        self,
        claim_provider: ClaimProvider,
        image_pool_provider: ImagePoolProvider,
        validator: SchemaValidator,
    ) -> None:
        ...

    def build(self, req: BuildRequest) -> BuildResult:
        """
        Deterministically builds a ClaimGallery + SelectionLog + Stats.
        Must not mutate the underlying web/image pool.
        """
        ...
```



------





## **2) Input contracts**







### **2.1 ImagePoolSnapshot (minimal fields required)**





The builder assumes an **image pool snapshot** contains a list of image records with:



Required per image:



- image_id (string)
- uri_or_path
- feature_scores: dict mapping feature_id -> score [0..1]
- facet_values: building_type / culture_region / modality / indoor_outdoor / task_proxy
- moderator_scores: dict mapping moderator_id -> score [0..1]
- tag_sets: feature_tags/context_tags (strings)
- provenance: source/license/attribution (+ optional study_id/doi)





Optional:



- embedding_id (for cosine similarity)
- project_id / source_id / study_id for dedupe
- outcome_evidence block if any measured outcomes exist





Snapshot metadata:



- snapshot_id
- created_at
- snapshot_hash (sha256 of canonical JSON or content manifest)







### **2.2 Claim object (minimal fields required)**





- claim_id
- statement
- feature: feature_id, feature_name, definition
- outcome: outcome_id, outcome_name, valence
- moderators_expected: list of moderators
- evidence_quality: design/consistency/portability + citations
- scope default (population/setting/task/measurement_context)







### **2.3 Config validation**





Before building:



- validate selection_config against gallery_selection_config.v1
- enforce determinism.random_seed + stable sort keys





------





## **3) Output contracts**







### **3.1 ClaimGallery output**





Return a ClaimGallery that validates against claim_gallery.v1 and additionally includes:



- provenance_summary.model_versions: includes builder version + detector versions

- provenance_summary.selection_method: includes config_id + snapshot_hash

- each image entry must have:

  

  - selection_reason
  - construct_confidence with basis
  - outcome_evidence.status
  - provenance

  







### **3.2 SelectionLog output**





File/object: selection_log.v1 (not previously defined; here’s the spec)



**Purpose:** explain why each image was selected or excluded, per slot, with deterministic ranking.



Structure:



- build metadata: claim_id, snapshot_id, snapshot_hash, config_id, persona

- per slot:

  

  - candidate_count
  - selected list (with scores and reasons)
  - top excluded candidates (with why excluded)
  - diversity outcomes (clusters, dedupe constraints)

  

- pair mining logs (if enabled)





Example skeleton:

```
{
  "schema_version": "selection_log.v1",
  "build_meta": {
    "claim_id": "C123",
    "snapshot_id": "IMGPOOL_2026_01_22_A",
    "snapshot_hash": "sha256:...",
    "config_id": "CFG_ARCHITECT_V1",
    "random_seed": 17
  },
  "slots": {
    "central_positive": {
      "tau": 0.65,
      "candidate_count": 238,
      "selected": [
        {
          "image_id": "img_001",
          "rank": 1,
          "feature_score": 0.92,
          "diversity_cluster": "k3",
          "dedupe_key": "proj_17",
          "moderator_risk": 0.12,
          "reason_codes": ["HIGH_FEATURE_SCORE", "DIVERSE_CLUSTER", "LOW_FAILURE_RISK"],
          "reason_text": "High refuge-edge cues; low clutter; selected for central positive coverage."
        }
      ],
      "excluded_top": [
        {
          "image_id": "img_044",
          "feature_score": 0.91,
          "excluded_because": ["DEDUPE_LIMIT_REACHED"],
          "note": "Same project_id as img_001; dedupe_key max reached."
        }
      ]
    }
  },
  "warnings": [
    {"code": "INSUFFICIENT_CONTEXT_SHIFT", "detail": "Only 1 building_type available in pool for this claim."}
  ]
}
```



### **3.3 Stats output**





A compact block for UI and regression testing:



- counts per slot
- % with outcome_evidence.measured_on_this_image
- diversity summary (unique projects/sources/studies)
- facet distribution (skew per facet)
- insufficient coverage flags





------





## **4) Deterministic scoring & selection rules (reference implementation behavior)**







### **4.1 Slot candidate filters**





Let τ = feature_threshold_tau, band = near_miss_band.



- central_positive candidates: P(F|img) >= τ + band
- central_negative candidates: P(F|img) <= τ - band
- near_miss candidates: abs(P(F|img) - τ) <= band





If insufficient candidates, follow config fallback.





### **4.2 Ranking score (auditable)**





Use a stable, additive score:



For positives:

score = wF*F + wD*diversity_bonus - wR*failure_risk + wB*facet_balance_bonus



For negatives:

score = wF*(1-F) + wD*diversity_bonus + wB*facet_balance_bonus



Near misses:

score = wN*(1 - abs(F-τ)/band) + wD*diversity_bonus + wB*facet_balance_bonus



All tie-breaks must be stable:



- sort keys from determinism.stable_sort_keys, ending in image_id.







### **4.3 Diversity enforcement**





Apply in this order:



1. hard dedupe: do not exceed max_per_dedupe_key
2. cluster diversity: prefer candidates from underrepresented clusters
3. facet balance: avoid exceeding max_skew per facet if enabled





Every time an image is excluded for diversity, log it in excluded_top.





### **4.4 Failure risk (for likely_failure slot)**





Compute:

failure_risk = clamp(sum(weight_j * moderator_score_j)) over configured moderators



Likely failure candidates:



- F >= τ + band AND failure_risk >= risk_threshold

  Rank by failure_risk descending + diversity.







### **4.5 Pair mining**





Confusion pairs:



- similarity >= min_similarity
- but P(F) differs by at least Δ (choose Δ=0.25 default)
- log pair reasons (“visually similar; different refuge cues”).





Controlled comparisons:



- match facets in match_facets
- maximize difference in F while minimizing differences in other key features (requires feature vector)
- if you can’t do this reliably, emit 0 pairs + warning.





------





## **5) Error handling contract**





The builder must never silently “kind of work.”



Raise or return warnings explicitly for:



- missing feature scores for claim.feature_id
- missing provenance/license
- insufficient candidates to meet min for required slots
- facet balance constraints impossible (only one facet value in pool)





Policy:



- Required slots: if below min, set stats.insufficient_coverage=True and add a warning; either:

  

  - emit partial gallery with warnings **or**
  - raise InsufficientCoverageError depending on fallback_policy.

  





------





## **6) Tests (minimum set)**





Add these as hard acceptance tests:



1. **Determinism test**: same inputs → identical image_ids per slot + same log hash.
2. **Schema validation test**: output validates against claim_gallery.v1 and selection_log.v1.
3. **Two-sided requirement**: positives/negatives/near_miss present or “insufficient coverage” warning emitted.
4. **Honest outcome labeling**: every image has outcome_evidence.status.
5. **Provenance requirement**: every image has license/attribution; otherwise excluded or flagged.





------





## **7) Integration points**







### **API route suggestion**





- POST /api/v1/galleries/build

  

  - body: { claim_id, image_pool_snapshot_id, selection_config, constraints }
  - returns: { claim_gallery, selection_log_id, stats }

  







### **Storage suggestion**





- store outputs in:

  

  - data/galleries/{gallery_id}.json
  - data/galleries/logs/{gallery_id}.selection_log.json
  - with gallery_id computed as hash(claim_id + snapshot_hash + config_id + constraints)

  





------



If you want, I can also define the selection_log.v1 schema formally (JSON Schema) and a small “gallery regression suite” format so you can pin expected galleries for a handful of flagship claims and catch drift automatically.