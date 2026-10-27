import uuid
from typing import Optional
from app.reporting.models import (
    AssessmentContext, ClinicalReport, ReportMetadata, PatientSummary,
    InterviewSummary, EvidenceItem, ReasoningSummary, PossibleCondition,
    RiskFactor, Recommendation, SafetyNotice, ClinicalDisclaimer, AuditMetadata
)
from app.reasoning.models import ClinicalReasoningOutput
from app.explanation.models import ClinicalExplanation
from app.reporting.report_validator import ReportValidator

class ReportGenerator:
    """
    Generates structured clinical assessment reports from deterministic outputs.
    Does NOT perform reasoning or modify logic.
    """

    def __init__(self, app_version: str = "1.0", kb_version: str = "1.0",
                 reasoning_version: str = "1.0", explanation_version: str = "1.0"):
        self.app_version = app_version
        self.kb_version = kb_version
        self.reasoning_version = reasoning_version
        self.explanation_version = explanation_version

    def generate(self, context: AssessmentContext, reasoning_output: ClinicalReasoningOutput,
                 explanation: ClinicalExplanation) -> ClinicalReport:
        
        # 1. Resolve Assessment ID
        assessment_id = context.assessment_id or context.session_id or str(uuid.uuid4())

        # 2. Build Metadata
        metadata = ReportMetadata(
            assessment_id=assessment_id,
            session_id=context.session_id,
            aura_version=self.app_version,
            knowledge_base_version=self.kb_version,
            reasoning_engine_version=self.reasoning_version,
            explanation_engine_version=self.explanation_version
        )

        # 3. Build Patient Summary
        patient_summary = PatientSummary(
            chief_complaint=context.chief_complaint,
            age=context.age,
            sex=context.sex,
            chronic_conditions=context.chronic_conditions,
            medications=context.medications,
            allergies=context.allergies
        )

        # 4. Build Interview Summary
        interview_summary = InterviewSummary(
            turn_count=context.interview_turn_count,
            completion_reason=context.interview_completion_reason,
            symptom_duration=context.symptom_duration,
            symptom_severity=context.symptom_severity
        )

        # 5. Build Evidence Summary
        evidence_summary = []
        for ev in context.evidence_collected:
            evidence_summary.append(
                EvidenceItem(
                    source=ev.get("source", "UNKNOWN"),
                    key=ev.get("key", "unknown_key"),
                    value=ev.get("value"),
                    confidence_weight=ev.get("confidence_weight", 1.0),
                    timestamp=ev.get("timestamp")
                )
            )

        # 6. Build Reasoning Summary
        reasoning_summary = ReasoningSummary(
            leading_condition=explanation.executive_summary.leading_condition,
            confidence=explanation.executive_summary.confidence,
            summary=explanation.executive_summary.summary
        )

        # 7. Build Possible Conditions
        possible_conditions = []
        for pc in explanation.possible_conditions:
            possible_conditions.append(
                PossibleCondition(
                    condition_name=pc.condition_name,
                    confidence=pc.confidence,
                    confidence_percent=pc.confidence_percent,
                    supporting_findings=pc.supporting_findings,
                    conflicting_findings=pc.conflicting_findings,
                    explanation=pc.explanation
                )
            )

        # 8. Build Risk Factors
        risk_factors = []
        for rf in explanation.risk_factors:
            risk_factors.append(
                RiskFactor(
                    factor_name=rf.factor_name,
                    description=rf.description,
                    risk_weight=rf.risk_weight,
                    affected_condition=rf.affected_condition,
                    explanation=rf.explanation
                )
            )

        # 9. Missing Information
        missing_information = explanation.missing_information

        # 10. Recommendations
        recommendations = []
        for rec in explanation.recommendations:
            recommendations.append(
                Recommendation(
                    severity=rec.severity,
                    title=rec.title,
                    action=rec.action,
                    timeframe=rec.timeframe,
                    rationale=rec.rationale,
                    priority=rec.priority
                )
            )

        # 11. Safety Notices
        safety_notices = []
        for sn in explanation.safety_notices:
            safety_notices.append(
                SafetyNotice(
                    severity=sn.severity,
                    title=sn.title,
                    message=sn.message,
                    immediate_action_required=sn.immediate_action_required
                )
            )

        # 12. Clinical Disclaimer
        clinical_disclaimer = ClinicalDisclaimer(
            informational_only=explanation.disclaimer.informational_only,
            not_a_diagnosis=explanation.disclaimer.not_a_diagnosis,
            seek_professional_care=explanation.disclaimer.seek_professional_care
        )

        # 13. Audit Metadata
        audit_metadata = AuditMetadata(
            reasoning_steps=[step.description for step in reasoning_output.reasoning_steps]
        )

        report = ClinicalReport(
            metadata=metadata,
            patient_summary=patient_summary,
            interview_summary=interview_summary,
            evidence_summary=evidence_summary,
            clinical_reasoning_summary=reasoning_summary,
            possible_conditions=possible_conditions,
            risk_factors=risk_factors,
            missing_information=missing_information,
            severity=context.severity,
            recommendations=recommendations,
            safety_notices=safety_notices,
            clinical_disclaimer=clinical_disclaimer,
            audit_metadata=audit_metadata
        )

        ReportValidator.validate(report)

        return report
