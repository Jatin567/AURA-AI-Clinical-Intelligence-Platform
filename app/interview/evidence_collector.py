import uuid
from typing import List, Any
from app.interview.models import ClinicalEvidence, EvidenceSource, AdaptiveQuestion, InterviewState
from app.reasoning.models import ClinicalInput


class EvidenceCollector:
    """
    Evidence ingestion service.
    Converts interview answers and external observations (OCR, Voice, Labs)
    into structured ClinicalEvidence items and updates ClinicalInput for the reasoning engine.
    """

    def process_interview_answer(
        self,
        question: AdaptiveQuestion,
        answer_value: Any,
        state: InterviewState
    ) -> ClinicalEvidence:
        """
        Converts a patient interview answer into a structured ClinicalEvidence item.
        Appends it to state.gathered_evidence.
        """
        # Map answer_value to symptom_tags based on question.evidence_mapping
        val_str = str(answer_value).strip().lower()
        symptom_tags: List[str] = []

        if question.evidence_mapping:
            for option_key, tags in question.evidence_mapping.items():
                if option_key.lower() == val_str:
                    symptom_tags.extend(tags)

        evidence = ClinicalEvidence(
            evidence_id=f"EV_{uuid.uuid4().hex[:8]}",
            source=EvidenceSource.PATIENT_INTERVIEW,
            key=question.target_evidence_key,
            value=answer_value,
            clinical_tags=symptom_tags,
            confidence_weight=1.0
        )

        state.gathered_evidence.append(evidence)
        state.asked_question_ids.append(question.question_id)
        state.turn_count += 1
        return evidence

    def ingest_external_evidence(
        self,
        source: EvidenceSource,
        key: str,
        value: Any,
        symptom_tags: List[str],
        state: InterviewState,
        confidence_weight: float = 1.0
    ) -> ClinicalEvidence:
        """
        Generic ingestion method for non-interview evidence sources (OCR, Voice, Labs, Imaging).
        Allows future multimodal modules to seamlessly feed into the evidence stream.
        """
        evidence = ClinicalEvidence(
            evidence_id=f"EV_{uuid.uuid4().hex[:8]}",
            source=source,
            key=key,
            value=value,
            clinical_tags=symptom_tags,
            confidence_weight=confidence_weight
        )
        state.gathered_evidence.append(evidence)
        return evidence

    def build_updated_clinical_input(
        self,
        base_input: ClinicalInput,
        state: InterviewState
    ) -> ClinicalInput:
        """
        Merges base ClinicalInput with all gathered ClinicalEvidence observations
        to produce an updated ClinicalInput object for ClinicalReasoningEngine.evaluate().
        """
        merged_symptoms = list(base_input.symptoms)
        duration = base_input.symptom_duration
        severity = base_input.symptom_severity

        for ev in state.gathered_evidence:
            # Merge symptom tags
            for tag in ev.clinical_tags:
                if tag not in merged_symptoms:
                    merged_symptoms.append(tag)

            # Update specific structured parameters if present in evidence
            if ev.key == "symptom_duration" and isinstance(ev.value, str):
                duration = ev.value
            elif ev.key == "symptom_severity" and isinstance(ev.value, (int, float)):
                severity = int(ev.value)

        # Construct updated ClinicalInput instance
        return ClinicalInput(
            symptoms=merged_symptoms,
            chief_complaint=base_input.chief_complaint,
            symptom_duration=duration,
            symptom_severity=severity,
            age=base_input.age,
            sex=base_input.sex,
            chronic_conditions=base_input.chronic_conditions,
            medications=base_input.medications,
            allergies=base_input.allergies
        )
