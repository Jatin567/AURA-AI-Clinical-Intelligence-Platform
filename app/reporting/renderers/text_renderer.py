from app.reporting.models import ClinicalReport
from app.reporting.renderers.base import ReportRenderer


class TextRenderer(ReportRenderer):
    """
    Renders the clinical report as a plain text string.
    """
    def render(self, report: ClinicalReport) -> str:
        lines = []
        
        lines.append("=" * 60)
        lines.append("AURA CLINICAL ASSESSMENT REPORT")
        lines.append("=" * 60)
        lines.append(f"Assessment ID: {report.metadata.assessment_id}")
        lines.append(f"Severity:      {report.severity.upper()}")
        lines.append(f"Date:          {report.metadata.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("=" * 60)
        lines.append("")

        lines.append("PATIENT SUMMARY")
        lines.append("-" * 20)
        lines.append(f"Chief Complaint: {report.patient_summary.chief_complaint or 'N/A'}")
        lines.append(f"Age: {report.patient_summary.age or 'N/A'}")
        lines.append(f"Sex: {report.patient_summary.sex or 'N/A'}")
        if report.patient_summary.chronic_conditions:
            lines.append(f"Chronic Conditions: {', '.join(report.patient_summary.chronic_conditions)}")
        if report.patient_summary.medications:
            lines.append(f"Medications: {', '.join(report.patient_summary.medications)}")
        if report.patient_summary.allergies:
            lines.append(f"Allergies: {', '.join(report.patient_summary.allergies)}")
        lines.append("")

        if report.safety_notices:
            lines.append("SAFETY NOTICES")
            lines.append("-" * 20)
            for sn in report.safety_notices:
                action_str = " [IMMEDIATE ACTION REQUIRED]" if sn.immediate_action_required else ""
                lines.append(f"! {sn.title} ({sn.severity}){action_str}")
                lines.append(f"  {sn.message}")
            lines.append("")

        lines.append("CLINICAL REASONING SUMMARY")
        lines.append("-" * 20)
        lines.append(f"Leading Condition: {report.clinical_reasoning_summary.leading_condition or 'Unknown'}")
        if report.clinical_reasoning_summary.confidence is not None:
            lines.append(f"Confidence: {report.clinical_reasoning_summary.confidence:.2f}")
        lines.append(f"Summary: {report.clinical_reasoning_summary.summary}")
        lines.append("")

        lines.append("POSSIBLE CONDITIONS")
        lines.append("-" * 20)
        for idx, pc in enumerate(report.possible_conditions, 1):
            lines.append(f"{idx}. {pc.condition_name} ({pc.confidence_percent}%)")
            lines.append(f"   Explanation: {pc.explanation}")
            if pc.supporting_findings:
                lines.append(f"   Supporting: {', '.join(pc.supporting_findings)}")
            if pc.conflicting_findings:
                lines.append(f"   Conflicting: {', '.join(pc.conflicting_findings)}")
        lines.append("")

        if report.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 20)
            for rec in report.recommendations:
                lines.append(f"- {rec.title} ({rec.timeframe})")
                lines.append(f"  {rec.action}")
                lines.append(f"  Rationale: {rec.rationale}")
            lines.append("")

        lines.append("CLINICAL DISCLAIMER")
        lines.append("-" * 20)
        lines.append(report.clinical_disclaimer.informational_only)
        lines.append(report.clinical_disclaimer.not_a_diagnosis)
        lines.append(report.clinical_disclaimer.seek_professional_care)
        
        return "\n".join(lines)
