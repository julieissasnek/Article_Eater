"""
Overseer AI Diagnostician — Problem-Solving Intelligence
=========================================================

When reflexes fail or novel issues arise, the Overseer should not just log
"reflex failed" and stop.  It should THINK.  This module provides a structured
AI-powered diagnostic loop:

    1. TRIAGE  —  Classify severity and isolate the failing subsystem
    2. DIAGNOSE —  Build a causal hypothesis using system context
    3. PLAN     —  Generate a concrete repair plan (steps, risk, rollback)
    4. EXECUTE  —  Optionally auto-execute safe repairs
    5. LEARN    —  Record the diagnosis for future pattern matching

Model Tiers (cost-optimized):
    - Gemini 2.0 Flash:  ~$0.10/1M tokens, ~1s latency
      → Routine triage, known patterns, simple root-cause analysis
    - Gemini 2.5 Pro:    ~$1.25/1M tokens, ~3s latency
      → Complex multi-subsystem cascades, novel failure modes

Design principles:
    - Structured output (JSON) for machine-parseable repair plans
    - Human-in-the-loop: AI suggests, human approves for destructive actions
    - Audit trail: every diagnosis logged to overseer.db
    - Graceful fallback: works without API key (returns manual instructions)

References:
    - Klein (1998) — Recognition-Primed Decision — experts recognize patterns
    - Reason (1990) — Swiss Cheese Model — layered defenses against failure
    - Pearl (2009) — Causal Inference — diagnostic reasoning as causal query

Usage:
    from src.services.overseer_diagnostician import OverseerDiagnostician
    diag = OverseerDiagnostician()
    result = diag.diagnose_subsystem("t3_belief_engine", probe_result)
    if result.auto_executable:
        diag.execute_repair(result)
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# =============================================================================
# Data Models
# =============================================================================

class DiagnosticSeverity(Enum):
    """How urgent is this issue?"""
    CRITICAL = "critical"    # Data loss risk, system down
    HIGH = "high"            # Major feature degraded
    MEDIUM = "medium"        # Minor degradation, workaround exists
    LOW = "low"              # Cosmetic or informational

class RepairRisk(Enum):
    """Risk level of a proposed repair."""
    SAFE = "safe"            # Read-only or idempotent operation
    LOW = "low"              # Reversible write operation
    MEDIUM = "medium"        # Write with side effects
    HIGH = "high"            # Destructive or irreversible
    CRITICAL = "critical"    # Could make things worse


@dataclass
class RepairStep:
    """A single step in a repair plan."""
    step_number: int
    action: str              # Human-readable description
    command: str             # Actual code/command to execute
    risk: RepairRisk
    rollback: str            # How to undo this step
    auto_executable: bool    # Can this be auto-executed?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "action": self.action,
            "command": self.command,
            "risk": self.risk.value,
            "rollback": self.rollback,
            "auto_executable": self.auto_executable,
        }


@dataclass
class DiagnosticResult:
    """Complete result from an AI diagnostic session."""
    subsystem_id: str
    timestamp: str
    severity: DiagnosticSeverity
    hypothesis: str          # Root cause hypothesis
    evidence: List[str]      # Supporting evidence
    repair_plan: List[RepairStep]
    confidence: float        # 0.0–1.0
    model_used: str          # Which Gemini model was used
    auto_executable: bool    # Can the entire plan be auto-executed?
    reasoning_trace: str     # Full AI reasoning for audit
    escalation_needed: bool  # Should a human review this?
    duration_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subsystem_id": self.subsystem_id,
            "timestamp": self.timestamp,
            "severity": self.severity.value,
            "hypothesis": self.hypothesis,
            "evidence": self.evidence,
            "repair_plan": [s.to_dict() for s in self.repair_plan],
            "confidence": self.confidence,
            "model_used": self.model_used,
            "auto_executable": self.auto_executable,
            "reasoning_trace": self.reasoning_trace[:500],  # Truncate for storage
            "escalation_needed": self.escalation_needed,
            "duration_ms": self.duration_ms,
        }


# =============================================================================
# Known Patterns — Local intelligence before calling AI
# =============================================================================

KNOWN_PATTERNS: Dict[str, Dict[str, Any]] = {
    "db_resolves_0": {
        "pattern": "db_infrastructure probe reports db_resolves=0",
        "hypothesis": "Database file not found at expected path",
        "steps": [
            {"action": "Check DB path in db_locator", "command": "python3 -c 'from src.services.db_locator import get_web_db; print(get_web_db())'", "risk": "safe"},
            {"action": "Verify file exists", "command": "ls -la data/*.db", "risk": "safe"},
            {"action": "Rebuild DB if missing", "command": "python3 -c 'from src.services.db_locator import get_web_db; print(\"DB at:\", get_web_db())'", "risk": "low"},
        ],
        "severity": "critical",
    },
    "extraction_count_low": {
        "pattern": "extraction_integration has fewer than 800 files",
        "hypothesis": "Extraction pipeline has not run or output directory is wrong",
        "steps": [
            {"action": "Count extraction files", "command": "ls data/extractions/*.json 2>/dev/null | wc -l", "risk": "safe"},
            {"action": "Check pipeline logs", "command": "tail -20 data/logs/extraction.log 2>/dev/null || echo 'No log found'", "risk": "safe"},
        ],
        "severity": "medium",
    },
    "classification_rate_low": {
        "pattern": "t3_belief_engine classification_rate below 0.70",
        "hypothesis": "IV classifier may have insufficient training data or new variable types",
        "steps": [
            {"action": "Check classification stats", "command": "python3 -c 'from src.services.iv_dv_classifier import IVDVClassifier; c=IVDVClassifier(); print(json.dumps(c.classification_stats(), indent=2))' 2>/dev/null", "risk": "safe"},
            {"action": "Identify unclassified IVs", "command": "python3 -c 'from src.services.iv_dv_classifier import IVDVClassifier; c=IVDVClassifier(); [print(v) for v in list(c._iv_cache.values())[:5] if v.method==\"unclassified\"]' 2>/dev/null", "risk": "safe"},
        ],
        "severity": "medium",
    },
    "bn_export_missing": {
        "pattern": "bayesian_network bn_export_exists=0",
        "hypothesis": "BN export has not been generated or was deleted",
        "steps": [
            {"action": "Check BN file", "command": "ls -la data/bn_export.json 2>/dev/null || echo 'Missing'", "risk": "safe"},
            {"action": "Regenerate BN", "command": "python3 -c 'from src.services.web_of_belief import WebOfBelief; w=WebOfBelief(); w.export_bn()' 2>/dev/null", "risk": "low"},
        ],
        "severity": "medium",
    },
    "module_not_importable": {
        "pattern": "module_importable=0 for any subsystem",
        "hypothesis": "Missing dependency or syntax error in module",
        "steps": [
            {"action": "Attempt import with traceback", "command": "python3 -c 'import {module}' 2>&1", "risk": "safe"},
        ],
        "severity": "high",
    },
}


# =============================================================================
# AI Diagnostician
# =============================================================================

class OverseerDiagnostician:
    """
    AI-powered problem-solving intelligence for the Overseer.

    Three tiers of intelligence:
    1. LOCAL PATTERNS — Instant recognition of known failure modes
    2. GEMINI FLASH  — Fast diagnosis for routine issues ($0.10/1M tokens)
    3. GEMINI PRO    — Deep analysis for complex multi-system cascades

    Usage:
        diag = OverseerDiagnostician()
        result = diag.diagnose("t3_belief_engine", probe_metrics, probe_failures)
        print(result.hypothesis)
        for step in result.repair_plan:
            print(f"  {step.step_number}. {step.action} [{step.risk.value}]")
    """

    # Configurable model names
    FLASH_MODEL = "gemini-2.0-flash"
    PRO_MODEL = "gemini-2.5-pro"

    # Threshold for escalating from Flash to Pro
    ESCALATION_CONFIDENCE_THRESHOLD = 0.5

    def __init__(
        self,
        api_key: Optional[str] = None,
        prefer_local: bool = True,
        auto_execute_safe: bool = False,
        overseer_db_path: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self.prefer_local = prefer_local
        self.auto_execute_safe = auto_execute_safe
        self.overseer_db_path = overseer_db_path or str(DATA_DIR / "overseer.db")
        self._diagnosis_history: List[DiagnosticResult] = []

    # ── Main Entry Point ──

    def diagnose(
        self,
        subsystem_id: str,
        metrics: Dict[str, Any],
        failures: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> DiagnosticResult:
        """
        Full diagnostic loop: triage → local pattern match → AI diagnosis.

        Args:
            subsystem_id: Which subsystem is failing
            metrics:      Probe metrics (e.g., {"belief_count": 3500})
            failures:     List of failure messages from health probe
            context:      Additional context (recent logs, related subsystems)

        Returns:
            DiagnosticResult with hypothesis, repair plan, and confidence
        """
        start = time.time()

        # ── TIER 1: Local Pattern Recognition ──
        if self.prefer_local:
            local_result = self._match_known_pattern(subsystem_id, metrics, failures)
            if local_result:
                local_result.duration_ms = (time.time() - start) * 1000
                self._persist_diagnosis(local_result)
                return local_result

        # ── TIER 2: Gemini Flash (fast, cheap) ──
        if self.api_key:
            flash_result = self._ai_diagnose(
                subsystem_id, metrics, failures, context,
                model=self.FLASH_MODEL
            )
            flash_result.duration_ms = (time.time() - start) * 1000

            # ── TIER 3: Escalate to Pro if Flash is uncertain ──
            if (flash_result.confidence < self.ESCALATION_CONFIDENCE_THRESHOLD
                    or flash_result.severity == DiagnosticSeverity.CRITICAL):
                logger.info(
                    f"Escalating {subsystem_id} to {self.PRO_MODEL} "
                    f"(Flash confidence: {flash_result.confidence:.2f})"
                )
                pro_result = self._ai_diagnose(
                    subsystem_id, metrics, failures, context,
                    model=self.PRO_MODEL,
                    prior_diagnosis=flash_result,
                )
                pro_result.duration_ms = (time.time() - start) * 1000
                self._persist_diagnosis(pro_result)
                return pro_result

            self._persist_diagnosis(flash_result)
            return flash_result

        # ── Fallback: No AI available ──
        fallback = DiagnosticResult(
            subsystem_id=subsystem_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=DiagnosticSeverity.MEDIUM,
            hypothesis=f"Subsystem {subsystem_id} is failing but no AI model is available for diagnosis",
            evidence=failures,
            repair_plan=[
                RepairStep(1, "Manual investigation required",
                          f"Review health probe for {subsystem_id}",
                          RepairRisk.SAFE, "N/A", False)
            ],
            confidence=0.0,
            model_used="none",
            auto_executable=False,
            reasoning_trace="No API key available. Set GOOGLE_API_KEY for AI diagnosis.",
            escalation_needed=True,
            duration_ms=(time.time() - start) * 1000,
        )
        self._persist_diagnosis(fallback)
        return fallback

    # ── Batch Diagnosis ──

    def diagnose_all_failing(
        self,
        health_report: Dict[str, Any],
    ) -> List[DiagnosticResult]:
        """
        Diagnose all failing/degraded subsystems from a health report.

        Returns list of DiagnosticResults sorted by severity.
        """
        results = []
        for sid, info in health_report.get("subsystems", {}).items():
            if info.get("status") in ("failing", "degraded"):
                result = self.diagnose(
                    sid,
                    info.get("metrics", {}),
                    info.get("failures", []),
                )
                results.append(result)

        # Sort: critical first, then by confidence descending
        severity_order = {
            DiagnosticSeverity.CRITICAL: 0,
            DiagnosticSeverity.HIGH: 1,
            DiagnosticSeverity.MEDIUM: 2,
            DiagnosticSeverity.LOW: 3,
        }
        results.sort(key=lambda r: (severity_order.get(r.severity, 9), -r.confidence))
        return results

    # ── Pattern Matching (Local) ──

    def _match_known_pattern(
        self,
        subsystem_id: str,
        metrics: Dict[str, Any],
        failures: List[str],
    ) -> Optional[DiagnosticResult]:
        """Match against known failure patterns without calling AI."""

        # Check specific metric-based patterns
        for metric_key, value in metrics.items():
            pattern_key = f"{metric_key}_{value}" if isinstance(value, int) else None

            # db_resolves=0
            if metric_key == "db_resolves" and value == 0:
                return self._build_local_result(subsystem_id, "db_resolves_0", metrics, failures)

            # extraction_count < 800
            if metric_key == "extraction_count" and isinstance(value, (int, float)) and value < 800:
                return self._build_local_result(subsystem_id, "extraction_count_low", metrics, failures)

            # classification_rate < 0.70
            if metric_key == "classification_rate" and isinstance(value, (int, float)) and value < 0.70:
                return self._build_local_result(subsystem_id, "classification_rate_low", metrics, failures)

            # bn_export_exists=0
            if metric_key == "bn_export_exists" and value == 0:
                return self._build_local_result(subsystem_id, "bn_export_missing", metrics, failures)

            # module_importable=0
            if metric_key == "module_importable" and value == 0:
                return self._build_local_result(subsystem_id, "module_not_importable", metrics, failures)

        return None

    def _build_local_result(
        self,
        subsystem_id: str,
        pattern_key: str,
        metrics: Dict[str, Any],
        failures: List[str],
    ) -> DiagnosticResult:
        """Build a DiagnosticResult from a known pattern."""
        pattern = KNOWN_PATTERNS[pattern_key]
        steps = []
        for i, step_def in enumerate(pattern["steps"], 1):
            # Template substitution for commands
            cmd = step_def["command"]
            if "{module}" in cmd:
                # Try to use the module from failure messages
                module = "unknown"
                for f in failures:
                    if "not importable" in f:
                        module = f.split(" not importable")[0].strip()
                        break
                cmd = cmd.replace("{module}", module)

            steps.append(RepairStep(
                step_number=i,
                action=step_def["action"],
                command=cmd,
                risk=RepairRisk[step_def["risk"].upper()],
                rollback="Undo manually" if step_def["risk"] != "safe" else "N/A (read-only)",
                auto_executable=step_def["risk"] == "safe",
            ))

        severity_map = {
            "critical": DiagnosticSeverity.CRITICAL,
            "high": DiagnosticSeverity.HIGH,
            "medium": DiagnosticSeverity.MEDIUM,
            "low": DiagnosticSeverity.LOW,
        }

        return DiagnosticResult(
            subsystem_id=subsystem_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=severity_map.get(pattern["severity"], DiagnosticSeverity.MEDIUM),
            hypothesis=pattern["hypothesis"],
            evidence=failures + [f"Matched known pattern: {pattern_key}"],
            repair_plan=steps,
            confidence=0.85,  # High confidence for known patterns
            model_used="local_pattern",
            auto_executable=all(s.auto_executable for s in steps),
            reasoning_trace=f"Pattern match: {pattern['pattern']}",
            escalation_needed=pattern["severity"] in ("critical", "high"),
            duration_ms=0,
        )

    # ── AI Diagnosis ──

    def _ai_diagnose(
        self,
        subsystem_id: str,
        metrics: Dict[str, Any],
        failures: List[str],
        context: Optional[Dict[str, Any]],
        model: str,
        prior_diagnosis: Optional[DiagnosticResult] = None,
    ) -> DiagnosticResult:
        """Run AI-powered diagnosis using Gemini."""

        prompt = self._build_diagnosis_prompt(
            subsystem_id, metrics, failures, context, prior_diagnosis
        )

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            ai_model = genai.GenerativeModel(model)

            response = ai_model.generate_content(prompt)
            raw_text = response.text or ""

            return self._parse_ai_response(subsystem_id, raw_text, model)

        except ImportError:
            logger.warning("google.generativeai not installed")
            return self._create_fallback_result(subsystem_id, failures, model,
                                                  "google.generativeai not installed")
        except Exception as e:
            logger.warning(f"AI diagnosis failed ({model}): {e}")
            return self._create_fallback_result(subsystem_id, failures, model, str(e))

    def _build_diagnosis_prompt(
        self,
        subsystem_id: str,
        metrics: Dict[str, Any],
        failures: List[str],
        context: Optional[Dict[str, Any]],
        prior_diagnosis: Optional[DiagnosticResult] = None,
    ) -> str:
        """Build a structured diagnostic prompt for the AI."""

        # Get subsystem definition for context
        subsystem_info = ""
        try:
            from src.services.overseer_self_healing import build_subsystem_registry
            registry = build_subsystem_registry()
            defn = registry.get(subsystem_id)
            if defn:
                subsystem_info = (
                    f"Name: {defn.name}\n"
                    f"Category: {defn.category}\n"
                    f"Dependencies: {', '.join(defn.depends_on) or 'none'}\n"
                    f"Success Conditions:\n"
                )
                for c in defn.success_conditions:
                    actual = metrics.get(c.metric, "N/A")
                    passed = "✅" if c.check(actual) else "❌"
                    subsystem_info += f"  {passed} {c.description}: {c.metric} {c.operator} {c.threshold} (actual: {actual})\n"
        except Exception:
            subsystem_info = f"Subsystem: {subsystem_id}\n"

        prior_text = ""
        if prior_diagnosis:
            prior_text = (
                f"\n## Prior Diagnosis (Flash model, confidence={prior_diagnosis.confidence:.2f})\n"
                f"Hypothesis: {prior_diagnosis.hypothesis}\n"
                f"This diagnosis needs deeper analysis.\n"
            )

        prompt = f"""# ATLAS Overseer Diagnostic Session

