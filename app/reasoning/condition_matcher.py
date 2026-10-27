import re
from typing import List, Tuple, Set
from app.reasoning.models import ClinicalInput, ConditionDefinition
from app.reasoning.knowledge_repository import KnowledgeRepository


class ConditionMatchCandidate:
    """Internal candidate representation before confidence normalization."""
    def __init__(
        self,
        condition: ConditionDefinition,
        supporting_symptoms: List[str],
        conflicting_symptoms: List[str],
        base_score: float
    ):
        self.condition = condition
        self.supporting_symptoms = supporting_symptoms
        self.conflicting_symptoms = conflicting_symptoms
        self.base_score = base_score


class ConditionMatcher:
    """
    Rule-based condition matcher that consumes the data-driven KnowledgeRepository.
    Evaluates patient symptom presentations against primary, secondary, and conflicting
    symptom rules defined in the repository without using any LLM or machine learning.
    """

    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository

    def match_conditions(self, clinical_input: ClinicalInput) -> List[ConditionMatchCandidate]:
        """
        Matches patient clinical input against all conditions in the repository.
        Returns a list of condition match candidates that have supporting symptoms.
        """
        # Gather and normalize patient tokens
        patient_tokens = self._extract_symptom_tokens(clinical_input)
        candidates: List[ConditionMatchCandidate] = []

        for condition in self.repository.get_all_conditions():
            candidate = self._evaluate_condition(condition, patient_tokens)
            if candidate and candidate.supporting_symptoms:
                candidates.append(candidate)

        # Sort candidates descending by base score
        candidates.sort(key=lambda c: c.base_score, reverse=True)
        return candidates

    def _extract_symptom_tokens(self, clinical_input: ClinicalInput) -> Set[str]:
        """Extracts and normalizes all symptom phrases into lowercase text tokens."""
        tokens: Set[str] = set()
        
        # Add explicit symptom tags
        for s in clinical_input.symptoms:
            tokens.add(s.strip().lower())
            
        # Add chief complaint terms
        if clinical_input.chief_complaint:
            cc = clinical_input.chief_complaint.lower()
            tokens.add(cc)
            # Add word phrases
            for phrase in re.split(r'[,;.\n]', cc):
                clean = phrase.strip()
                if clean:
                    tokens.add(clean)

        return tokens

    def _evaluate_condition(
        self, condition: ConditionDefinition, patient_tokens: Set[str]
    ) -> ConditionMatchCandidate:
        """Evaluates a single condition definition against patient symptom tokens."""
        supporting: List[str] = []
        conflicting: List[str] = []

        # 1. Match Primary Symptoms (Weight = 2.0)
        primary_matches = 0
        for ps in condition.primary_symptoms:
            if self._token_matches(ps, patient_tokens):
                primary_matches += 1
                if ps not in supporting:
                    supporting.append(ps)

        # 2. Match Secondary Symptoms (Weight = 1.0)
        secondary_matches = 0
        for ss in condition.secondary_symptoms:
            if self._token_matches(ss, patient_tokens):
                secondary_matches += 1
                if ss not in supporting:
                    supporting.append(ss)

        # 3. Match Conflicting Symptoms (Penalty = -0.2)
        for cs in condition.conflicting_symptoms:
            if self._token_matches(cs, patient_tokens):
                if cs not in conflicting:
                    conflicting.append(cs)

        if not supporting:
            return ConditionMatchCandidate(
                condition=condition,
                supporting_symptoms=[],
                conflicting_symptoms=[],
                base_score=0.0
            )

        # 4. Calculate Base Score
        # Max achievable score calculation
        total_primary = max(len(condition.primary_symptoms), 1)
        total_secondary_cap = min(len(condition.secondary_symptoms), 3) or 1
        
        max_possible_points = (total_primary * 2.0) + (total_secondary_cap * 1.0)
        earned_points = (primary_matches * 2.0) + (min(secondary_matches, 3) * 1.0)

        raw_match_ratio = earned_points / max_possible_points
        penalty = len(conflicting) * 0.2
        
        base_score = round(max(0.0, raw_match_ratio - penalty), 4)

        return ConditionMatchCandidate(
            condition=condition,
            supporting_symptoms=supporting,
            conflicting_symptoms=conflicting,
            base_score=base_score
        )

    def _token_matches(self, pattern: str, patient_tokens: Set[str]) -> bool:
        """Helper to match a symptom pattern string against normalized patient tokens."""
        pat_low = pattern.lower().strip()
        for token in patient_tokens:
            if pat_low in token or token in pat_low:
                return True
        return False
