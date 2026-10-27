from app.reporting.models import ClinicalReport
from app.reporting.renderers.base import ReportRenderer


class MarkdownRenderer(ReportRenderer):
    """
    Renders the clinical report as a Markdown string (GFM).
    """
    def render(self, report: ClinicalReport) -> str:
        lines = []
        
        lines.append(f"# AURA Clinical Assessment Report")
        lines.append(f"**Assessment ID:** `{report.metadata.assessment_id}`  ")
        lines.append(f"**Severity:** **{report.severity.upper()}**  ")
        lines.append(f"**Date:** {report.metadata.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
        lines.append("")

        if report.safety_notices:
            for sn in report.safety_notices:
                alert_type = "CAUTION" if sn.immediate_action_required else "WARNING"
                lines.append(f"> [!{alert_type}]")
                lines.append(f"> **{sn.title} ({sn.severity})**")
                lines.append(f"> {sn.message}")
            lines.append("")

        lines.append("## Patient Summary")
        lines.append(f"- **Chief Complaint:** {report.patient_summary.chief_complaint or 'N/A'}")
        lines.append(f"- **Age/Sex:** {report.patient_summary.age or 'N/A'} / {report.patient_summary.sex or 'N/A'}")
        
        if report.patient_summary.chronic_conditions:
            lines.append(f"- **Chronic Conditions:** {', '.join(report.patient_summary.chronic_conditions)}")
        if report.patient_summary.medications:
            lines.append(f"- **Medications:** {', '.join(report.patient_summary.medications)}")
        if report.patient_summary.allergies:
            lines.append(f"- **Allergies:** {', '.join(report.patient_summary.allergies)}")
        lines.append("")

        lines.append("## Clinical Reasoning Summary")
        lines.append(f"**Leading Condition:** {report.clinical_reasoning_summary.leading_condition or 'Unknown'}  ")
        if report.clinical_reasoning_summary.confidence is not None:
            lines.append(f"**Confidence:** {report.clinical_reasoning_summary.confidence:.2f}  ")
        lines.append(f"{report.clinical_reasoning_summary.summary}")
        lines.append("")

        lines.append("## Possible Conditions")
        for pc in report.possible_conditions:
            lines.append(f"### {pc.condition_name} ({pc.confidence_percent}%)")
            lines.append(f"{pc.explanation}")
            if pc.supporting_findings:
                lines.append(f"- **Supporting:** {', '.join(pc.supporting_findings)}")
            if pc.conflicting_findings:
                lines.append(f"- **Conflicting:** {', '.join(pc.conflicting_findings)}")
            lines.append("")

        if report.recommendations:
            lines.append("## Recommendations")
            for rec in report.recommendations:
                lines.append(f"### {rec.title} ({rec.timeframe})")
                lines.append(f"{rec.action}")
                lines.append(f"*Rationale:* {rec.rationale}")
                lines.append("")

        lines.append("---")
        lines.append("## Clinical Disclaimer")
        lines.append(f"_{report.clinical_disclaimer.informational_only}_")
        lines.append(f"_{report.clinical_disclaimer.not_a_diagnosis}_")
        lines.append(f"_{report.clinical_disclaimer.seek_professional_care}_")
        
        return "\n".join(lines)
