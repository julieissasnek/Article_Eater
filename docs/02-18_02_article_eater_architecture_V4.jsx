import { useState } from "react";

const theories = [
  {
    id: "art", name: "Attention Restoration Theory", author: "Kaplan, 1989",
    color: "#2B8C5A", claim: "Natural environments restore depleted directed attention through fascination, being-away, extent, and compatibility.",
    templates: ["T041", "T031", "T044", "T033", "T061"],
    residual: "Four-property necessity claim; directed attention as specific depletable resource",
    overlaps: ["SRT (nature effects)", "PP (mechanism)", "Berlyne (complexity)"]
  },
  {
    id: "srt", name: "Stress Recovery Theory", author: "Ulrich, 1983",
    color: "#8C2B5A", claim: "Unthreatening natural environments trigger rapid pre-cognitive parasympathetic stress recovery.",
    templates: ["T041", "T042", "T025", "T038"],
    residual: "Pre-cognitive affective pathway (vs. ART's cognitive restoration)",
    overlaps: ["ART (nature effects)", "Biophilia (evolution)"]
  },
  {
    id: "bio", name: "Biophilia Hypothesis", author: "Wilson, 1984",
    color: "#5A8C2B", claim: "Innate, evolved human tendency to affiliate with life and life-like processes.",
    templates: ["T022", "T023", "T035", "T036", "T038", "T039"],
    residual: "Innateness claim — are preferences evolved or culturally learned?",
    overlaps: ["SRT (nature/safety)", "Fractal Fluency (patterns)"]
  },
  {
    id: "pp", name: "Predictive Processing", author: "Friston, 2010; Clark, 2013",
    color: "#5A2B8C", claim: "Brain minimizes prediction error; moderate-complexity environments optimize cognitive engagement.",
    templates: ["T022*", "T031*", "T028*", "T055*", "T058*"],
    residual: "Claim that ALL environmental effects reduce to prediction error dynamics",
    overlaps: ["All theories — offers alternative mechanism language"],
    note: "* PP provides mechanism re-descriptions, not unique templates"
  },
  {
    id: "berlyne", name: "Berlyne's Aesthetics", author: "Berlyne, 1971",
    color: "#8C5A2B", claim: "Aesthetic preference follows inverted-U of arousal potential (novelty, complexity, ambiguity).",
    templates: ["T031", "T044", "T029"],
    residual: "Arousal potential (vs. actual arousal) as mediator",
    overlaps: ["PP (complexity as PE)", "ART (fascination)"]
  },
  {
    id: "pr", name: "Prospect-Refuge Theory", author: "Appleton, 1975",
    color: "#2B5A8C", claim: "Humans prefer environments offering both open views (prospect) and enclosure (refuge).",
    templates: ["T025", "T025a", "T025b", "T025c"],
    residual: "Evolutionary vs. learned origin of spatial safety preferences",
    overlaps: ["SRT (safety)", "Biophilia (evolution)"]
  },
  {
    id: "ec", name: "Embodied Cognition", author: "Lakoff & Johnson, 1980",
    color: "#8C2B2B", claim: "Abstract thought is grounded in bodily/spatial metaphor: UP=FREE, OPEN=POSSIBLE, CONSTRAINED=LIMITED.",
    templates: ["T007", "T009", "T033", "T035"],
    residual: "Generative claim that novel metaphors can create new environment-cognition pathways",
    overlaps: ["Construal Level Theory"]
  },
  {
    id: "tc", name: "Thermal Comfort", author: "Fanger, 1970; de Dear, 2002",
    color: "#2B8C8C", claim: "Thermal comfort follows PMV-PPD model (Fanger) or adaptive model (de Dear).",
    templates: ["T027", "T028", "T028b"],
    residual: "Fixed physiology (Fanger) vs. adaptive psychology (de Dear)",
    overlaps: ["PP (thermal prediction error)"]
  },
  {
    id: "cp", name: "Circadian Photobiology", author: "Czeisler et al., 1999",
    color: "#4B8C2B", claim: "Light spectrum and timing regulate circadian rhythms, arousal, and cognitive performance.",
    templates: ["T014", "T015", "T016"],
    residual: "Individual genetic variation in melanopsin/clock gene photosensitivity",
    overlaps: ["Arousal Theory"]
  },
  {
    id: "msi", name: "Multisensory Integration", author: "Stein & Meredith, 1993",
    color: "#8C4B8C", claim: "Cross-modal signals are combined according to reliability-weighted Bayesian rules.",
    templates: ["T050", "T051", "T052"],
    residual: "Precise computational rules of optimal cue combination",
    overlaps: ["PP (Bayesian inference)"]
  },
];

