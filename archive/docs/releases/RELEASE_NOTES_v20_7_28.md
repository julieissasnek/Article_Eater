# Article Eater v20.7.28 – Job Status & Failure Visibility

This release is a small, surgical hardening on top of v20.7.27. The goal is
to make it very obvious when jobs fail and to give operators a fast way to
inspect the processing_queue table from the command line.

## Changes in this release

1. **Job status model documented.**
   The existing status lifecycle (`pending → running → complete / failed`)
   and `error` field in `processing_queue` are now explained in a dedicated
   note under `docs/`.

2. **CLI inspector for stuck or failed jobs.**
   A new script `scripts/job_status_inspector.py` provides a safe,
   read-only view over the job queue. It:
   - summarizes counts by status,
   - lists failed jobs with a short error snippet, and
   - highlights any `running` jobs whose `started_at` timestamp is older
     than a configurable threshold (default: 30 minutes).

   This is intended for TAs / operators to run periodically when debugging
   or during teaching sessions.

3. **No change to worker semantics.**
   The worker already:
   - marks jobs `running` before execution,
   - marks jobs `complete` on success, and
   - marks jobs `failed` and records the exception message in `error` on
     any unhandled exception.

   v20.7.28 does not change that behaviour; it only adds documentation and
   tooling around it.

This release is wire-compatible with v20.7.27: database schema, job types,
and queue semantics are unchanged.
