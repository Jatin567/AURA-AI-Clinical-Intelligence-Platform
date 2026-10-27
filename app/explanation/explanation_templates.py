from app.models.triage import TriageLevel


DIAGNOSIS_NOTICE = "This is not a confirmed diagnosis."

NO_CONDITION_SUMMARY = (
    "The available information does not identify a clear leading possible "
    "condition. Additional clinical information may improve confidence."
)

LEADING_CONDITION_SUMMARY = (
    "The available information suggests that {condition_name} is currently "
    "the leading possible condition. This is not a confirmed diagnosis."
)

CONDITION_WITH_EVIDENCE = (
    "{condition_name} has a confidence score of {confidence_percent}%. "
    "This estimate is based on supporting findings including {supporting}. "
    "Conflicting findings include {conflicting}."
)

CONDITION_WITHOUT_CONFLICTS = (
    "{condition_name} has a confidence score of {confidence_percent}%. "
    "This estimate is based on supporting findings including {supporting}. "
    "No conflicting findings were identified in the available information."
)

CONDITION_WITHOUT_SUPPORT = (
    "{condition_name} has a confidence score of {confidence_percent}%. "
    "The deterministic reasoning output did not list specific supporting "
    "findings for this condition."
)

RISK_EXPLANATION = (
    "{factor_name} may affect clinical risk because {description} "
    "Risk weight: {risk_weight}."
)

MISSING_INFORMATION = (
    "{field_name}: {clinical_relevance} Impact on reasoning: {impact_on_reasoning}"
)

RECOMMENDATION_TEMPLATES = {
    TriageLevel.EMERGENCY: {
        "severity": "EMERGENCY",
        "title": "Seek Emergency Care Immediately",
        "action": "Call emergency services or go to the nearest emergency department now. Do not drive yourself if symptoms are severe.",
        "timeframe": "Now",
        "rationale": "The authoritative severity classifier marked this presentation as emergency-level.",
        "priority": 1,
    },
    TriageLevel.URGENT: {
        "severity": "URGENT",
        "title": "Seek Prompt Medical Care",
        "action": "Contact a doctor, urgent care clinic, or local medical advice line today.",
        "timeframe": "Within 24 hours",
        "rationale": "The authoritative severity classifier marked this presentation as requiring prompt evaluation.",
        "priority": 2,
    },
    TriageLevel.ROUTINE: {
        "severity": "ROUTINE",
        "title": "Schedule a Clinical Appointment",
        "action": "Schedule an appointment with a healthcare professional and monitor symptoms for changes.",
        "timeframe": "Routine appointment",
        "rationale": "The authoritative severity classifier marked this presentation as appropriate for routine follow-up.",
        "priority": 3,
    },
    TriageLevel.HOME_CARE: {
        "severity": "SELF_CARE",
        "title": "Self Care With Monitoring",
        "action": "Rest, stay hydrated, monitor symptoms, and seek care if symptoms worsen or new red flags appear.",
        "timeframe": "Self care with reassessment if symptoms change",
        "rationale": "The authoritative severity classifier marked this presentation as suitable for home care monitoring.",
        "priority": 4,
    },
}

SAFETY_NOTICE_TEMPLATES = {
    TriageLevel.EMERGENCY: {
        "severity": "EMERGENCY",
        "title": "Emergency Warning",
        "message": "This assessment indicates possible emergency-level symptoms. Seek emergency care immediately.",
        "immediate_action_required": True,
    },
    TriageLevel.URGENT: {
        "severity": "URGENT",
        "title": "Urgent Care Notice",
        "message": "This assessment indicates symptoms that should be reviewed by a healthcare professional promptly.",
        "immediate_action_required": False,
    },
}

DISCLAIMER = {
    "informational_only": "This explanation is for informational purposes only.",
    "not_a_diagnosis": "This is not a diagnosis and does not confirm or rule out any condition.",
    "seek_professional_care": "Seek care from a qualified healthcare professional for medical concerns, and contact emergency services for urgent or life-threatening symptoms.",
}

