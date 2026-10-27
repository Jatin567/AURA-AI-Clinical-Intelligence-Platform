from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response
from app.patients.models import Session
from app.api.dependencies import get_auth_session, profile_service, timeline_engine

router = APIRouter(prefix="/export", tags=["export"])

def generate_markdown(patient_id: str) -> str:
    try:
        # Safely fetch patient profile if available
        profile = None
        try:
            profile = profile_service.get_profile(patient_id)
        except Exception:
            profile = None

        # Safely fetch timeline entries using existing TimelineEngine API
        try:
            entries = timeline_engine.get_patient_timeline(patient_id) or []
        except Exception:
            entries = []

        # Safely generate timeline summary if historical entries exist
        summary = None
        if entries:
            try:
                summary = timeline_engine.generate_summary(patient_id)
            except Exception:
                summary = None

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        patient_display = profile.full_name if profile and getattr(profile, "full_name", None) else patient_id

        md = f"# AURA Clinical Summary\n\n"
        md += f"**Patient:** {patient_display}  \n"
        md += f"**Patient ID:** {patient_id}  \n"
        md += f"**Report Date:** {now_str}  \n\n"

        if profile:
            demographics = []
            if getattr(profile, "date_of_birth", None):
                demographics.append(f"DOB: {profile.date_of_birth}")
            if getattr(profile, "biological_sex", None):
                demographics.append(f"Sex: {profile.biological_sex}")
            if demographics:
                md += f"**Demographics:** {', '.join(demographics)}  \n\n"

        md += "## Health Timeline Summary\n"
        if summary and summary.overall_summary and summary.overall_summary.strip():
            md += f"{summary.overall_summary.strip()}\n\n"
        elif entries:
            latest = entries[-1]
            md += f"Latest assessment recorded: Severity **{latest.severity}**.\n\n"
        else:
            md += "No prior clinical assessments recorded.\n\n"

        md += "## Clinical Findings & Conditions\n"
        if summary and summary.condition_summary and summary.condition_summary.strip() and summary.condition_summary != "Condition confidence stable.":
            md += f"{summary.condition_summary.strip()}\n\n"
        elif entries:
            latest = entries[-1]
            cond = latest.top_condition or (", ".join(latest.possible_conditions) if latest.possible_conditions else None)
            if cond:
                md += f"Evaluated Condition: {cond} (Severity: {latest.severity})\n\n"
            if latest.symptoms:
                md += f"Documented Symptoms: {', '.join(latest.symptoms)}\n\n"
        else:
            md += "No acute medical conditions documented in history.\n\n"

        md += "## Follow-up Guidance & Recommendations\n"
        if summary and getattr(summary, "recommendation_summary", None) and summary.recommendation_summary.strip():
            md += f"- {summary.recommendation_summary.strip()}\n"
        elif entries and entries[-1].recommendation:
            md += f"- {entries[-1].recommendation.strip()}\n"
        else:
            md += "- Consult with a certified clinician for further medical evaluation.\n"

        md += "\n---\n*Disclaimer: AURA is an AI-powered clinical intake and decision support tool, not a diagnostic doctor. Always consult a healthcare professional for emergencies or medical decisions.*\n"
        return md
    except Exception as e:
        return f"# Clinical Report\n\nUnable to generate report: {str(e)}"

def _build_pdf(title: str, lines: list[str]) -> bytes:
    """Generates a genuine valid PDF 1.4 document without external dependencies."""
    content = "BT\n/F1 16 Tf\n50 740 Td\n(" + title.replace("(", "").replace(")", "") + ") Tj\n/F1 10 Tf\n0 -28 Td\n"
    for line in lines[:45]:
        clean = line.replace("(", "").replace(")", "").replace("\t", " ")
        content += "(" + clean[:85] + ") Tj\n0 -14 Td\n"
    content += "ET"
    stream = content.encode("latin1", "replace")

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    offsets = []
    offsets.append(len(pdf))
    pdf.extend(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    offsets.append(len(pdf))
    pdf.extend(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    offsets.append(len(pdf))
    pdf.extend(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n")
    offsets.append(len(pdf))
    pdf.extend(f"4 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("latin1") + stream + b"\nendstream\nendobj\n")
    offsets.append(len(pdf))
    pdf.extend(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)+1}\n0000000000 65535 f \n".encode("latin1"))
    for o in offsets:
        pdf.extend(f"{o:010d} 00000 n \n".encode("latin1"))
    pdf.extend(f"trailer\n<< /Size {len(offsets)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin1"))
    return bytes(pdf)

@router.get("/markdown")
async def export_markdown(patient_id: str, session: Session = Depends(get_auth_session)):
    md_content = generate_markdown(patient_id)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="aura_report_{patient_id}.md"'}
    )

@router.get("/pdf")
async def export_pdf(patient_id: str, session: Session = Depends(get_auth_session)):
    md_content = generate_markdown(patient_id)
    lines = [l.strip() for l in md_content.splitlines() if l.strip()]
    pdf_bytes = _build_pdf("AURA Clinical Summary Report", lines)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="aura_report_{patient_id}.pdf"'}
    )

