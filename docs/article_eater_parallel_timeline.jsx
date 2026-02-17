import { useState } from "react";

const agents = [
  {
    name: "Opus",
    role: "Theory Architect",
    color: "#f59e0b",
    tasks: [
      { id: "O1", label: "Panel L-I: Light & Luminance", detail: "Doc 34 · Templates L1–L5 · Circadian, luminance PE, daylight cognition", start: 0, end: 3 },
      { id: "O2", label: "Panel MAT-I: Materials + Haptic", detail: "Doc 35 · Templates MAT1–MAT5 · Somatosensory PE, thermal comfort, C-tactile", start: 3, end: 6 },
      { id: "O3", label: "Panel SC-I: Space Syntax", detail: "Doc 36 · Templates SC1–SC4 · Integration metrics, isovist PE, promenade", start: 6, end: 9 },
      { id: "O4", label: "Update Doc 33 Cross-Ref", detail: "Add new templates to attribute index, recalculate coverage ratings", start: 9, end: 10 },
    ],
  },
  {
    name: "Codex",
    role: "Schema & API Design",
    color: "#3b82f6",
    tasks: [
      { id: "CX1", label: "CX-1: TypeScript Interfaces", detail: "Template, CausalLink, ReductionClaim, AttributeDomain, MechanisticClaim types", start: 0, end: 1.5, critical: true },
      { id: "CX2", label: "CX-2: API Layer Design", detail: "Query specs: attribute lookup, mechanism lookup, gap analysis, evaluateFinding", start: 1.5, end: 3.5 },
      { id: "CX3", label: "CX-3: Cross-Repo Contract", detail: "Extend existing contract with theory tier interfaces, versioning scheme", start: 3.5, end: 5 },
      { id: "CX4", label: "CX-4: Extraction→Theory Interface", detail: "ExtractedFinding → TheoryMatchInput spec. Depends on CC-5 audit results", start: 4, end: 6, depends: "CC5", highlight: true },
      { id: "CX5", label: "Review: New Template Types", detail: "Extend types if L-I / MAT-I templates need new fields", start: 7, end: 8 },
    ],
  },
  {
    name: "Claude Code",
    role: "Primary Implementation",
    color: "#10b981",
    tasks: [
      { id: "CC5", label: "CC-5: PDF & Abstract Table Audit", detail: "Audit extraction schemas, run quality check on sample papers, identify gaps for theory-tier interface", start: 0, end: 2.5, highlight: true },
      { id: "CC1", label: "CC-1: Template Encoding (63)", detail: "T1–T40, M1–M17, AX1–AX6 → JSON + templateRegistry.ts", start: 1.5, end: 5, critical: true, depends: "CX1" },
      { id: "CC2", label: "CC-2: ReductionClaim Encoding", detail: "ART×4, SRT×3, Biophilia×3 → JSON + reductionRegistry.ts", start: 4, end: 6, depends: "CX1" },
      { id: "CC3", label: "CC-3: Cross-Ref Index Encoding", detail: "Doc 33 → Attribute index + Mechanism index + Matrix lookup", start: 5, end: 7, depends: "CX1" },
      { id: "CC4", label: "CC-4: Epistemic Core Bridge", detail: "MechanisticClaim integration, template → claim generation", start: 6, end: 8.5, depends: "CX2" },
      { id: "CC6", label: "CC-6: Implement Extraction→Theory Map", detail: "Build mapping function from CX-4 spec, fix extraction schema gaps from CC-5", start: 7, end: 9, depends: "CX4", highlight: true },
      { id: "CC7", label: "Encode New Templates", detail: "Add L1–L5, MAT1–MAT5, SC1–SC4 as Opus delivers them", start: 8.5, end: 10 },
    ],
  },
  {
    name: "Antigravity",
    role: "Test Suite & Validation",
    color: "#ef4444",
    tasks: [
      { id: "AG1a", label: "AG-1a: Design Validation Suite", detail: "Structural, referential integrity, content spot-check test specs", start: 0.5, end: 2.5 },
      { id: "AG1b", label: "AG-1b: Run Validation Suite", detail: "Execute against CC-1/CC-2 output, iterate on failures", start: 5, end: 6.5, depends: "CC1" },
      { id: "AG2", label: "AG-2: Expert Workflow Test", detail: "Wood-surfaces-stress canonical test from Doc 33 §D5", start: 7, end: 8.5, depends: "CC3" },
      { id: "AG3", label: "AG-3: Drift Check Infrastructure", detail: "CI-style check for new template additions, coverage recalculation", start: 8, end: 9 },
      { id: "AG4", label: "AG-4: Extraction→Theory Round-Trip", detail: "3 scenarios: single-domain, multi-domain, gap-detection. Full pipeline test.", start: 8.5, end: 10, depends: "CC6", highlight: true },
      { id: "AG5", label: "AG-5: Validate New Templates", detail: "Run suite against L1–L5, MAT1–MAT5, SC1–SC4. Re-run Scenario 3 post-Light panel", start: 9.5, end: 10.5 },
    ],
  },
];