You are the diagnostic intelligence for the ATLAS Overseer system — a self-monitoring
research pipeline for architectural psychology.  A subsystem has failed its health check.

## System Context
{subsystem_info}

## Current Probe Results
Metrics: {json.dumps(metrics, indent=2)}
Failures: {json.dumps(failures, indent=2)}
{prior_text}
{f"## Additional Context" + chr(10) + json.dumps(context, indent=2) if context else ""}

## Your Task
Provide a structured diagnosis in EXACTLY this JSON format:
```json
{{
  "severity": "critical|high|medium|low",
  "hypothesis": "One-sentence root cause hypothesis",
  "evidence": ["evidence item 1", "evidence item 2"],
  "confidence": 0.0 to 1.0,
  "repair_steps": [
    {{
      "action": "Human-readable description",
      "command": "Exact Python/shell command to run",
      "risk": "safe|low|medium|high|critical",
      "rollback": "How to undo this step"
    }}
  ],
  "escalation_needed": true/false,
  "reasoning": "Brief explanation of your diagnostic reasoning"
}}
```

Rules:
1. Be SPECIFIC — name actual files, functions, and modules
2. Commands should be executable Python one-liners or shell commands
3. Mark "safe" only for read-only diagnostics
4. Set escalation_needed=true if repair could cause data loss
5. Include rollback instructions for any write operation
"""
        return prompt

    def _parse_ai_response(
        self,
        subsystem_id: str,
        raw_text: str,
        model_used: str,
    ) -> DiagnosticResult:
        """Parse structured JSON from AI response."""

        # Extract JSON block from response
        json_str = raw_text
        if "```json" in raw_text:
            json_str = raw_text.split("```json")[1].split("```")[0]
        elif "```" in raw_text:
            json_str = raw_text.split("```")[1].split("```")[0]

        try:
            data = json.loads(json_str.strip())
        except json.JSONDecodeError:
            # Fallback: treat entire response as reasoning
            return DiagnosticResult(
                subsystem_id=subsystem_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                severity=DiagnosticSeverity.MEDIUM,
                hypothesis="AI provided unstructured response (see reasoning trace)",
                evidence=[],
                repair_plan=[],
                confidence=0.3,
                model_used=model_used,
                auto_executable=False,
                reasoning_trace=raw_text[:2000],
                escalation_needed=True,
                duration_ms=0,
            )

        # Parse structured response
        severity_map = {
            "critical": DiagnosticSeverity.CRITICAL,
            "high": DiagnosticSeverity.HIGH,
            "medium": DiagnosticSeverity.MEDIUM,
            "low": DiagnosticSeverity.LOW,
        }
        risk_map = {
            "safe": RepairRisk.SAFE,
            "low": RepairRisk.LOW,
            "medium": RepairRisk.MEDIUM,
            "high": RepairRisk.HIGH,
            "critical": RepairRisk.CRITICAL,
        }

        steps = []
        for i, step_data in enumerate(data.get("repair_steps", []), 1):
            risk = risk_map.get(step_data.get("risk", "medium"), RepairRisk.MEDIUM)
            steps.append(RepairStep(
                step_number=i,
                action=step_data.get("action", ""),
                command=step_data.get("command", ""),
                risk=risk,
                rollback=step_data.get("rollback", "Manual review"),
                auto_executable=(risk == RepairRisk.SAFE and self.auto_execute_safe),
            ))

        return DiagnosticResult(
            subsystem_id=subsystem_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=severity_map.get(data.get("severity", "medium"), DiagnosticSeverity.MEDIUM),
            hypothesis=data.get("hypothesis", "Unknown"),
            evidence=data.get("evidence", []),
            repair_plan=steps,
            confidence=float(data.get("confidence", 0.5)),
            model_used=model_used,
            auto_executable=all(s.auto_executable for s in steps) if steps else False,
            reasoning_trace=data.get("reasoning", raw_text[:500]),
            escalation_needed=data.get("escalation_needed", False),
            duration_ms=0,
        )

    def _create_fallback_result(
        self,
        subsystem_id: str,
        failures: List[str],
        model: str,
        error: str,
    ) -> DiagnosticResult:
        """Create a fallback result when AI is unavailable."""
        return DiagnosticResult(
            subsystem_id=subsystem_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=DiagnosticSeverity.MEDIUM,
            hypothesis=f"AI diagnosis unavailable: {error}",
            evidence=failures,
            repair_plan=[
                RepairStep(1, "Manual investigation required",
                          f"Investigate {subsystem_id} failures manually",
                          RepairRisk.SAFE, "N/A", False)
            ],
            confidence=0.0,
            model_used=f"{model} (failed)",
            auto_executable=False,
            reasoning_trace=f"Error: {error}",
            escalation_needed=True,
            duration_ms=0,
        )

    # ── Execute Repair ──

    def execute_repair(
        self,
        diagnosis: DiagnosticResult,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the repair plan from a diagnosis.

        Only executes steps marked as auto_executable.
        In dry_run mode (default), only shows what would be done.
        """
        results = {"steps_executed": 0, "steps_skipped": 0, "outputs": []}

        for step in diagnosis.repair_plan:
            if not step.auto_executable:
                results["steps_skipped"] += 1
                results["outputs"].append({
                    "step": step.step_number,
                    "action": step.action,
                    "status": "skipped",
                    "reason": f"Risk too high ({step.risk.value})",
                })
                continue

            if dry_run:
                results["outputs"].append({
                    "step": step.step_number,
                    "action": step.action,
                    "command": step.command,
                    "status": "dry_run",
                })
                results["steps_executed"] += 1
                continue

            # Actually execute safe commands
            try:
                import subprocess
                result = subprocess.run(
                    step.command, shell=True, capture_output=True,
                    text=True, timeout=30
                )
                results["outputs"].append({
                    "step": step.step_number,
                    "action": step.action,
                    "status": "success" if result.returncode == 0 else "failed",
                    "stdout": result.stdout[:500],
                    "stderr": result.stderr[:200],
                })
                results["steps_executed"] += 1
            except Exception as e:
                results["outputs"].append({
                    "step": step.step_number,
                    "action": step.action,
                    "status": "error",
                    "error": str(e),
                })

        return results

    # ── Persistence ──

    def _persist_diagnosis(self, result: DiagnosticResult) -> None:
        """Save diagnosis to overseer.db for audit trail."""
        self._diagnosis_history.append(result)
        try:
            conn = sqlite3.connect(self.overseer_db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS diagnostic_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subsystem_id TEXT,
                    timestamp TEXT,
                    severity TEXT,
                    hypothesis TEXT,
                    confidence REAL,
                    model_used TEXT,
                    auto_executable INTEGER,
                    escalation_needed INTEGER,
                    duration_ms REAL,
                    result_json TEXT
                )
            """)
            conn.execute(
                "INSERT INTO diagnostic_sessions "
                "(subsystem_id, timestamp, severity, hypothesis, confidence, "
                "model_used, auto_executable, escalation_needed, duration_ms, result_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    result.subsystem_id,
                    result.timestamp,
                    result.severity.value,
                    result.hypothesis,
                    result.confidence,
                    result.model_used,
                    1 if result.auto_executable else 0,
                    1 if result.escalation_needed else 0,
                    result.duration_ms,
                    json.dumps(result.to_dict()),
                )
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Could not persist diagnosis: {e}")

    # ── Reporting ──

    def get_diagnosis_summary(self) -> Dict[str, Any]:
        """Get summary of all diagnostic sessions."""
        if not self._diagnosis_history:
            return {"total_sessions": 0}

        by_model = {}
        by_severity = {}
        for d in self._diagnosis_history:
            by_model[d.model_used] = by_model.get(d.model_used, 0) + 1
            by_severity[d.severity.value] = by_severity.get(d.severity.value, 0) + 1

        return {
            "total_sessions": len(self._diagnosis_history),
            "by_model": by_model,
            "by_severity": by_severity,
            "mean_confidence": sum(d.confidence for d in self._diagnosis_history) / len(self._diagnosis_history),
            "auto_executable_pct": sum(1 for d in self._diagnosis_history if d.auto_executable) / len(self._diagnosis_history),
        }


# =============================================================================
# Integration: Wire into Overseer heal() cycle
# =============================================================================

def diagnose_and_heal(
    overseer_db: str = "data/overseer.db",
) -> Dict[str, Any]:
    """
    Run the full diagnostic loop:
    1. Check all subsystems via health probes
    2. Diagnose all failing ones via AI
    3. Generate repair plans
    4. Return comprehensive report

    Usage:
        from src.services.overseer_diagnostician import diagnose_and_heal
        report = diagnose_and_heal()
        for d in report["diagnoses"]:
            print(f"{d['subsystem_id']}: {d['hypothesis']}")
    """
    from src.services.overseer_self_healing import SubsystemHealthChecker

    checker = SubsystemHealthChecker()
    health = checker.check_all()

    diag = OverseerDiagnostician(overseer_db_path=overseer_db)
    diagnoses = diag.diagnose_all_failing(health)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health_summary": {
            "total": health["total_subsystems"],
            "healthy": health["healthy"],
            "degraded": health["degraded"],
            "failing": health["failing"],
        },
        "diagnoses": [d.to_dict() for d in diagnoses],
        "diagnosis_summary": diag.get_diagnosis_summary(),
    }


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    report = diagnose_and_heal()
    print(json.dumps(report, indent=2))
