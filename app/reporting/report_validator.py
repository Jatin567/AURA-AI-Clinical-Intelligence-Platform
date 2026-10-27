from app.reporting.models import ClinicalReport
from typing import List


class ReportValidationError(Exception):
    """Exception raised for errors in the report validation."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


class ReportValidator:
    """
    Validates logical consistency of the ClinicalReport.
    Ensures no missing mandatory sections and valid states based on severity and confidence.
    """

    @classmethod
    def validate(cls, report: ClinicalReport) -> None:
        errors: List[str] = []

        # 1. Required sections must never be empty (null or conceptually empty)
        if not report.metadata:
            errors.append("Report metadata is missing.")
        if not report.patient_summary:
            errors.append("Patient summary is missing.")
        if not report.clinical_reasoning_summary:
            errors.append("Clinical reasoning summary is missing.")
        if not report.clinical_disclaimer:
            errors.append("Clinical disclaimer is missing.")
        if not report.audit_metadata:
            errors.append("Audit metadata is missing.")
        if not report.severity:
            errors.append("Severity is missing.")
        
        # 2. Reports must contain at least one possible condition.
        if not report.possible_conditions:
            errors.append("Report must contain at least one possible condition.")

        # 3. EMERGENCY reports must include at least one safety notice.
        if report.severity.upper() == "EMERGENCY" and not report.safety_notices:
            errors.append("EMERGENCY reports must include at least one safety notice.")

        # 4. Reports with high-confidence conditions must include supporting findings.
        for condition in report.possible_conditions:
            if condition.confidence >= 0.8 and not condition.supporting_findings:
                errors.append(f"High-confidence condition '{condition.condition_name}' must include supporting findings.")

        # Let's ensure basic sanity on missing information isn't strictly required to be non-empty,
        # since it's normal for there to be no missing information.
        
        if errors:
            raise ReportValidationError(errors)
