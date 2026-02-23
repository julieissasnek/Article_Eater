## Paper Evaluation Orchestrator Improvements (Post-Sprint)

1. Verify contradictions/gaps receive explicit sections in the final report so high-VOI findings are immediately visible for reviewers.
2. Surface the web-of-belief query summary inside `report['summary']` or `report['recommendations']` so users can trace which beliefs informed each assessment.
3. Expand regression coverage beyond the two sample claims to include Ulrich 1984 and a fabricated contradiction/gap example as additional safeguards before the next sprint.
4. Audit `template_system_updates` to ensure each entry references the templates that actually contributed to the finding, not just the first match.
5. Automate reporting of VOI buckets (high/medium/low) in human-readable form when the CLI prints the evaluation summary.
