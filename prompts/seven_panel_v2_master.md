Seven-Panel v2 Master Prompt (Subject-Aware, BN-Friendly)

You are an expert in cognitive science, experimental design, and
architectural psychology. Your task is to read the abstract and PDF
excerpt of a single academic paper and return a **single JSON object**
containing the Seven-Panel v2 representation of the study.

Return ONLY JSON, no commentary. The JSON object must have the keys:

{
  "panel_subjects": {...} | null,
  "panel_context": {...} | null,
  "panel_measures": {...} | null,
  "panel_findings": {...} | null,
  "panel_heterogeneity": {...} | null,
  "panel_mechanisms": {...} | null,
  "panel_limits": {...} | null
}

For any panel where the information is not available, use null.

High-level intent of each panel
-------------------------------

- panel_subjects: Who are the participants? Capture demographics,
  culture/region, clinical status (if any), and any measured traits
  relevant to how they might DIFFERENTIALLY respond to environments.

- panel_context: What tasks or activities did participants perform,
  in what setting, and for roughly how long? Capture tasks as an array
  of PanelTask objects.

- panel_measures: What indicators were recorded (e.g., self-report
  scales, HRV, EEG, reaction times), and how do they map to psychological
  constructs such as stress, restoration, preference, or workload?

- panel_findings: The core empirical findings, one per FindingV2 item,
  summarising results that link experimental manipulations or stimuli
  to the measured constructs.

- panel_heterogeneity: Any evidence that effects differ across subject
  subgroups (e.g., age bands, cultures, trait anxiety levels). Encode
  these as ModerationPattern records.

- panel_mechanisms: Any explicit mechanism or theory claims about WHY
  the observed effects occur (e.g., predictive coding, biophilia,
  attentional restoration, perceptual fluency).

- panel_limits: Statements about generalisation limits, threats to
  validity, or important boundary conditions the authors highlight.

Schema expectations (summary)
-----------------------------

You MUST follow these shapes:

1) panel_subjects (type == "panel_subjects")

{
  "type": "panel_subjects",
  "paper_id": "<string>",
  "sample": {
    "demographics": {
      "age_mean": <number|null>,
      "age_sd": <number|null>,
      "age_range": "<string|null>",
      "age_band": "<string|null>",
      "sex_gender_distribution": {
        "<category>": <number>,
        ...
      },
      "education_band": "<string|null>",
      "sample_size": <number|null>
    },
    "culture": {
      "countries": ["<string>", ...] | null,
      "region": "<string|null>",
      "self_construal_profile": "<string|null>"
    },
    "clinical_status": {
      "population": "healthy" | "clinical" | "mixed" | "unknown" | null,
      "key_inclusions": ["<string>", ...] | null,
      "key_exclusions": ["<string>", ...] | null
    },
    "traits_measured": [
      {
        "name": "<string>",
        "scale": "<string|null>",
        "used_as_moderator": <bool>
      }
    ] | null,
    "notes": "<string|null>"
  },
  "traits_measured": [
    {
      "name": "<string>",
      "scale": "<string|null>",
      "used_as_moderator": <bool>
    }
  ] | null,
  "notes": "<string|null>"
}

2) panel_context (type == "panel_context")

{
  "type": "panel_context",
  "paper_id": "<string>",
  "tasks": [
    {
      "task_id": "<string>",
      "name": "<string>",
      "activity_type": "<string|null>",
      "duration_min": <number|null>,
      "setting": "<string|null>",
      "environment_type": "<string|null>",
      "relevance_tags": ["<string>", ...] | null,
      "notes": "<string|null>"
    }
  ],
  "global_notes": "<string|null>"
}

3) panel_measures (type == "panel_measures")

{
  "type": "panel_measures",
  "paper_id": "<string>",
  "indicators": [
    {
      "indicator_id": "<string>",
      "name": "<string>",
      "modality": "<string|null>",
      "instrument": "<string|null>",
      "timescale": "<string|null>",
      "interpretation": ["<string>", ...] | null,
      "notes": "<string|null>"
    }
  ] | null,
  "construct_mappings": [
    {
      "construct": "<string>",
      "indicator_ids": ["<string>", ...],
      "notes": "<string|null>"
    }
  ] | null,
  "notes": "<string|null>"
}

4) panel_findings (type == "panel_findings")

{
  "type": "panel_findings",
  "paper_id": "<string>",
  "items": [
    {
      "finding_id": "<string>",
      "finding_text": "<string>",
      "statistics": {
        "p_value": <number|null>,
        "effect_size": <number|null>,
        "effect_size_type": "<string|null>",
        "sample_size": <number|null>,
        "ci_lower": <number|null>,
        "ci_upper": <number|null>
      } | null,
      "quote": "<string|null>",
      "page_span": "<string|null>",
      "task_id": "<string|null>",
      "indicator_ids": ["<string>", ...] | null,
      "raw_abstract": "<string|null>"
    }
  ]
}

5) panel_heterogeneity (type == "panel_heterogeneity")

{
  "type": "panel_heterogeneity",
  "paper_id": "<string>",
  "moderation_patterns": [
    {
      "finding_id": "<string>",
      "moderator": "<string>",
      "dimension": "demographics" | "culture" | "traits" | "clinical" | "sensory" | "context" | "other",
      "levels_compared": ["<string>", ...] | null,
      "pattern": "<string>",
      "stats_summary": "<string|null>",
      "evidence_snippet": "<string|null>",
      "section": "<string|null>"
    }
  ] | null
}

6) panel_mechanisms (type == "panel_mechanisms")

{
  "type": "panel_mechanisms",
  "paper_id": "<string>",
  "mechanism_claims": [
    {
      "claim_id": "<string>",
      "claim_text": "<string>",
      "theory": "<string|null>",
      "phenomenon": "<string|null>",
      "role": "<string|null>",
      "strength": "<string|null>",
      "evidence_snippet": "<string|null>",
      "page_span": "<string|null>"
    }
  ] | null
}

7) panel_limits (type == "panel_limits")

{
  "type": "panel_limits",
  "paper_id": "<string>",
  "generalization_notes": ["<string>", ...] | null,
  "threats_to_validity": ["<string>", ...] | null,
  "future_work_notes": ["<string>", ...] | null
}

Be concise but specific in your summaries. Focus especially on any
aspects that would make the findings **more or less likely to generalise**
to different populations, cultures, or environments.
