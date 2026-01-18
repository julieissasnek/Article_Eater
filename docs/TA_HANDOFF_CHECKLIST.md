# TA Handoff Checklist — Article Eater v20.x

## 11. Worker idle timeout and single-instance lock

The background worker enforces:

- A single-instance lock (it binds to a localhost port and will refuse to
  start if another worker is already running).
- An idle timeout (by default 30 minutes, configurable via
  `AE_WORKER_IDLE_TIMEOUT_SECONDS`).

This means:

- If you try to start a second worker, you will get a clear
  "worker already running" message.
- If the worker sits idle (no jobs) for a long period, it will shut
  itself down to free the slot for the next user.

If you see the idle-timeout message, just start the worker again when
you are ready to run new jobs.