const templateDB = {
  T007: { name: "Ceiling Height → Cognitive Scope", mech: "Spatial freedom schema → abstract processing", effect: "d = 0.30–0.55" },
  T009: { name: "Corridor Width → Social Comfort", mech: "Personal space schema", effect: "d = 0.20–0.40" },
  T014: { name: "Natural Light → Alertness", mech: "ipRGC → SCN → cortisol → attention", effect: "d = 0.35–0.65" },
  T015: { name: "Light CCT → Arousal", mech: "Spectral composition → arousal state", effect: "d = 0.20–0.45" },
  T016: { name: "Light Timing → Circadian Phase", mech: "Temporal light pattern → phase shifting", effect: "d = 0.30–0.55" },
  T022: { name: "Wood → Stress Reduction", mech: "1/f pattern → processing fluency → parasympathetic", effect: "d = 0.25–0.50 (inverted-U)" },
  T023: { name: "Stone → Groundedness", mech: "Material permanence → stability affect", effect: "d = 0.15–0.30" },
  T025: { name: "Prospect-Refuge → Comfort", mech: "View + enclosure → safety evaluation", effect: "d = 0.30–0.55" },
  "T025a": { name: "Prospect → Sense of Control", mech: "Visual openness → surveillance affordance", effect: "d = 0.20–0.40" },
  "T025b": { name: "Refuge → Security", mech: "Enclosure → protection signal", effect: "d = 0.25–0.45" },
  "T025c": { name: "P+R Conjunction > Either Alone", mech: "Combined > sum", effect: "interaction effect" },
  T027: { name: "Temperature → Comfort", mech: "Thermoregulatory homeostasis", effect: "strong (PMV-PPD)" },
  T028: { name: "Thermal Deviation → Cognitive Decrement", mech: "Thermal PE → resource diversion", effect: "d = 0.30–0.60" },
  "T028b": { name: "Thermal Control → Tolerance", mech: "Perceived control → adaptive comfort", effect: "d = 0.20–0.35" },
  T029: { name: "Ambient Stimulation → Arousal", mech: "Yerkes-Dodson (inverted-U)", effect: "d = 0.25–0.50" },
  T031: { name: "Visual Complexity → Engagement", mech: "Collative variables → arousal/preference", effect: "inverted-U" },
  T033: { name: "Spatial Depth → Exploratory Affordance", mech: "Deep vista → exploration invitation", effect: "d = 0.20–0.40" },
  T035: { name: "Curved Geometry → Preference", mech: "Non-angular = non-threatening", effect: "d = 0.25–0.45" },
  T036: { name: "Biomorphic Patterns → Comfort", mech: "Life-like form → fascination + ease", effect: "d = 0.20–0.40" },
  T038: { name: "Indoor Plants → Stress + Air Quality", mech: "Green → nature association", effect: "d = 0.25–0.50" },
  T039: { name: "Water Features → Auditory Masking + Affect", mech: "Water sound → masking + calm", effect: "d = 0.30–0.55" },
  T041: { name: "Nature View → Restoration", mech: "Soft fascination + safety signal", effect: "d = 0.40–0.70" },
  T042: { name: "Water Presence → Restorative Benefit", mech: "Evolved water-seeking → positive affect", effect: "d = 0.25–0.50" },
  T044: { name: "Novelty → Psychological Detachment", mech: "Schema disruption → routine-thought suppression", effect: "d = 0.20–0.40" },
  T050: { name: "Cross-modal Congruence → Coherence", mech: "Matched signals → environmental unity", effect: "d = 0.20–0.45" },
  T051: { name: "Audiovisual Mismatch → Unease", mech: "Cross-modal PE", effect: "d = 0.25–0.50" },
  T052: { name: "Weak Signal → Enhanced Integration", mech: "Inverse effectiveness principle", effect: "varies" },
  T055: { name: "Acoustic Level → Distraction", mech: "Auditory PE → attentional capture", effect: "d = 0.40–0.70" },
  T058: { name: "Olfactory Incongruence → Unease", mech: "Smell-context mismatch PE", effect: "d = 0.15–0.35" },
  T061: { name: "Task-Environment Fit → Efficiency", mech: "Affordance match → reduced overhead", effect: "d = 0.30–0.55" },
};

