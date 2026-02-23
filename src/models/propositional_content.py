"""
Article Eater - Propositional Content Model
ARCH-4 Sprint 1.2: Data Model Implementation

Represents the content of a belief as a structured proposition.
Designed per Liskov panel review for clean separation of content from epistemic status.

Reference: contracts/schemas/propositional_content.v1.schema.json
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import re


# ============================================================
# ENUMS
# ============================================================

class ContentType(Enum):
    """Type of propositional content - affects how it can be evaluated and combined."""
    CAUSAL_CLAIM = "causal_claim"
    CORRELATIONAL_CLAIM = "correlational_claim"
    DEFINITIONAL = "definitional"
    OBSERVATIONAL = "observational"
    THEORETICAL = "theoretical"


class Polarity(Enum):
    """Whether the proposition is stated positively or as negation."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Variables:
    """Variables referenced in a proposition."""
    antecedent: List[str] = field(default_factory=list)
    consequent: List[str] = field(default_factory=list)
    mediators: List[str] = field(default_factory=list)
    moderators: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Variables':
        return cls(
            antecedent=data.get('antecedent', []),
            consequent=data.get('consequent', []),
            mediators=data.get('mediators', []),
            moderators=data.get('moderators', [])
        )


@dataclass
class ScopeCondition:
    """
    Scope conditions for a proposition.
    Per Pearl transportability - specifies when the proposition applies.
    """
    population: Optional[str] = None
    context: Optional[str] = None
    temporal: Optional[str] = None
    exceptions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None and v != []}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScopeCondition':
        return cls(
            population=data.get('population'),
            context=data.get('context'),
            temporal=data.get('temporal'),
            exceptions=data.get('exceptions', [])
        )

    def is_within_scope(self, context: Dict[str, Any]) -> bool:
        """Check if a given context falls within this scope."""
        # Check exceptions first
        for exception in self.exceptions:
            if exception.lower() in str(context).lower():
                return False

        # Check population if specified
        if self.population and 'population' in context:
            if self.population.lower() not in context['population'].lower():
                return False

        # Check context if specified
        if self.context and 'context' in context:
            if self.context.lower() not in context['context'].lower():
                return False

        return True


@dataclass
class PropositionalContent:
    """
    Content of a belief as a structured proposition.

    This class represents WHAT is believed, separate from HOW STRONGLY
    it is believed (EpistemicStatus) and WHERE it comes from (Provenance).

    Design principle (Liskov): Content should be substitutable without
    affecting epistemic status logic.
    """
    proposition_id: str
    canonical_form: str
    content_type: ContentType
    domain: Optional[str] = None
    variables: Optional[Variables] = None
    scope: Optional[ScopeCondition] = None
    polarity: Polarity = Polarity.POSITIVE
    aliases: List[str] = field(default_factory=list)

    # Validation patterns
    EDGE_PATTERN = re.compile(r'^[a-z_]+→[a-z_]+$')
    DOTTED_PATTERN = re.compile(r'^[a-z_]+\.[a-z_]+\.[a-z_]+$')

    def __post_init__(self):
        """Validate proposition_id format."""
        if not self._is_valid_proposition_id(self.proposition_id):
            # Allow flexible IDs but log warning
            pass  # In production, could log warning here

        # Ensure content_type is enum
        if isinstance(self.content_type, str):
            self.content_type = ContentType(self.content_type)

        # Ensure polarity is enum
        if isinstance(self.polarity, str):
            self.polarity = Polarity(self.polarity)

    def _is_valid_proposition_id(self, prop_id: str) -> bool:
        """Check if proposition_id matches expected patterns."""
        return bool(
            self.EDGE_PATTERN.match(prop_id) or
            self.DOTTED_PATTERN.match(prop_id)
        )

    @property
    def is_causal(self) -> bool:
        """Check if this is a causal claim."""
        return self.content_type == ContentType.CAUSAL_CLAIM

    @property
    def is_observational(self) -> bool:
        """Check if this is an observational claim."""
        return self.content_type == ContentType.OBSERVATIONAL

    def matches_alias(self, query: str) -> bool:
        """Check if query matches canonical form or any alias."""
        query_lower = query.lower()
        if query_lower in self.canonical_form.lower():
            return True
        return any(query_lower in alias.lower() for alias in self.aliases)

    def extract_edge_notation(self) -> Optional[tuple]:
        """
        If proposition_id uses edge notation (A→B), extract source and target.
        Returns None if not in edge notation.
        """
        if '→' in self.proposition_id:
            parts = self.proposition_id.split('→')
            if len(parts) == 2:
                return (parts[0], parts[1])
        return None

    def negated(self) -> 'PropositionalContent':
        """Return a new PropositionalContent with negated polarity."""
        new_polarity = Polarity.NEGATIVE if self.polarity == Polarity.POSITIVE else Polarity.POSITIVE
        return PropositionalContent(
            proposition_id=f"neg_{self.proposition_id}",
            canonical_form=f"NOT: {self.canonical_form}",
            content_type=self.content_type,
            domain=self.domain,
            variables=self.variables,
            scope=self.scope,
            polarity=new_polarity,
            aliases=[f"not {a}" for a in self.aliases]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'proposition_id': self.proposition_id,
            'canonical_form': self.canonical_form,
            'content_type': self.content_type.value,
            'polarity': self.polarity.value,
        }

        if self.domain:
            result['domain'] = self.domain
        if self.variables:
            result['variables'] = self.variables.to_dict()
        if self.scope:
            result['scope'] = self.scope.to_dict()
        if self.aliases:
            result['aliases'] = self.aliases

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropositionalContent':
        """Create from dictionary."""
        variables = None
        if 'variables' in data:
            variables = Variables.from_dict(data['variables'])

        scope = None
        if 'scope' in data:
            scope = ScopeCondition.from_dict(data['scope'])

        return cls(
            proposition_id=data['proposition_id'],
            canonical_form=data['canonical_form'],
            content_type=ContentType(data['content_type']),
            domain=data.get('domain'),
            variables=variables,
            scope=scope,
            polarity=Polarity(data.get('polarity', 'positive')),
            aliases=data.get('aliases', [])
        )

    @classmethod
    def from_legacy_belief(cls, belief_content: str, belief_id: str,
                           level: str = None) -> 'PropositionalContent':
        """
        Create PropositionalContent from legacy Belief format.
        Used for migration from v1 to v2.
        """
        # Infer content type from level if available
        content_type_map = {
            'THEORETICAL': ContentType.THEORETICAL,
            'INTERMEDIATE': ContentType.CAUSAL_CLAIM,
            'EMPIRICAL': ContentType.CORRELATIONAL_CLAIM,
            'OBSERVATIONAL': ContentType.OBSERVATIONAL,
        }
        content_type = content_type_map.get(level, ContentType.CAUSAL_CLAIM)

        # Extract domain from belief_id if in edge notation
        domain = None
        if '.' in belief_id:
            domain = belief_id.split('.')[0]

        return cls(
            proposition_id=belief_id,
            canonical_form=belief_content,
            content_type=content_type,
            domain=domain
        )


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def generate_proposition_id(domain: str, subject: str, predicate: str) -> str:
    """Generate a proposition ID in dotted notation."""
    return f"{domain.lower()}.{subject.lower()}.{predicate.lower()}"


def generate_edge_id(source: str, target: str) -> str:
    """Generate a proposition ID in edge notation."""
    return f"{source.lower()}→{target.lower()}"
