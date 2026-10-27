from app.reporting.models import ClinicalReport
from app.reporting.renderers.base import ReportRenderer


class HTMLRenderer(ReportRenderer):
    """
    Renders the clinical report as semantic HTML with embedded CSS.
    """
    
    CSS = """
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1, h2, h3 { color: #111; }
    .header { border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
    .meta { font-size: 0.9em; color: #666; }
    .severity { font-weight: bold; padding: 4px 8px; border-radius: 4px; display: inline-block; }
    .severity-emergency { background: #fee2e2; color: #991b1b; }
    .severity-urgent { background: #ffedd5; color: #9a3412; }
    .severity-routine { background: #fef9c3; color: #854d0e; }
    .safety-notice { background: #fee2e2; border-left: 4px solid #ef4444; padding: 10px; margin: 10px 0; }
    .card { border: 1px solid #ddd; border-radius: 6px; padding: 15px; margin-bottom: 15px; }
    .condition-confidence { font-weight: bold; color: #0284c7; }
    .disclaimer { font-size: 0.85em; color: #555; font-style: italic; border-top: 1px solid #eee; padding-top: 15px; margin-top: 30px; }
    """

    def render(self, report: ClinicalReport) -> str:
        sev_class = f"severity-{report.severity.lower()}" if report.severity.lower() in ["emergency", "urgent", "routine"] else "severity-routine"
        
        html = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            f"<title>AURA Clinical Report - {report.metadata.assessment_id}</title>",
            f"<style>{self.CSS}</style>",
            "</head>",
            "<body>"
        ]
        
        # Header
        html.extend([
            "<div class='header'>",
            "<h1>AURA Clinical Assessment Report</h1>",
            f"<div class='meta'>Assessment ID: {report.metadata.assessment_id}</div>",
            f"<div class='meta'>Date: {report.metadata.generation_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>",
            f"<div class='meta' style='margin-top: 10px;'>Severity: <span class='severity {sev_class}'>{report.severity.upper()}</span></div>",
            "</div>"
        ])
        
        # Safety Notices
        if report.safety_notices:
            for sn in report.safety_notices:
                html.append(f"<div class='safety-notice'>")
                html.append(f"<strong>{sn.title}</strong><br/>")
                html.append(f"{sn.message}")
                html.append("</div>")

        # Patient Summary
        html.append("<h2>Patient Summary</h2>")
        html.append("<ul>")
        html.append(f"<li><strong>Chief Complaint:</strong> {report.patient_summary.chief_complaint or 'N/A'}</li>")
        html.append(f"<li><strong>Age/Sex:</strong> {report.patient_summary.age or 'N/A'} / {report.patient_summary.sex or 'N/A'}</li>")
        if report.patient_summary.chronic_conditions:
            html.append(f"<li><strong>Chronic Conditions:</strong> {', '.join(report.patient_summary.chronic_conditions)}</li>")
        if report.patient_summary.medications:
            html.append(f"<li><strong>Medications:</strong> {', '.join(report.patient_summary.medications)}</li>")
        if report.patient_summary.allergies:
            html.append(f"<li><strong>Allergies:</strong> {', '.join(report.patient_summary.allergies)}</li>")
        html.append("</ul>")

        # Reasoning Summary
        html.append("<h2>Clinical Reasoning Summary</h2>")
        html.append(f"<p><strong>Leading Condition:</strong> {report.clinical_reasoning_summary.leading_condition or 'Unknown'}</p>")
        html.append(f"<p>{report.clinical_reasoning_summary.summary}</p>")

        # Possible Conditions
        html.append("<h2>Possible Conditions</h2>")
        for pc in report.possible_conditions:
            html.append("<div class='card'>")
            html.append(f"<h3>{pc.condition_name} <span class='condition-confidence'>({pc.confidence_percent}%)</span></h3>")
            html.append(f"<p>{pc.explanation}</p>")
            if pc.supporting_findings:
                html.append(f"<p><strong>Supporting:</strong> {', '.join(pc.supporting_findings)}</p>")
            if pc.conflicting_findings:
                html.append(f"<p><strong>Conflicting:</strong> {', '.join(pc.conflicting_findings)}</p>")
            html.append("</div>")
            
        # Recommendations
        if report.recommendations:
            html.append("<h2>Recommendations</h2>")
            for rec in report.recommendations:
                html.append("<div class='card'>")
                html.append(f"<h3>{rec.title} ({rec.timeframe})</h3>")
                html.append(f"<p>{rec.action}</p>")
                html.append(f"<p><em>Rationale: {rec.rationale}</em></p>")
                html.append("</div>")

        # Disclaimer
        html.append("<div class='disclaimer'>")
        html.append(f"<p>{report.clinical_disclaimer.informational_only}</p>")
        html.append(f"<p>{report.clinical_disclaimer.not_a_diagnosis}</p>")
        html.append(f"<p>{report.clinical_disclaimer.seek_professional_care}</p>")
        html.append("</div>")

        html.extend(["</body>", "</html>"])
        
        return "\n".join(html)
