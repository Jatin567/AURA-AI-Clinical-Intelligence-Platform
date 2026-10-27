from app.patients.models import PatientProfile
from app.workspace.models import WorkspacePatientSummary

class PatientAdapter:
    """Adapts PatientProfile into WorkspacePatientSummary."""
    
    @staticmethod
    def adapt(profile: PatientProfile) -> WorkspacePatientSummary:
        return WorkspacePatientSummary(
            full_name=profile.full_name,
            date_of_birth=profile.date_of_birth.isoformat() if profile.date_of_birth else "",
            biological_sex=profile.biological_sex,
            chronic_conditions=profile.medical_history.chronic_conditions.copy(),
            allergies=profile.allergies.allergies.copy(),
            current_medications=profile.medications.current_medications.copy()
        )
