"""
Prose Revision Service — Active diagnostic and revision tool for ATLAS prose.

Implements the three-pass revision protocol from SCIENCE_COMMUNICATION_NORMS.md:
  Pass 1: Structural (Doumont) — headings, argument flow, first/last sentence coherence
  Pass 2: Sentence-level (Lanham + Williams) — nominalizations, passive voice, Given-New
  Pass 3: Knowledge-curse audit (Pinker) — undefined terms, implicit assumptions, calibration

Also implements:
  - Sword's Writer's Diet diagnostic (5-category word health)
  - Lanham's Paramedic Method (lard factor computation)
  - Quantitative prose health metrics

Usage:
    from src.services.prose_revision_service import ProseRevisionService

    service = ProseRevisionService()

    # Full 3-pass critique
    report = service.full_critique(text, context="master_doc_section")

    # Individual diagnostics
    diet = service.writers_diet(text)
    lard = service.lard_factor(text)
    noms = service.find_nominalizations(text)
    passives = service.find_passive_voice(text)
    hedges = service.find_hedge_stacks(text)

    # Structural analysis
    structure = service.structural_audit(text)

    # Generate revision suggestions
    suggestions = service.suggest_revisions(text, max_suggestions=10)
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ── Diagnostic severity ──────────────────────────────────────────────────────

class Severity(Enum):
    """How serious is this prose issue?"""
    INFO = "info"           # Stylistic note, not a problem
    ADVISORY = "advisory"   # Could be better; revise if time permits
    WARNING = "warning"     # Likely hurts readability; should revise
    CRITICAL = "critical"   # Definitely hurts readability; must revise


class DiagnosticCategory(Enum):
    """Which norm does this diagnostic relate to?"""
    NOMINALIZATION = "zombie_nouns"          # Norm 4 (Lanham/Sword)
    PASSIVE_VOICE = "passive_voice"         # Writing Style Guide §1.3
    HEDGE_STACK = "hedge_stacks"            # Writing Style Guide §8.1
    THROAT_CLEARING = "throat_clearing"     # Norm 1 (Pinker) — meta-commentary
    SENTENCE_LENGTH = "sentence_length"     # Cognitive load
    GIVEN_NEW = "given_new_violation"       # Norm 2 (Williams)
    STRESS_POSITION = "stress_position"     # Norm 3 (Williams)
    CONFIDENCE_CALIBRATION = "confidence"   # Norm 9 (Carson/Sagan)
    JARGON = "undefined_jargon"            # Norm 6 (Pinker)
    STRUCTURE = "structure"                 # Norm 11 (Doumont)
    CITATION_STYLE = "citation_style"      # Writing Style Guide §4.4
    LARD_FACTOR = "lard_factor"            # Norm 5 (Lanham)


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class Diagnostic:
    """A single prose diagnostic finding."""
    category: DiagnosticCategory
    severity: Severity
    message: str
    location: str = ""         # e.g., "paragraph 3, sentence 2" or "line 45"
    original: str = ""         # the offending text
    suggestion: str = ""       # how to fix it
    norm_reference: str = ""   # which norm this violates


@dataclass
class WritersDiet:
    """Sword's Writer's Diet — 5-category prose health diagnostic."""
    be_verb_pct: float = 0.0         # "is", "was", "are", "were", "been", "being"
    abstract_noun_pct: float = 0.0   # nominalizations (-tion, -ment, -ness, -ity, etc.)
    preposition_pct: float = 0.0     # "of", "in", "by", "for", "with", etc.
    adjadv_pct: float = 0.0          # adjectives and adverbs (rough heuristic)
    it_this_there_pct: float = 0.0   # weak sentence openers
    total_words: int = 0
    verdict: str = ""                # "Lean", "Fit & Trim", "Needs Toning", "Flabby", "Heart Attack"

    def as_dict(self) -> dict:
        return {
            "be_verb_pct": round(self.be_verb_pct, 1),
            "abstract_noun_pct": round(self.abstract_noun_pct, 1),
            "preposition_pct": round(self.preposition_pct, 1),
            "adjadv_pct": round(self.adjadv_pct, 1),
            "it_this_there_pct": round(self.it_this_there_pct, 1),
            "total_words": self.total_words,
            "verdict": self.verdict,
        }


@dataclass
class ProseHealthReport:
    """Full prose health report from 3-pass critique."""
    # Quantitative metrics
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    max_sentence_length: int = 0
    paragraph_count: int = 0
    avg_paragraph_length: float = 0.0
    nominalization_density: float = 0.0    # per 100 words
    passive_voice_pct: float = 0.0
    lard_factor_estimate: float = 0.0      # 0-100%
    writers_diet: Optional[WritersDiet] = None

    # Diagnostics by pass
    pass1_structural: list = field(default_factory=list)     # Doumont
    pass2_sentence: list = field(default_factory=list)       # Lanham + Williams
    pass3_knowledge: list = field(default_factory=list)      # Pinker

    # Overall
    overall_score: float = 0.0    # 0-10
    verdict: str = ""
    summary: str = ""

    @property
    def all_diagnostics(self) -> list:
        return self.pass1_structural + self.pass2_sentence + self.pass3_knowledge

    @property
    def critical_count(self) -> int:
        return sum(1 for d in self.all_diagnostics if d.severity == Severity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for d in self.all_diagnostics if d.severity == Severity.WARNING)


# ── Constants ────────────────────────────────────────────────────────────────

BE_VERBS = {
    "is", "am", "are", "was", "were", "be", "been", "being",
    "isn't", "aren't", "wasn't", "weren't",
}

PREPOSITIONS = {
    "of", "in", "to", "for", "with", "on", "at", "from", "by", "about",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "along", "until", "upon", "toward", "towards",
    "within", "without", "among", "across", "against", "behind", "beyond",
}

# Suffixes that signal nominalizations (zombie nouns)
NOMINALIZATION_SUFFIXES = (
    "tion", "sion", "ment", "ness", "ity", "ence", "ance",
    "ism", "ure", "ology", "ysis",
)

# Common exceptions — these are legitimate nouns, not buried verbs
NOMINALIZATION_EXCEPTIONS = {
    "information", "question", "situation", "position", "condition",
    "attention", "mention", "nation", "station", "fashion", "section",
    "function", "emotion", "notion", "motion", "portion", "caution",
    "location", "relation", "solution", "education", "population",
    "generation", "institution", "environment", "management",
    "department", "government", "development", "assessment",
    "measurement", "experiment", "element", "document", "moment",
    "comment", "basement", "apartment", "statement", "treatment",
    "argument", "movement", "agreement", "arrangement",
    "consciousness", "awareness", "darkness", "illness", "business",
    "happiness", "fitness", "wilderness", "witness",
    "community", "university", "opportunity", "quality", "ability",
    "activity", "reality", "identity", "personality", "diversity",
    "electricity", "complexity", "city", "society", "anxiety",
    "experience", "difference", "science", "evidence", "sentence",
    "audience", "presence", "absence", "silence", "sequence",
    "conference", "reference", "preference", "influence",
    "performance", "distance", "substance", "insurance", "instance",
    "importance", "resistance", "tolerance", "guidance", "balance",
    "cognition", "perception", "prediction", "architecture",
    "neuroscience", "psychology",
}

# Throat-clearing phrases (Pinker: classic style violations)
THROAT_CLEARERS = [
    r"\bit is important to note that\b",
    r"\bit should be noted that\b",
    r"\bit is worth pointing out that\b",
    r"\bit is interesting to note that\b",
    r"\bit can be observed that\b",
    r"\bit has been suggested that\b",
    r"\bit is well known that\b",
    r"\bit is generally accepted that\b",
    r"\bin this section,? we will\b",
    r"\bin this paper,? we\b",
    r"\bas noted above\b",
    r"\bas mentioned earlier\b",
    r"\bas previously discussed\b",
    r"\bthe fact that\b",
    r"\bthe purpose of this\b",
    r"\bthe author would like to\b",
    r"\bwe would like to argue\b",
    r"\bneedless to say\b",
    r"\bit goes without saying\b",
]

# Hedge stacks — multiple hedges in sequence
HEDGE_WORDS = [
    r"\bmight\b", r"\bperhaps\b", r"\bsomewhat\b", r"\bpossibly\b",
    r"\bcould potentially\b", r"\bmay perhaps\b", r"\btends to\b",
    r"\bappears to\b", r"\bseems to\b", r"\bit is possible that\b",
    r"\bto some extent\b", r"\bin some cases\b", r"\brelatively\b",
]

# Overclaiming words (Norm 9 — Carson/Sagan)
OVERCLAIM_WORDS = [
    r"\bclearly\b", r"\bobviously\b", r"\bundoubtedly\b",
    r"\bunambiguously\b", r"\bwithout question\b", r"\bdefinitively\b",
    r"\bproves that\b", r"\bdemonstrates conclusively\b",
    r"\binterestingly\b", r"\bremarkably\b", r"\bstrikingly\b",
]

# Weak openers
WEAK_OPENERS = [
    r"^it is\b", r"^it was\b", r"^there is\b", r"^there are\b",
    r"^there was\b", r"^there were\b", r"^this is\b",
]


# ── The Service ──────────────────────────────────────────────────────────────

class ProseRevisionService:
    """
    Active diagnostic and revision tool for ATLAS prose.

    Implements the norms from SCIENCE_COMMUNICATION_NORMS.md as executable
    checks that can critique existing prose and suggest revisions.
    """

    def __init__(self, context: str = "general"):
        """
        Args:
            context: One of "master_doc", "paper", "qa_response", "general".
                     Adjusts thresholds and severity levels.
        """
        self.context = context
        self._thresholds = self._get_thresholds(context)

    def _get_thresholds(self, context: str) -> dict:
        """Context-sensitive thresholds for diagnostics."""
        base = {
            "max_sentence_length": 45,
            "target_avg_sentence_length": 22,
            "max_paragraph_sentences": 8,
            "nominalization_warning": 4.0,     # per 100 words
            "nominalization_critical": 7.0,
            "passive_voice_warning": 20.0,     # percent
            "passive_voice_critical": 35.0,
            "hedge_stack_threshold": 2,        # hedges per sentence
            "lard_factor_warning": 35.0,       # percent
            "lard_factor_critical": 50.0,
        }
        if context == "qa_response":
            base["max_sentence_length"] = 35
            base["target_avg_sentence_length"] = 18
            base["max_paragraph_sentences"] = 5
        elif context == "paper":
            base["max_sentence_length"] = 50
            base["max_paragraph_sentences"] = 10
        return base

    # ── Tokenization helpers ─────────────────────────────────────────────

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences. Handles common abbreviations."""
        # Remove markdown headers, links, code blocks
        clean = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
        clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
        clean = re.sub(r"`[^`]+`", "CODE", clean)
        clean = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", clean)

        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"])', clean)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs."""
        paras = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paras if p.strip() and len(p.strip()) > 20]

    def _tokenize(self, text: str) -> list[str]:
        """Simple word tokenization."""
        return re.findall(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b", text.lower())

    def _extract_headings(self, text: str) -> list[tuple[int, str]]:
        """Extract markdown headings with their level."""
        return [(len(m.group(1)), m.group(2).strip())
                for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)]

    # ── Pass 1: Structural Audit (Doumont) ───────────────────────────────

    def structural_audit(self, text: str) -> list[Diagnostic]:
        """
        Pass 1: Structural revision (Doumont).

        Checks:
        - Headings: informative vs. topic-only
        - First/last sentence coherence
        - Paragraph length
        - Section flow
        """
        diagnostics = []
        headings = self._extract_headings(text)
        paragraphs = self._split_paragraphs(text)

        # Check headings
        topic_only_patterns = [
            r"^(Introduction|Background|Methods|Results|Discussion|"
            r"Conclusion|Overview|Summary|Analysis|Approach|"
            r"Related Work|Literature Review|Future Work|"
            r"Methodology|Implementation|Evaluation)$",
        ]
        for level, heading in headings:
            for pat in topic_only_patterns:
                if re.match(pat, heading, re.IGNORECASE):
                    diagnostics.append(Diagnostic(
                        category=DiagnosticCategory.STRUCTURE,
                        severity=Severity.WARNING,
                        message=f"Topic-only heading: '{heading}'. Headings should state the section's claim, not just its topic.",
                        original=heading,
                        suggestion=f"Replace '{heading}' with a sentence that states what the section concludes.",
                        norm_reference="Norm 11 (Doumont): Structure as Communication; WRITING_STYLE_GUIDE §3.3",
                    ))
                    break

        # Check paragraph lengths
        for i, para in enumerate(paragraphs):
            sentences = self._split_sentences(para)
            if len(sentences) > self._thresholds["max_paragraph_sentences"]:
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.STRUCTURE,
                    severity=Severity.WARNING,
                    message=f"Paragraph {i+1} has {len(sentences)} sentences (max recommended: {self._thresholds['max_paragraph_sentences']}). A paragraph is a unit of argument — it should contain exactly one move.",
                    location=f"paragraph {i+1}",
                    norm_reference="WRITING_STYLE_GUIDE §2.2; Norm 5 (Mayer): Cognitive Load",
                ))
            elif len(sentences) <= 1 and len(para) > 50:
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.STRUCTURE,
                    severity=Severity.INFO,
                    message=f"Paragraph {i+1} is a single sentence. This can be effective for emphasis but should be used sparingly.",
                    location=f"paragraph {i+1}",
                    norm_reference="WRITING_STYLE_GUIDE §2.2",
                ))

        # Check for missing section openers (first sentence should orient)
        # This is a heuristic: if the first sentence of a paragraph right after a heading
        # doesn't reference the heading's topic, it may lack orientation.
        # (Full implementation would need NLP; this checks for basic patterns)

        return diagnostics

    # ── Pass 2: Sentence-Level (Lanham + Williams) ───────────────────────

    def find_nominalizations(self, text: str) -> list[Diagnostic]:
        """
        Norm 4: Kill the Zombie Nouns (Lanham/Sword).

        Identifies nominalizations — abstract nouns derived from verbs —
        and suggests restoring the buried verb.
        """
        diagnostics = []
        words = self._tokenize(text)
        sentences = self._split_sentences(text)

        nominalization_count = 0
        for word in words:
            if (len(word) > 6 and
                word.endswith(NOMINALIZATION_SUFFIXES) and
                word not in NOMINALIZATION_EXCEPTIONS):
                nominalization_count += 1

        # Compute density
        if words:
            density = (nominalization_count / len(words)) * 100
        else:
            density = 0.0

        if density >= self._thresholds["nominalization_critical"]:
            sev = Severity.CRITICAL
        elif density >= self._thresholds["nominalization_warning"]:
            sev = Severity.WARNING
        else:
            sev = Severity.INFO

        if density >= self._thresholds["nominalization_warning"]:
            diagnostics.append(Diagnostic(
                category=DiagnosticCategory.NOMINALIZATION,
                severity=sev,
                message=f"Nominalization density: {density:.1f} per 100 words ({nominalization_count} total). Target: <{self._thresholds['nominalization_warning']:.0f}/100.",
                suggestion="Scan for -tion, -ment, -ness, -ity suffixes. For each, ask: can this be restored to its verb form? 'The optimization of' → 'optimizing'; 'the implementation of' → 'implementing'.",
                norm_reference="Norm 4 (Lanham/Sword): Kill the Zombie Nouns",
            ))

        # Find specific high-density sentences
        for i, sent in enumerate(sentences):
            sent_words = self._tokenize(sent)
            sent_noms = [w for w in sent_words
                        if len(w) > 6
                        and w.endswith(NOMINALIZATION_SUFFIXES)
                        and w not in NOMINALIZATION_EXCEPTIONS]
            if len(sent_noms) >= 3:
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.NOMINALIZATION,
                    severity=Severity.WARNING,
                    message=f"Sentence has {len(sent_noms)} nominalizations: {', '.join(sent_noms)}",
                    location=f"sentence {i+1}",
                    original=sent[:120] + ("..." if len(sent) > 120 else ""),
                    suggestion="Apply Lanham's Paramedic Method: find the action, put it in an active verb, put the agent in the subject.",
                    norm_reference="Norm 5 (Lanham): Paramedic Method",
                ))

        return diagnostics

    def find_passive_voice(self, text: str) -> list[Diagnostic]:
        """
        WRITING_STYLE_GUIDE §1.3: Active Voice.

        Identifies passive constructions (was/were/is/are + past participle).
        """
        diagnostics = []
        sentences = self._split_sentences(text)

        passive_pattern = re.compile(
            r"\b(is|are|was|were|be|been|being)\s+"
            r"(being\s+)?"
            r"(\w+(?:ed|en|nt|wn|ck|lt|pt|ft|ght))\b",
            re.IGNORECASE,
        )

        passive_count = 0
        for i, sent in enumerate(sentences):
            matches = passive_pattern.findall(sent)
            if matches:
                passive_count += 1

        if sentences:
            pct = (passive_count / len(sentences)) * 100
        else:
            pct = 0.0

        if pct >= self._thresholds["passive_voice_critical"]:
            sev = Severity.CRITICAL
        elif pct >= self._thresholds["passive_voice_warning"]:
            sev = Severity.WARNING
        else:
            sev = Severity.INFO

        if pct >= self._thresholds["passive_voice_warning"]:
            diagnostics.append(Diagnostic(
                category=DiagnosticCategory.PASSIVE_VOICE,
                severity=sev,
                message=f"Passive voice in {pct:.0f}% of sentences ({passive_count}/{len(sentences)}). Target: <{self._thresholds['passive_voice_warning']:.0f}%.",
                suggestion="For each passive sentence, ask: who is doing the action? Make them the subject. 'The effect was measured by...' → 'We measured the effect...'",
                norm_reference="WRITING_STYLE_GUIDE §1.3; Norm 4 (Lanham): restore the agent",
            ))

        return diagnostics

    def find_hedge_stacks(self, text: str) -> list[Diagnostic]:
        """
        WRITING_STYLE_GUIDE §8.1: Hedge stacking.

        Finds sentences with multiple hedging words.
        """
        diagnostics = []
        sentences = self._split_sentences(text)

        for i, sent in enumerate(sentences):
            hedge_count = sum(1 for h in HEDGE_WORDS if re.search(h, sent, re.IGNORECASE))
            if hedge_count >= self._thresholds["hedge_stack_threshold"]:
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.HEDGE_STACK,
                    severity=Severity.WARNING,
                    message=f"Sentence has {hedge_count} hedging words. Pick one hedge or none.",
                    location=f"sentence {i+1}",
                    original=sent[:120] + ("..." if len(sent) > 120 else ""),
                    suggestion="Choose the single most appropriate qualifier. If the evidence warrants hedging, one hedge is enough. If it doesn't, remove all hedges.",
                    norm_reference="WRITING_STYLE_GUIDE §8.1; Norm 9 (Carson/Sagan): Honest Uncertainty",
                ))

        return diagnostics

    def find_throat_clearing(self, text: str) -> list[Diagnostic]:
        """
        Norm 1 (Pinker): Classic Style violations.

        Finds meta-commentary, self-referential phrases, and slow windups.
        """
        diagnostics = []
        for pattern in THROAT_CLEARERS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.THROAT_CLEARING,
                    severity=Severity.WARNING,
                    message=f"Throat-clearing phrase: '{m.group()}'",
                    original=m.group(),
                    suggestion="Delete the phrase and start with the actual content. If you're noting something, just note it. If you're arguing, just argue.",
                    norm_reference="Norm 1 (Pinker): Classic Style — the writer as guide, not commentator",
                ))
        return diagnostics

    def find_overclaiming(self, text: str) -> list[Diagnostic]:
        """
        Norm 9 (Carson/Sagan): Honest Uncertainty.

        Finds overclaiming language that doesn't match evidence level.
        """
        diagnostics = []
        for pattern in OVERCLAIM_WORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.CONFIDENCE_CALIBRATION,
                    severity=Severity.WARNING,
                    message=f"Overclaiming word: '{m.group()}'. If the evidence truly warrants this, the reader doesn't need to be told. If it doesn't, remove the word.",
                    original=m.group(),
                    suggestion="Replace with evidence-calibrated language. See the confidence spectrum in SCIENCE_COMMUNICATION_NORMS.md Norm 9.",
                    norm_reference="Norm 9 (Carson/Sagan): Honest Uncertainty; WRITING_STYLE_GUIDE §6.1",
                ))
        return diagnostics

    def find_long_sentences(self, text: str) -> list[Diagnostic]:
        """Check sentence length distribution."""
        diagnostics = []
        sentences = self._split_sentences(text)

        for i, sent in enumerate(sentences):
            word_count = len(self._tokenize(sent))
            if word_count > self._thresholds["max_sentence_length"]:
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.SENTENCE_LENGTH,
                    severity=Severity.WARNING if word_count < 60 else Severity.CRITICAL,
                    message=f"Sentence has {word_count} words (max recommended: {self._thresholds['max_sentence_length']}).",
                    location=f"sentence {i+1}",
                    original=sent[:120] + ("..." if len(sent) > 120 else ""),
                    suggestion="Split into two or more sentences. Each sentence should carry one idea (WRITING_STYLE_GUIDE §1.2).",
                    norm_reference="WRITING_STYLE_GUIDE §1.2; Norm 5 (Mayer): Cognitive Load",
                ))

        return diagnostics

    def find_weak_openers(self, text: str) -> list[Diagnostic]:
        """Sword's Writer's Diet: weak sentence openers (it is, there are, this is)."""
        diagnostics = []
        sentences = self._split_sentences(text)
        weak_count = 0

        for i, sent in enumerate(sentences):
            for pat in WEAK_OPENERS:
                if re.match(pat, sent.strip(), re.IGNORECASE):
                    weak_count += 1
                    break

        if sentences and (weak_count / len(sentences)) > 0.15:
            diagnostics.append(Diagnostic(
                category=DiagnosticCategory.NOMINALIZATION,
                severity=Severity.WARNING,
                message=f"{weak_count}/{len(sentences)} sentences ({weak_count/len(sentences)*100:.0f}%) open with 'It is/There are/This is'. Target: <15%.",
                suggestion="Replace 'It is X that Y' with 'Y does X'. Replace 'There are N things that...' with a specific subject doing a specific action.",
                norm_reference="Sword Writer's Diet; Norm 4 (Lanham): put the agent in the subject",
            ))

        return diagnostics

    def find_citation_clusters(self, text: str) -> list[Diagnostic]:
        """WRITING_STYLE_GUIDE §4.4: Citation clusters that interrupt prose."""
        diagnostics = []
        # Pattern: multiple (Author, Year) citations in sequence
        cluster_pattern = re.compile(
            r"\([A-Z][a-z]+(?:\s+(?:et\s+al\.|&\s+[A-Z][a-z]+))?,\s*\d{4}"
            r"(?:;\s*[A-Z][a-z]+(?:\s+(?:et\s+al\.|&\s+[A-Z][a-z]+))?,\s*\d{4}){2,}\)"
        )
        for m in cluster_pattern.finditer(text):
            diagnostics.append(Diagnostic(
                category=DiagnosticCategory.CITATION_STYLE,
                severity=Severity.ADVISORY,
                message=f"Citation cluster: {m.group()[:80]}... Weave citations into the narrative instead of stacking them.",
                original=m.group()[:100],
                suggestion="Name the 1-2 most important authors in the prose; cite the rest in a footnote or as supporting references.",
                norm_reference="WRITING_STYLE_GUIDE §4.4",
            ))

        return diagnostics

    # ── Pass 3: Knowledge-Curse Audit (Pinker) ───────────────────────────

    def knowledge_curse_audit(self, text: str, defined_terms: set[str] | None = None) -> list[Diagnostic]:
        """
        Norm 6 (Pinker): Curse of Knowledge.

        Checks for:
        - Technical terms that may not be defined
        - Abbreviations used without expansion
        - Implicit reasoning steps
        """
        diagnostics = []

        if defined_terms is None:
            defined_terms = set()

        # Find abbreviations (2+ uppercase letters) not preceded by expansion
        abbrev_pattern = re.compile(r"\b([A-Z]{2,})\b")
        expansion_pattern = re.compile(r"\(([A-Z]{2,})\)")

        # Find all abbreviations that have been expanded (in parentheses after full term)
        expanded = set()
        for m in expansion_pattern.finditer(text):
            expanded.add(m.group(1))

        # Find abbreviations used without expansion
        first_use = {}
        for m in abbrev_pattern.finditer(text):
            abbrev = m.group(1)
            if abbrev not in first_use:
                first_use[abbrev] = m.start()

        # Common abbreviations that don't need expansion
        common_abbrevs = {
            "US", "UK", "EU", "UN", "DNA", "RNA", "MRI", "fMRI", "EEG",
            "LED", "UV", "IR", "API", "URL", "HTML", "CSS", "JSON",
            "APA", "DOI", "PDF", "PhD", "MD", "CEO", "CTO", "AI", "ML",
            "IQ", "EQ", "HR", "OR", "CI", "SD", "SE", "df", "VR", "AR",
            "ANOVA", "ANCOVA", "MANOVA", "HLM", "SEM", "CFA", "EFA",
            "BOLD", "SCN", "HPA", "LC", "NE", "PP", "BN", "EN",
        }

        for abbrev, pos in first_use.items():
            if (abbrev not in expanded and
                abbrev not in common_abbrevs and
                abbrev not in defined_terms and
                len(abbrev) <= 6):
                diagnostics.append(Diagnostic(
                    category=DiagnosticCategory.JARGON,
                    severity=Severity.ADVISORY,
                    message=f"Abbreviation '{abbrev}' used without expansion. Spell out on first use.",
                    original=abbrev,
                    suggestion=f"Write 'Full Term ({abbrev})' on first use, then use '{abbrev}' thereafter.",
                    norm_reference="Norm 6 (Pinker): Curse of Knowledge; WRITING_STYLE_GUIDE §4.3",
                ))

        return diagnostics

    # ── Composite Diagnostics ────────────────────────────────────────────

    def writers_diet(self, text: str) -> WritersDiet:
        """
        Sword's Writer's Diet — 5-category word health diagnostic.

        Returns percentage of words in each category and an overall verdict.
        """
        words = self._tokenize(text)
        total = len(words)
        if total == 0:
            return WritersDiet(verdict="Empty text")

        be_count = sum(1 for w in words if w in BE_VERBS)
        prep_count = sum(1 for w in words if w in PREPOSITIONS)
        nom_count = sum(1 for w in words
                       if len(w) > 6
                       and w.endswith(NOMINALIZATION_SUFFIXES)
                       and w not in NOMINALIZATION_EXCEPTIONS)

        # Rough adjective/adverb heuristic: words ending in -ly, -ful, -ous, -ive, -able, -ible
        adj_adv_suffixes = ("ly", "ful", "ous", "ive", "able", "ible", "ical", "ular")
        adj_adv_count = sum(1 for w in words if w.endswith(adj_adv_suffixes) and len(w) > 4)

        # Weak openers
        sentences = self._split_sentences(text)
        weak_opener_count = 0
        for sent in sentences:
            for pat in WEAK_OPENERS:
                if re.match(pat, sent.strip(), re.IGNORECASE):
                    weak_opener_count += 1
                    break

        diet = WritersDiet(
            be_verb_pct=(be_count / total) * 100,
            abstract_noun_pct=(nom_count / total) * 100,
            preposition_pct=(prep_count / total) * 100,
            adjadv_pct=(adj_adv_count / total) * 100,
            it_this_there_pct=(weak_opener_count / max(len(sentences), 1)) * 100,
            total_words=total,
        )

        # Compute verdict based on Sword's categories
        score = 0
        if diet.be_verb_pct > 5:
            score += 2
        elif diet.be_verb_pct > 3:
            score += 1
        if diet.abstract_noun_pct > 5:
            score += 2
        elif diet.abstract_noun_pct > 3:
            score += 1
        if diet.preposition_pct > 18:
            score += 2
        elif diet.preposition_pct > 14:
            score += 1
        if diet.adjadv_pct > 6:
            score += 2
        elif diet.adjadv_pct > 4:
            score += 1
        if diet.it_this_there_pct > 20:
            score += 2
        elif diet.it_this_there_pct > 10:
            score += 1

        verdicts = {
            0: "Lean & Mean",
            1: "Fit & Trim",
            2: "Fit & Trim",
            3: "Needs Toning",
            4: "Needs Toning",
            5: "Flabby",
            6: "Flabby",
            7: "Heart Attack Territory",
            8: "Heart Attack Territory",
            9: "Heart Attack Territory",
            10: "Heart Attack Territory",
        }
        diet.verdict = verdicts.get(score, "Heart Attack Territory")

        return diet

    def lard_factor(self, text: str) -> float:
        """
        Norm 5 (Lanham): Estimate the lard factor.

        The lard factor is the percentage of words that carry no information.
        This is a heuristic estimate based on nominalization density,
        preposition chains, throat-clearing phrases, and passive constructions.
        A full computation requires actually revising the text (which is Pass 2's job).

        Returns: estimated lard factor as percentage (0-100).
        """
        words = self._tokenize(text)
        total = len(words)
        if total == 0:
            return 0.0

        lard_words = 0

        # Count preposition chain words
        for m in re.finditer(r"\b(of the|in the|for the|by the|with the|on the|at the|from the|to the)\b", text, re.IGNORECASE):
            lard_words += 2

        # Count throat-clearing phrase words
        for pat in THROAT_CLEARERS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                lard_words += len(m.group().split())

        # Count nominalization overhead (each nominalization adds ~2 extra words)
        nom_count = sum(1 for w in words
                       if len(w) > 6
                       and w.endswith(NOMINALIZATION_SUFFIXES)
                       and w not in NOMINALIZATION_EXCEPTIONS)
        lard_words += nom_count * 2

        return min((lard_words / total) * 100, 100.0)

    # ── Full Critique ────────────────────────────────────────────────────

    def full_critique(self, text: str, defined_terms: set[str] | None = None) -> ProseHealthReport:
        """
        Run the complete 3-pass revision protocol.

        Returns a ProseHealthReport with quantitative metrics,
        diagnostics organized by pass, and an overall score.
        """
        words = self._tokenize(text)
        sentences = self._split_sentences(text)
        paragraphs = self._split_paragraphs(text)

        # Basic metrics
        report = ProseHealthReport()
        report.word_count = len(words)
        report.sentence_count = len(sentences)
        report.paragraph_count = len(paragraphs)

        if sentences:
            sentence_lengths = [len(self._tokenize(s)) for s in sentences]
            report.avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
            report.max_sentence_length = max(sentence_lengths)
        if paragraphs:
            para_lengths = [len(self._split_sentences(p)) for p in paragraphs]
            report.avg_paragraph_length = sum(para_lengths) / len(para_lengths)

        # Nominalization density
        nom_count = sum(1 for w in words
                       if len(w) > 6
                       and w.endswith(NOMINALIZATION_SUFFIXES)
                       and w not in NOMINALIZATION_EXCEPTIONS)
        report.nominalization_density = (nom_count / max(len(words), 1)) * 100

        # Passive voice
        passive_pattern = re.compile(
            r"\b(is|are|was|were|be|been|being)\s+(being\s+)?(\w+(?:ed|en|nt|wn|ck|lt|pt|ft|ght))\b",
            re.IGNORECASE,
        )
        passive_count = sum(1 for s in sentences if passive_pattern.search(s))
        report.passive_voice_pct = (passive_count / max(len(sentences), 1)) * 100

        # Lard factor
        report.lard_factor_estimate = self.lard_factor(text)

        # Writer's Diet
        report.writers_diet = self.writers_diet(text)

        # Pass 1: Structural (Doumont)
        report.pass1_structural = self.structural_audit(text)

        # Pass 2: Sentence-level (Lanham + Williams)
        report.pass2_sentence = (
            self.find_nominalizations(text) +
            self.find_passive_voice(text) +
            self.find_hedge_stacks(text) +
            self.find_throat_clearing(text) +
            self.find_overclaiming(text) +
            self.find_long_sentences(text) +
            self.find_weak_openers(text) +
            self.find_citation_clusters(text)
        )

        # Pass 3: Knowledge-curse audit (Pinker)
        report.pass3_knowledge = self.knowledge_curse_audit(text, defined_terms)

        # Compute overall score (0-10)
        deductions = 0.0
        for d in report.all_diagnostics:
            if d.severity == Severity.CRITICAL:
                deductions += 1.0
            elif d.severity == Severity.WARNING:
                deductions += 0.4
            elif d.severity == Severity.ADVISORY:
                deductions += 0.1

        # Additional deductions for quantitative metrics
        if report.nominalization_density > 7:
            deductions += 1.5
        elif report.nominalization_density > 4:
            deductions += 0.5
        if report.passive_voice_pct > 35:
            deductions += 1.5
        elif report.passive_voice_pct > 20:
            deductions += 0.5
        if report.lard_factor_estimate > 50:
            deductions += 1.5
        elif report.lard_factor_estimate > 35:
            deductions += 0.5

        report.overall_score = max(0.0, min(10.0, 10.0 - deductions))

        # Verdict
        if report.overall_score >= 8.5:
            report.verdict = "Excellent — clean, active prose"
        elif report.overall_score >= 7.0:
            report.verdict = "Good — minor revisions would help"
        elif report.overall_score >= 5.0:
            report.verdict = "Needs Work — apply Paramedic Method"
        elif report.overall_score >= 3.0:
            report.verdict = "Significant Issues — structural + sentence revision needed"
        else:
            report.verdict = "Major Revision Required"

        # Summary
        issues = []
        if report.critical_count > 0:
            issues.append(f"{report.critical_count} critical")
        if report.warning_count > 0:
            issues.append(f"{report.warning_count} warnings")
        report.summary = (
            f"{report.word_count} words, {report.sentence_count} sentences. "
            f"Score: {report.overall_score:.1f}/10 ({report.verdict}). "
            f"Writer's Diet: {report.writers_diet.verdict}. "
            f"Lard factor: {report.lard_factor_estimate:.0f}%. "
            f"Diagnostics: {', '.join(issues) if issues else 'none significant'}."
        )

        return report

    def suggest_revisions(self, text: str, max_suggestions: int = 10) -> list[Diagnostic]:
        """
        Generate a prioritized list of revision suggestions.

        Returns the most impactful diagnostics sorted by severity,
        limited to max_suggestions.
        """
        report = self.full_critique(text)
        all_diags = report.all_diagnostics

        # Sort by severity (critical first) then by category
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.WARNING: 1,
            Severity.ADVISORY: 2,
            Severity.INFO: 3,
        }
        sorted_diags = sorted(all_diags, key=lambda d: severity_order.get(d.severity, 4))

        return sorted_diags[:max_suggestions]

    def format_report(self, report: ProseHealthReport) -> str:
        """Format a ProseHealthReport as readable text."""
        lines = []
        lines.append(f"# Prose Health Report")
        lines.append(f"")
        lines.append(f"**Summary**: {report.summary}")
        lines.append(f"")
        lines.append(f"## Quantitative Metrics")
        lines.append(f"")
        lines.append(f"| Metric | Value | Target |")
        lines.append(f"|--------|-------|--------|")
        lines.append(f"| Words | {report.word_count} | — |")
        lines.append(f"| Sentences | {report.sentence_count} | — |")
        lines.append(f"| Avg sentence length | {report.avg_sentence_length:.1f} | ~22 |")
        lines.append(f"| Max sentence length | {report.max_sentence_length} | <{self._thresholds['max_sentence_length']} |")
        lines.append(f"| Nominalization density | {report.nominalization_density:.1f}/100 | <4/100 |")
        lines.append(f"| Passive voice | {report.passive_voice_pct:.0f}% | <20% |")
        lines.append(f"| Lard factor | {report.lard_factor_estimate:.0f}% | <35% |")
        lines.append(f"| Writer's Diet | {report.writers_diet.verdict} | Lean or Fit |")
        lines.append(f"| Overall score | {report.overall_score:.1f}/10 | — |")
        lines.append(f"")

        for pass_name, diags in [
            ("Pass 1: Structural (Doumont)", report.pass1_structural),
            ("Pass 2: Sentence-Level (Lanham + Williams)", report.pass2_sentence),
            ("Pass 3: Knowledge-Curse Audit (Pinker)", report.pass3_knowledge),
        ]:
            if diags:
                lines.append(f"## {pass_name}")
                lines.append(f"")
                for d in diags:
                    icon = {"critical": "!!!", "warning": "!!", "advisory": "!", "info": ""}[d.severity.value]
                    lines.append(f"- **[{d.severity.value.upper()}]** {d.message}")
                    if d.suggestion:
                        lines.append(f"  - *Suggestion*: {d.suggestion}")
                    if d.norm_reference:
                        lines.append(f"  - *Norm*: {d.norm_reference}")
                    lines.append(f"")

        return "\n".join(lines)