// PP mechanism templates
["T022*","T031*","T028*","T055*","T058*"].forEach(k => {
  const base = k.replace("*","");
  if (templateDB[base]) templateDB[k] = { ...templateDB[base], name: templateDB[base].name + " (PP mechanism)", mech: "PP re-description: prediction error account" };
});

export default function ArticleEaterDiagram() {
  const [view, setView] = useState("architecture");
  const [selectedTheory, setSelectedTheory] = useState(null);
  const [selectedComp, setSelectedComp] = useState(null);

  const components = {
    extraction: { title: "Extraction Engine", color: "#2B5A8C", desc: "386 papers → ~2,000 claims via abstracts, captions, tables" },
    resolution: { title: "Variable Resolution", color: "#3B7A4C", desc: "Maps heterogeneous vocab → canonical template variables (200+ synonyms)" },
    web: { title: "Web of Belief", color: "#8C4B2B", desc: "Coherentist knowledge graph: what should we believe? (Quine & Ullian)" },
    bayesian: { title: "Bayesian Network", color: "#6B3B8C", desc: "Foundationalist causal inference: what should we predict? (from templates)" },
    prediction: { title: "Prediction & Reporting", color: "#8C6B2B", desc: "Design recommendations with uncertainty, trade-offs, and provenance" },
  };

  const theory = selectedTheory ? theories.find(t => t.id === selectedTheory) : null;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4 font-sans">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-center mb-1 text-blue-300">The Article Eater</h1>
        <p className="text-center text-gray-500 text-xs mb-4">Compositional Mechanistic Reasoning for Evidence-Based Architectural Design</p>

        {/* Tab navigation */}
        <div className="flex gap-2 mb-4 justify-center">
          {[
            ["architecture", "System Architecture"],
            ["theories", "Theories → Templates"],
            ["template", "What Is a Template?"],
          ].map(([id, label]) => (
            <button key={id} onClick={() => { setView(id); setSelectedTheory(null); setSelectedComp(null); }}
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${view === id ? "bg-blue-700 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}>
              {label}
            </button>
          ))}
        </div>

        {/* ───── ARCHITECTURE VIEW ───── */}
        {view === "architecture" && (
          <div>
            <div className="grid grid-cols-5 gap-2 mb-4">
              {Object.entries(components).map(([key, c]) => (
                <button key={key} onClick={() => setSelectedComp(selectedComp === key ? null : key)}
                  className={`rounded-xl p-3 text-center transition-all border ${selectedComp === key ? "border-white bg-opacity-30" : "border-gray-700 bg-opacity-15 hover:bg-opacity-20"}`}
                  style={{ backgroundColor: c.color + (selectedComp === key ? "55" : "22") }}>
                  <div className="text-xs font-bold text-white">{c.title}</div>
                </button>
              ))}
            </div>
            {/* Flow arrows */}
            <div className="flex items-center justify-center gap-0 mb-4 text-gray-600 text-xs">
              <span>Papers</span>
              {["→ Extract →", "→ Resolve →", "→ Believe →", "→ Infer →", "→ Predict"].map((a,i) => (
                <span key={i} className="text-gray-600">{a}</span>
              ))}
            </div>
            {selectedComp && (
              <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 mb-4" style={{ borderLeftColor: components[selectedComp].color, borderLeftWidth: 4 }}>
                <h3 className="font-bold text-lg" style={{ color: components[selectedComp].color }}>{components[selectedComp].title}</h3>
                <p className="text-gray-300 text-sm mt-1">{components[selectedComp].desc}</p>
              </div>
            )}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <p className="text-gray-400 text-sm leading-relaxed">
                <span className="text-yellow-300 font-bold">Key insight:</span> The system has two epistemological structures. 
                The <span className="text-orange-300 font-bold">Web of Belief</span> (coherentist) manages <em>what we should believe</em> — credences, consensus, disagreement. 
                The <span className="text-purple-300 font-bold">Bayesian Network</span> (foundationalist) computes <em>what we should predict</em> — causal inference from environmental variables to human outcomes. 
                The Web determines which templates enter the BN and with what confidence.
              </p>
            </div>
          </div>
        )}

        {/* ───── THEORIES VIEW ───── */}
        {view === "theories" && (
          <div>
            <div className="bg-gray-900 border border-yellow-800 rounded-xl p-3 mb-4">
              <p className="text-yellow-200 text-sm">
                <span className="font-bold">The theory-to-template reduction is itself a scholarly contribution.</span> It maps exactly what each theory claims at the mechanistic level, where theories overlap, and what each claims that no template captures (the <em>irreducible residual</em>). Click any theory to see its decomposition.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-4">
              {theories.map(t => (
                <button key={t.id} onClick={() => setSelectedTheory(selectedTheory === t.id ? null : t.id)}
                  className={`rounded-xl p-3 text-left transition-all border ${selectedTheory === t.id ? "border-white" : "border-gray-700 hover:border-gray-500"}`}
                  style={{ backgroundColor: t.color + (selectedTheory === t.id ? "44" : "18") }}>
                  <div className="text-sm font-bold text-white">{t.name}</div>
                  <div className="text-xs text-gray-400">{t.author}</div>
                  <div className="text-xs text-gray-500 mt-1">{t.templates.length} templates</div>
                </button>
              ))}
            </div>

            {theory && (
              <div className="bg-gray-900 border rounded-xl p-5 mb-4" style={{ borderColor: theory.color }}>
                <h3 className="text-lg font-bold mb-2" style={{ color: theory.color }}>{theory.name}</h3>
                <p className="text-gray-300 text-sm mb-3">{theory.claim}</p>

                <div className="mb-3">
                  <div className="text-xs font-bold text-gray-500 uppercase mb-1">Templates Generated</div>
                  <div className="grid gap-1">
                    {theory.templates.map(tid => {
                      const t = templateDB[tid];
                      return t ? (
                        <div key={tid} className="bg-gray-800 rounded-lg px-3 py-2 flex gap-3 items-start">
                          <span className="text-blue-300 font-mono text-xs font-bold min-w-12">{tid}</span>
                          <div>
                            <div className="text-gray-200 text-xs font-bold">{t.name}</div>
                            <div className="text-gray-500 text-xs">{t.mech} · {t.effect}</div>
                          </div>
                        </div>
                      ) : null;
                    })}
                  </div>
                </div>

                <div className="mb-3">
                  <div className="text-xs font-bold text-gray-500 uppercase mb-1">Overlaps With</div>
                  <div className="text-gray-400 text-xs">{theory.overlaps.join(" · ")}</div>
                </div>

                <div className="bg-red-950 border border-red-800 rounded-lg p-3">
                  <div className="text-xs font-bold text-red-400 uppercase mb-1">Irreducible Residual — what no template captures</div>
                  <div className="text-gray-300 text-sm">{theory.residual}</div>
                </div>

                {theory.note && (
                  <div className="text-gray-500 text-xs mt-2 italic">{theory.note}</div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ───── TEMPLATE VIEW ───── */}
        {view === "template" && (
          <div>
            <div className="bg-gray-900 border border-blue-800 rounded-xl p-5 mb-4">
              <h3 className="text-lg font-bold text-blue-300 mb-3">What Is a Template?</h3>
              <p className="text-gray-300 text-sm leading-relaxed mb-4">
                A template is a <strong className="text-white">parameterized causal schema</strong> connecting an environmental feature to a human outcome through a named mechanism, with quantified effect size, explicit boundary conditions, and documented evidence. It is the atom of the system's reasoning — everything else (Web of Belief, Bayesian Network, prediction engine) operates over templates and their compositions.
              </p>

              <h4 className="text-sm font-bold text-blue-200 mb-2">Example: T014 — Natural Light → Circadian Alertness</h4>
              <div className="space-y-1">
                {[
                  ["What changes in the environment?", "Natural light (lux, spectral composition, timing relative to circadian phase)"],
                  ["What changes in the person?", "Sustained attention accuracy (PVT reaction time, vigilance errors)"],
                  ["By what causal mechanism?", "Blue light (460–480nm) → melanopsin receptors → SCN phase-setting → cortisol response → norepinephrine arousal → dorsal attention network → sustained vigilance"],
                  ["How big is the effect?", "d = 0.35–0.65; positive linear 100–2000 lux; ceiling above 2000 lux"],
                  ["When does it NOT apply?", "Exposure < 30 min; screen-dominated work; shift workers; evening chronotypes show weaker effects"],
                  ["What modifies it?", "Chronotype, time of day, season, age, prior sleep duration"],
                  ["What interacts?", "Synergistic with nature views; antagonistic with glare/thermal discomfort; conditional on noise"],
                  ["Evidence?", "Boubekri (2014) d=0.52, N=49; Viola (2008) d=0.58, N=104; Phipps-Nelson (2003) d=0.63, N=16"],
                  ["Source theory?", "Circadian Photobiology + Arousal Theory; consistent with Predictive Processing"],
                ].map(([label, value]) => (
                  <div key={label} className="flex gap-2 bg-gray-800 rounded px-3 py-2">
                    <span className="text-gray-400 font-bold text-xs min-w-48 shrink-0">{label}</span>
                    <span className="text-gray-200 text-xs">{value}</span>
                  </div>
                ))}
              </div>

              <div className="mt-4 bg-gray-800 rounded-lg p-3">
                <p className="text-gray-400 text-xs leading-relaxed">
                  <span className="text-yellow-300 font-bold">Why mechanism chains matter:</span> Because every step is named, the system can detect when two templates share an intermediate node (e.g., both affect norepinephrine arousal). Shared nodes mean the templates interact — their combined effect must be modeled, not assumed additive.
                </p>
              </div>
            </div>

            <div className="bg-gray-900 border border-gray-700 rounded-xl p-5">
              <h4 className="text-sm font-bold text-gray-300 mb-3">The system contains ~60 templates spanning:</h4>
              <div className="grid grid-cols-2 gap-2">
                {[
                  ["Light", "T014, T015, T016", "#4B8C2B"],
                  ["Sound", "T055, T051, T029", "#8C5A2B"],
                  ["Temperature", "T027, T028, T028b", "#2B8C8C"],
                  ["Materials", "T022, T023", "#5A8C2B"],
                  ["Geometry", "T007, T009, T035", "#8C2B2B"],
                  ["Nature/Views", "T041, T042, T038, T039", "#2B8C5A"],
                  ["Spatial Layout", "T025, T033, T061", "#2B5A8C"],
                  ["Multisensory", "T050, T051, T052", "#8C4B8C"],
                ].map(([domain, templates, color]) => (
                  <div key={domain} className="bg-gray-800 rounded-lg p-2 border-l-2" style={{ borderLeftColor: color }}>
                    <div className="text-xs font-bold" style={{ color }}>{domain}</div>
                    <div className="text-xs text-gray-500">{templates}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
