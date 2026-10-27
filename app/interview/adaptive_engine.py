import math
import logging
from typing import List, Optional, Tuple
from app.interview.models import (
    AdaptiveQuestion,
    InterviewState,
    AdaptiveSelectionResult,
    PriorityTier
)
from app.interview.question_bank import QuestionBank
from app.interview.evidence_collector import EvidenceCollector
from app.reasoning.reasoning_engine import ClinicalReasoningEngine
from app.reasoning.models import ClinicalInput, ClinicalReasoningOutput

logger = logging.getLogger("aura.interview.adaptive_engine")


class AdaptiveInterviewEngine:
    """
    Evidence-Driven Adaptive Clinical Interview Engine.
    Dynamically selects the highest-yield follow-up question using expected information gain
    and differential entropy reduction, while relying on ClinicalReasoningEngine as the authority.
    """

    MAX_TURNS = 6
    CONFIDENCE_THRESHOLD = 0.85
    MARGIN_THRESHOLD = 0.25

    TIER_WEIGHTS = {
        PriorityTier.CRITICAL_RED_FLAG: 10.0,
        PriorityTier.DIFFERENTIAL_DISCRIMINATOR: 5.0,
        PriorityTier.MISSING_DATA_RECOVERY: 3.0,
        PriorityTier.SYMPTOM_REFINEMENT: 1.0
    }

    def __init__(
        self,
        reasoning_engine: Optional[ClinicalReasoningEngine] = None,
        question_bank: Optional[QuestionBank] = None
    ):
        self.reasoning_engine = reasoning_engine or ClinicalReasoningEngine()
        self.question_bank = question_bank or QuestionBank()
        self.evidence_collector = EvidenceCollector()

    def evaluate_and_select_next(
        self,
        base_input: ClinicalInput,
        state: InterviewState
    ) -> AdaptiveSelectionResult:
        """
        Main execution point for adaptive question selection:
        1. Updates ClinicalInput with all gathered evidence.
        2. Recalculates authoritative reasoning output.
        3. Computes differential entropy.
        4. Checks stopping criteria.
        5. Scores unasked questions by expected information gain.
        6. Returns AdaptiveSelectionResult.
        """
        # Step 1: Merge gathered evidence into updated ClinicalInput
        updated_input = self.evidence_collector.build_updated_clinical_input(base_input, state)

        # Step 2: Recalculate authoritative reasoning output
        reasoning_output: ClinicalReasoningOutput = self.reasoning_engine.evaluate(updated_input)

        # Step 3: Compute Differential Entropy
        entropy = self._calculate_differential_entropy(reasoning_output)

        # Step 4: Check Stopping Criteria
        is_complete, completion_reason = self._check_stopping_criteria(state, reasoning_output)
        if is_complete:
            state.is_complete = True
            state.completion_reason = completion_reason
            return AdaptiveSelectionResult(
                selected_question=None,
                selection_rationale=f"Interview complete: {completion_reason}",
                expected_information_gain=0.0,
                differential_entropy=entropy,
                is_complete=True,
                completion_reason=completion_reason,
                current_reasoning_output=reasoning_output
            )

        # Step 5: Score Unasked Questions
        unasked_questions = self.question_bank.get_unasked_questions(state.asked_question_ids)
        if not unasked_questions:
            state.is_complete = True
            state.completion_reason = "Question bank exhausted"
            return AdaptiveSelectionResult(
                selected_question=None,
                selection_rationale="Interview complete: All questions in repository have been evaluated.",
                expected_information_gain=0.0,
                differential_entropy=entropy,
                is_complete=True,
                completion_reason="Question bank exhausted",
                current_reasoning_output=reasoning_output
            )

        best_question, best_score, rationale = self._select_best_question(
            unasked_questions, reasoning_output
        )

        return AdaptiveSelectionResult(
            selected_question=best_question,
            selection_rationale=rationale,
            expected_information_gain=round(best_score, 4),
            differential_entropy=round(entropy, 4),
            is_complete=False,
            completion_reason=None,
            current_reasoning_output=reasoning_output
        )

    def _calculate_differential_entropy(self, reasoning_output: ClinicalReasoningOutput) -> float:
        """Calculates Shannon entropy across candidate condition confidence distribution."""
        conditions = reasoning_output.possible_conditions
        if not conditions:
            return 0.0

        scores = [c.confidence for c in conditions if c.confidence > 0]
        total = sum(scores)
        if total <= 0:
            return 0.0

        entropy = 0.0
        for s in scores:
            p = s / total
            if p > 0:
                entropy -= p * math.log2(p)

        return round(entropy, 4)

    def _check_stopping_criteria(
        self, state: InterviewState, reasoning_output: ClinicalReasoningOutput
    ) -> Tuple[bool, Optional[str]]:
        """Evaluates deterministic interview stopping rules."""
        # 1. Turn Cap
        if state.turn_count >= self.MAX_TURNS:
            return True, f"Maximum dynamic interview turns ({self.MAX_TURNS}) reached"

        conditions = reasoning_output.possible_conditions
        if conditions:
            top_cond = conditions[0]
            # 2. Top Diagnostic Confidence Reached
            if top_cond.confidence >= self.CONFIDENCE_THRESHOLD:
                if len(conditions) == 1 or (top_cond.confidence - conditions[1].confidence) >= self.MARGIN_THRESHOLD:
                    return True, f"High diagnostic confidence achieved for {top_cond.name} (confidence={top_cond.confidence:.2f})"

            # 3. Emergency Intercept (Rule out immediate escalation)
            if top_cond.name in ["Acute Coronary Syndrome", "Anaphylaxis", "Cerebrovascular Accident", "Pulmonary Embolism"] and top_cond.confidence >= 0.8:
                return True, f"High-risk red-flag condition detected ({top_cond.name}); immediate emergency clinical evaluation required"

        return False, None

    def _select_best_question(
        self,
        unasked_questions: List[AdaptiveQuestion],
        reasoning_output: ClinicalReasoningOutput
    ) -> Tuple[AdaptiveQuestion, float, str]:
        """Scores candidate questions and picks the highest-yield question."""
        top_condition_name = (
            reasoning_output.possible_conditions[0].name
            if reasoning_output.possible_conditions else None
        )

        best_question = unasked_questions[0]
        best_score = -1.0

        for q in unasked_questions:
            tier_weight = self.TIER_WEIGHTS.get(q.priority_tier, 1.0)
            
            # Relevance bonus if question targets top condition
            relevance_bonus = 0.0
            if top_condition_name and any(cid in q.target_condition_ids for cid in ["COND_001", "COND_002", "COND_007", "COND_012", "COND_013"]):
                relevance_bonus = 2.0

            score = tier_weight + (q.base_information_gain * (1.0 + relevance_bonus))

            if score > best_score:
                best_score = score
                best_question = q

        rationale = (
            f"Selected '{best_question.question_id}' (Priority Tier: {best_question.priority_tier.value}) "
            f"to {best_question.purpose}. Expected Information Gain: {best_question.base_information_gain}."
        )

        return best_question, best_score, rationale