const dependencies = [
  { from: "CX1", to: "CC1" },
  { from: "CX1", to: "CC2" },
  { from: "CX1", to: "CC3" },
  { from: "CX2", to: "CC4" },
  { from: "CC1", to: "AG1b" },
  { from: "CC3", to: "AG2" },
  { from: "CC5", to: "CX4" },
  { from: "CX4", to: "CC6" },
  { from: "CC6", to: "AG4" },
];

const totalUnits = 11;
const unitWidth = 82;
const rowHeight = 36;
const labelWidth = 130;
const headerHeight = 56;
const agentHeaderHeight = 32;

export default function GanttChart() {
  const [hoveredTask, setHoveredTask] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);

  const chartWidth = labelWidth + totalUnits * unitWidth + 30;

  let yOffset = headerHeight + 8;
  const agentBlocks = agents.map((agent) => {
    const blockStart = yOffset;
    yOffset += agentHeaderHeight;
    const taskPositions = agent.tasks.map((task, i) => {
      const y = yOffset + i * (rowHeight + 3);
      return { ...task, y };
    });
    yOffset += agent.tasks.length * (rowHeight + 3) + 10;
    return { ...agent, blockStart, taskPositions, blockEnd: yOffset };
  });

  const totalHeight = yOffset + 100;

  const getTaskPos = (taskId) => {
    for (const block of agentBlocks) {
      for (const t of block.taskPositions) {
        if (t.id === taskId) return t;
      }
    }
    return null;
  };

  const weekLabels = ["W1", "", "", "W2", "", "", "W3", "", "", "W4", ""];

  return (
    <div style={{ fontFamily: "system-ui, -apple-system, sans-serif", background: "#0f172a", color: "#e2e8f0", minHeight: "100vh", padding: "20px" }}>
      <div style={{ maxWidth: 1120, margin: "0 auto" }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f8fafc", marginBottom: 2 }}>
          Article Eater — Parallel Task Timeline V1.1
        </h1>
        <p style={{ fontSize: 12, color: "#94a3b8", marginBottom: 16 }}>
          Adds extraction audit (CC-5), extraction→theory interface (CX-4), and round-trip test (AG-4). Two critical paths converge at AG-4.
        </p>

        <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
          {agents.map((a) => (
            <button
              key={a.name}
              onClick={() => setSelectedAgent(selectedAgent === a.name ? null : a.name)}
              style={{
                padding: "5px 12px", borderRadius: 6,
                border: `2px solid ${selectedAgent === a.name ? a.color : "transparent"}`,
                background: selectedAgent === a.name ? a.color + "22" : "#1e293b",
                color: a.color, fontSize: 12, fontWeight: 600, cursor: "pointer",
              }}
            >
              {a.name} <span style={{ fontWeight: 400, color: "#94a3b8", fontSize: 11 }}>— {a.role}</span>
            </button>
          ))}
          <button
            onClick={() => setSelectedAgent(null)}
            style={{
              padding: "5px 12px", borderRadius: 6, border: "1px solid #334155",
              background: "#1e293b", color: "#94a3b8", fontSize: 12, cursor: "pointer",
            }}
          >
            Show all
          </button>
        </div>

        <div style={{ overflowX: "auto", borderRadius: 10, border: "1px solid #334155" }}>
          <svg width={chartWidth} height={totalHeight} style={{ display: "block", background: "#1e293b" }}>

            {/* Time grid */}
            {Array.from({ length: totalUnits + 1 }).map((_, i) => (
              <g key={`grid-${i}`}>
                <line
                  x1={labelWidth + i * unitWidth} y1={headerHeight}
                  x2={labelWidth + i * unitWidth} y2={totalHeight - 50}
                  stroke={i % 3 === 0 ? "#475569" : "#334155"}
                  strokeWidth={i % 3 === 0 ? 1.2 : 0.5}
                  strokeDasharray={i % 3 === 0 ? "none" : "3,3"}
                />
                {i < totalUnits && (
                  <text x={labelWidth + i * unitWidth + unitWidth / 2} y={18} textAnchor="middle" fill="#64748b" fontSize={10}>
                    {weekLabels[i]}
                  </text>
                )}
              </g>
            ))}

            {/* Phase labels */}
            <rect x={labelWidth} y={26} width={3 * unitWidth} height={16} rx={3} fill="#6366f118" />
            <text x={labelWidth + 1.5 * unitWidth} y={37} textAnchor="middle" fill="#818cf8" fontSize={9} fontWeight={600}>Contracts + Audit</text>

            <rect x={labelWidth + 1.5 * unitWidth} y={26} width={5.5 * unitWidth} height={16} rx={3} fill="#8b5cf618" />
            <text x={labelWidth + 4.25 * unitWidth} y={37} textAnchor="middle" fill="#a78bfa" fontSize={9} fontWeight={600}>Core Encoding</text>

            <rect x={labelWidth + 5 * unitWidth} y={26} width={4 * unitWidth} height={16} rx={3} fill="#a855f718" />
            <text x={labelWidth + 7 * unitWidth} y={37} textAnchor="middle" fill="#c084fc" fontSize={9} fontWeight={600}>Validation + Bridge</text>

            <rect x={labelWidth + 8 * unitWidth} y={26} width={3 * unitWidth} height={16} rx={3} fill="#c084fc18" />
            <text x={labelWidth + 9.5 * unitWidth} y={37} textAnchor="middle" fill="#d8b4fe" fontSize={9} fontWeight={600}>New Templates In</text>

            {/* Agent blocks */}
            {agentBlocks.map((block) => {
              const dimmed = selectedAgent && selectedAgent !== block.name;
              return (
                <g key={block.name} opacity={dimmed ? 0.18 : 1} style={{ transition: "opacity 0.2s" }}>
                  <rect
                    x={3} y={block.blockStart} width={chartWidth - 6}
                    height={block.blockEnd - block.blockStart - 6}
                    rx={7} fill={block.color + "06"} stroke={block.color + "25"} strokeWidth={1}
                  />
                  <text x={10} y={block.blockStart + 22} fill={block.color} fontSize={13} fontWeight={700}>
                    {block.name}
                  </text>

                  {block.taskPositions.map((task) => {
                    const x = labelWidth + task.start * unitWidth;
                    const w = (task.end - task.start) * unitWidth;
                    const isHovered = hoveredTask === task.id;
                    const isNew = task.highlight;

                    return (
                      <g
                        key={task.id}
                        onMouseEnter={() => setHoveredTask(task.id)}
                        onMouseLeave={() => setHoveredTask(null)}
                        style={{ cursor: "pointer" }}
                      >
                        <rect
                          x={x} y={task.y} width={w} height={rowHeight - 4} rx={5}
                          fill={isHovered ? block.color + "44" : isNew ? block.color + "35" : block.color + "22"}
                          stroke={task.critical ? block.color : isNew ? block.color + "90" : block.color + "50"}
                          strokeWidth={task.critical ? 2.5 : isNew ? 2 : 1}
                        />
                        {task.critical && (
                          <rect x={x} y={task.y} width={4} height={rowHeight - 4} rx={2} fill={block.color} />
                        )}
                        {isNew && !task.critical && (
                          <rect x={x + w - 4} y={task.y} width={4} height={rowHeight - 4} rx={2} fill="#fbbf24" />
                        )}
                        <text x={x + 7} y={task.y + 14} fill="#f1f5f9" fontSize={10.5} fontWeight={600}>
                          {task.label.length > w / 7 ? task.label.slice(0, Math.floor(w / 7)) + "…" : task.label}
                        </text>
                        <text x={x + 7} y={task.y + 26} fill="#94a3b8" fontSize={8.5}>
                          {task.id}{task.depends ? ` \u2190 ${task.depends}` : ""}
                        </text>

                        {isHovered && (
                          <g>
                            <rect
                              x={Math.min(x, chartWidth - 380)} y={task.y - 36}
                              width={360} height={28} rx={5}
                              fill="#0f172aee" stroke={block.color + "80"} strokeWidth={1}
                            />
                            <text x={Math.min(x, chartWidth - 380) + 8} y={task.y - 18} fill="#e2e8f0" fontSize={10.5}>
                              {task.detail.length > 55 ? task.detail.slice(0, 55) + "…" : task.detail}
                            </text>
                          </g>
                        )}
                      </g>
                    );
                  })}
                </g>
              );
            })}

            {/* Dependency arrows */}
            {dependencies.map((dep, i) => {
              const from = getTaskPos(dep.from);
              const to = getTaskPos(dep.to);
              if (!from || !to) return null;

              const isNewDep = ["CC5", "CX4", "CC6", "AG4"].includes(dep.from) || ["CX4", "CC6", "AG4"].includes(dep.to);
              const dimmed = selectedAgent && !agents.some(
                (a) => a.name === selectedAgent && a.tasks.some((t) => t.id === dep.from || t.id === dep.to)
              );

              const x1 = labelWidth + from.end * unitWidth;
              const y1 = from.y + (rowHeight - 4) / 2;
              const x2 = labelWidth + to.start * unitWidth;
              const y2 = to.y + (rowHeight - 4) / 2;
              const midX = (x1 + x2) / 2;

              return (
                <g key={`dep-${i}`} opacity={dimmed ? 0.08 : isNewDep ? 0.8 : 0.5}>
                  <path
                    d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
                    fill="none"
                    stroke={isNewDep ? "#fbbf24" : "#f59e0b"}
                    strokeWidth={isNewDep ? 2 : 1.5}
                    strokeDasharray={isNewDep ? "6,3" : "4,3"}
                  />
                  <polygon
                    points={`${x2},${y2} ${x2 - 5},${y2 - 3} ${x2 - 5},${y2 + 3}`}
                    fill={isNewDep ? "#fbbf24" : "#f59e0b"}
                  />
                </g>
              );
            })}

            {/* Legend */}
            <g transform={`translate(10, ${totalHeight - 44})`}>
              <rect x={0} y={0} width={8} height={8} rx={2} fill="#f59e0b" />
              <text x={13} y={8} fill="#94a3b8" fontSize={9}>Dependency</text>

              <rect x={80} y={0} width={8} height={8} rx={2} fill="#fbbf24" />
              <text x={93} y={8} fill="#94a3b8" fontSize={9}>New (V1.1) dependency</text>

              <rect x={210} y={0} width={14} height={8} rx={2} fill="#10b98135" stroke="#10b981" strokeWidth={2.5} />
              <text x={229} y={8} fill="#94a3b8" fontSize={9}>Critical path</text>

              <rect x={310} y={0} width={14} height={8} rx={2} fill="#10b98135" />
              <rect x={320} y={0} width={4} height={8} rx={2} fill="#fbbf24" />
              <text x={329} y={8} fill="#94a3b8" fontSize={9}>New task (V1.1)</text>

              <text x={430} y={8} fill="#64748b" fontSize={9}>Hover for details · Click agent to filter</text>
            </g>
          </svg>
        </div>

        {/* Critical paths summary */}
        <div style={{ marginTop: 16, padding: 14, background: "#1e293b", borderRadius: 8, border: "1px solid #334155" }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: "#f8fafc", marginBottom: 10 }}>Two Critical Paths → Converge at AG-4</h3>
          
          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 11, color: "#94a3b8", marginBottom: 4, fontWeight: 600 }}>Path 1: Theory Tier</div>
            <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
              {[
                { label: "CX-1 Interfaces", color: "#3b82f6" },
                { label: "\u2192" },
                { label: "CC-1 Templates", color: "#10b981" },
                { label: "\u2192" },
                { label: "AG-1b Validate", color: "#ef4444" },
                { label: "\u2192" },
                { label: "CC-3 Cross-Ref", color: "#10b981" },
                { label: "\u2192" },
                { label: "AG-2 Workflow Test", color: "#ef4444" },
              ].map((item, i) =>
                item.color ? (
                  <span key={i} style={{ padding: "3px 8px", borderRadius: 4, background: item.color + "22", color: item.color, fontSize: 11, fontWeight: 600 }}>
                    {item.label}
                  </span>
                ) : (
                  <span key={i} style={{ color: "#475569", fontSize: 12 }}>{item.label}</span>
                )
              )}
            </div>
          </div>

          <div style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 11, color: "#fbbf24", marginBottom: 4, fontWeight: 600 }}>Path 2: Extraction Bridge (NEW in V1.1)</div>
            <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
              {[
                { label: "CC-5 Table Audit", color: "#10b981" },
                { label: "\u2192" },
                { label: "CX-4 Interface Spec", color: "#3b82f6" },
                { label: "\u2192" },
                { label: "CC-6 Implement Map", color: "#10b981" },
                { label: "\u2192" },
                { label: "AG-4 Round-Trip Test", color: "#ef4444" },
              ].map((item, i) =>
                item.color ? (
                  <span key={i} style={{ padding: "3px 8px", borderRadius: 4, background: item.color + "22", color: item.color, fontSize: 11, fontWeight: 600, border: `1px solid ${item.color}33` }}>
                    {item.label}
                  </span>
                ) : (
                  <span key={i} style={{ color: "#475569", fontSize: 12 }}>{item.label}</span>
                )
              )}
            </div>
          </div>

          <p style={{ color: "#94a3b8", fontSize: 11, marginTop: 6, lineHeight: 1.5 }}>
            <strong style={{ color: "#fbbf24" }}>AG-4 is the convergence point</strong> — the first test that the full system works: paper in → extraction → theory match → evaluation. 
            Both paths must complete before AG-4 can run. CC-5 (table audit) starts immediately with no dependencies.
          </p>
        </div>
      </div>
    </div>
  );
}
