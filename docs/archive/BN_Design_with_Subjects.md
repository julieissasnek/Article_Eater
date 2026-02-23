# BN Design with Subject-Aware RuleGraph v2

This note explains how to use RuleGraph v2 to design Bayesian networks that:

- distinguish environment, subject, latent construct, and indicator nodes,
- encode heterogeneous treatment effects via subject attributes,
- separate measurement relations from structural and causal relations.

## Node classes

- Environment/context nodes: `environment_feature`, `structural_property`, `context_feature`.
- Subject nodes: derived from `subject_scope` and `subject_moderators` (age band, culture region, clinical status, key traits).
- Latent construct nodes: `latent_construct` and related constructs.
- Indicator nodes: `indicator` from Panel M.

## Edge classes

- `causal`: environment/subject → constructs.
- `correlational`: associations where direction is not asserted.
- `indicator` / `operationalization`: construct → indicator.
- `structural`: hierarchies and part–whole/context.
- `explanatory`: theory → phenomenon.
- `evidential`: meta-relations between rules (often used to weight priors, not instantiated as BN edges).

## Subject heterogeneity

Two main patterns:

1. Explicit subject parents:
   - subject nodes are parents of outcome constructs,
   - CPTs encode moderation patterns.

2. Hierarchical priors:
   - subject attributes parameterize priors over causal strengths,
   - RuleGraph v2 annotations indicate which parameters should depend on which attributes.

## Measurement model

From Panel M:

- For each construct with indicators:
  - create construct node,
  - create indicator nodes,
  - add construct → indicator edges.

Subject and context nodes can influence indicators directly where appropriate.

## Using relation_type and scope

A minimal export pattern:

- include causal edges for rules with `relation_type = "causal"`,
- include indicator edges from measurement rules,
- include structural edges from context/mechanism rules,
- add subject nodes and connections wherever `subject_moderators` exist.

Panel L and `subject_scope` guide how strongly these priors should be trusted for a given application context.
