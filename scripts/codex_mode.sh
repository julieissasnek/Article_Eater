#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/codex_mode.sh <max|balanced|low> [options] [-- <extra prompt text>]

Options:
  --task "<text>"        Task focus to include in startup prompt
  --cd <dir>             Working directory for new Codex session (default: current dir)
  --playbook <path>      Playbook path to reference in startup prompt
                         (default: docs/CODEX_MODEL_SWITCH_PLAYBOOK.md)
  --strategy <mode>      Session strategy:
                         new | resume-last | fork-last
                         (default: resume-last)
  --resume-last          Shortcut for --strategy resume-last
  --fork-last            Shortcut for --strategy fork-last
  --resume <session_id>  Resume specific session id
  --fork <session_id>    Fork specific session id
  --dry-run              Print command without launching Codex
  -h, --help             Show this help

Examples:
  scripts/codex_mode.sh low --task "Run 5-PDF pilot extraction"
  scripts/codex_mode.sh balanced --fork-last --task "Patch issues from previous run"
  scripts/codex_mode.sh max --fork-last --task "Discuss results at max quality"
  scripts/codex_mode.sh low --dry-run --task "Pilot run"
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

mode="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
shift

task_focus=""
workdir="$(pwd)"
playbook_path="docs/CODEX_MODEL_SWITCH_PLAYBOOK.md"
dry_run="false"
extra_prompt=""
strategy="resume-last"
session_id=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)
      [[ $# -ge 2 ]] || { echo "Missing value for --task" >&2; exit 1; }
      task_focus="$2"
      shift 2
      ;;
    --cd)
      [[ $# -ge 2 ]] || { echo "Missing value for --cd" >&2; exit 1; }
      workdir="$2"
      shift 2
      ;;
    --playbook)
      [[ $# -ge 2 ]] || { echo "Missing value for --playbook" >&2; exit 1; }
      playbook_path="$2"
      shift 2
      ;;
    --strategy)
      [[ $# -ge 2 ]] || { echo "Missing value for --strategy" >&2; exit 1; }
      strategy="$2"
      shift 2
      ;;
    --resume-last)
      strategy="resume-last"
      shift
      ;;
    --fork-last)
      strategy="fork-last"
      shift
      ;;
    --resume)
      [[ $# -ge 2 ]] || { echo "Missing value for --resume" >&2; exit 1; }
      strategy="resume"
      session_id="$2"
      shift 2
      ;;
    --fork)
      [[ $# -ge 2 ]] || { echo "Missing value for --fork" >&2; exit 1; }
      strategy="fork"
      session_id="$2"
      shift 2
      ;;
    --dry-run)
      dry_run="true"
      shift
      ;;
    --)
      shift
      extra_prompt="$*"
      break
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      # Treat trailing free text as extra prompt.
      extra_prompt="$*"
      break
      ;;
  esac
done

case "$mode" in
  max)
    model="gpt-5.3-codex"
    effort="xhigh"
    session_mode="MAX"
    ;;
  balanced)
    model="gpt-5.2-codex"
    effort="medium"
    session_mode="BALANCED"
    ;;
  low)
    model="gpt-5.1-codex-mini"
    effort="low"
    session_mode="LOW_COST"
    ;;
  *)
    echo "Unknown mode: $mode" >&2
    usage
    exit 1
    ;;
esac

if [[ -z "$task_focus" ]]; then
  if [[ "$session_mode" == "MAX" ]]; then
    task_focus="Review outputs and strategic discussion."
  else
    task_focus="Execution run for extraction/processing tasks."
  fi
fi

startup_prompt=$(
  cat <<EOF
Use playbook: $playbook_path
Session mode: $session_mode.
Task focus: $task_focus
If current model does not match this mode, give restart command first.
When done, provide next command to switch mode if needed.
EOF
)

if [[ -n "$extra_prompt" ]]; then
  startup_prompt="$startup_prompt

Extra instruction:
$extra_prompt"
fi

strategy="$(echo "$strategy" | tr '[:upper:]' '[:lower:]')"
case "$strategy" in
  new)
    cmd=(
      codex
      -m "$model"
      -c "model_reasoning_effort=\"$effort\""
      -C "$workdir"
      "$startup_prompt"
    )
    launch_note="Launching NEW Codex session."
    ;;
  resume-last)
    cmd=(
      codex
      resume
      --last
      -m "$model"
      -c "model_reasoning_effort=\"$effort\""
      -C "$workdir"
      "$startup_prompt"
    )
    launch_note="Resuming LAST session with model override."
    ;;
  fork-last)
    cmd=(
      codex
      fork
      --last
      -m "$model"
      -c "model_reasoning_effort=\"$effort\""
      -C "$workdir"
      "$startup_prompt"
    )
    launch_note="Forking LAST session with model override."
    ;;
  resume)
    [[ -n "$session_id" ]] || { echo "Missing session id for --resume" >&2; exit 1; }
    cmd=(
      codex
      resume
      "$session_id"
      -m "$model"
      -c "model_reasoning_effort=\"$effort\""
      -C "$workdir"
      "$startup_prompt"
    )
    launch_note="Resuming session $session_id with model override."
    ;;
  fork)
    [[ -n "$session_id" ]] || { echo "Missing session id for --fork" >&2; exit 1; }
    cmd=(
      codex
      fork
      "$session_id"
      -m "$model"
      -c "model_reasoning_effort=\"$effort\""
      -C "$workdir"
      "$startup_prompt"
    )
    launch_note="Forking session $session_id with model override."
    ;;
  *)
    echo "Unknown strategy: $strategy (expected new|resume-last|fork-last|resume|fork)" >&2
    exit 1
    ;;
esac

echo "$launch_note"
echo "Mode: $session_mode | Model: $model | Reasoning: $effort | Workdir: $workdir | Strategy: $strategy"

if [[ "$dry_run" == "true" ]]; then
  printf 'DRY RUN:'
  for arg in "${cmd[@]}"; do
    printf ' %q' "$arg"
  done
  printf '\n'
  exit 0
fi

"${cmd[@]}"
