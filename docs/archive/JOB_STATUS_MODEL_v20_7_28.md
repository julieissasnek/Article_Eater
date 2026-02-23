# Job Status Model – Article Eater v20.7.28

The `processing_queue` table (defined in `db/sql/015_core_tables.sql`) is
the canonical source of truth for long‑running jobs in the Article Eater
pipeline.

## Columns relevant to status / failure

- `job_id` (TEXT, PK) – opaque job identifier.
- `job_type` (TEXT) – one of `L0_harvest`, `L1_cluster`, `L2_extract`,
  `L3_synthesize`, `L4_expand`.
- `status` (TEXT) – one of:
  - `pending`  – created but not yet claimed by a worker,
  - `running`  – claimed by a worker and currently being processed,
  - `complete` – finished successfully,
  - `failed`   – finished with an error.
- `created_at` (TEXT) – when the job was inserted.
- `started_at` (TEXT) – first time a worker marked this job as `running`.
- `completed_at` (TEXT) – when the job reached a terminal state
  (`complete` or `failed`).
- `error` (TEXT) – a short message describing the failure, if any.

## Worker behaviour

The research worker in `app/worker.py` implements the following lifecycle:

1. A new job is inserted with `status = 'pending'`.
2. When `ResearchWorker.fetch_next_job` claims a job, but before any work
   is done, `ResearchWorker.process_job` calls:

       _update_status(job_id, "running")

   which sets `status = 'running'` and populates `started_at` (if null).

3. The job‑specific handler runs:
   - `run_l0_harvest` for `L0_harvest` jobs, or
   - `run_l2_extract` for `L2_extract` jobs.

4. If the handler returns without raising an exception, the worker calls:

       _update_status(job_id, "complete")

   which sets `status = 'complete'` and `completed_at = now`.

5. If the handler raises an exception that is not handled inside the
   handler, `process_job` catches it and calls:

       _update_status(job_id, "failed", error=str(exc))

   which sets `status = 'failed'`, records a short error message in
   `error`, and sets `completed_at = now`.

As a result, jobs should never remain in a non‑terminal state forever
unless the worker itself is unable to reach the database.

## Operational guidance

- A job stuck in `pending` usually indicates that:
  - no worker is running, or
  - workers are configured to process only certain `job_type`s.

- A job stuck in `running` with a very old `started_at` usually indicates
  a worker crash or DB connectivity issue. The new
  `scripts/job_status_inspector.py` helper will highlight such jobs.

- For teaching / lab scenarios, it is recommended that TAs run the
  inspector script periodically to monitor failed jobs and clean up test
  queues as needed.
