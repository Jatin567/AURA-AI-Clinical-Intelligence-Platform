from datetime import date
from typing import List
from app.patients.models import PatientProfile

class ProfileValidationError(Exception):
    pass

class ProfileValidator:
    """
    Ensures data integrity for patient profiles.
    """
    
    VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}

    @classmethod
    def validate(cls, profile: PatientProfile) -> None:
        errors: List[str] = []

        # DOB must be in the past
        if profile.date_of_birth > date.today():
            errors.append("Date of birth must be in the past.")

        # Height/weight must be positive
        if profile.height is not None and profile.height <= 0:
            errors.append("Height must be positive.")
        if profile.weight is not None and profile.weight <= 0:
            errors.append("Weight must be positive.")

        # Blood group must be valid
        if profile.blood_group and profile.blood_group.upper() not in cls.VALID_BLOOD_GROUPS:
            errors.append(f"Invalid blood group: {profile.blood_group}. Must be one of {cls.VALID_BLOOD_GROUPS}.")

        # Reject duplicate medications
        meds = profile.medications.current_medications
        if len(meds) != len(set(meds)):
            errors.append("Duplicate medications found.")

        # Reject duplicate allergies
        allergies = profile.allergies.allergies
        if len(allergies) != len(set(allergies)):
            errors.append("Duplicate allergies found.")

        # Emergency contact consistency
        if profile.emergency_contact:
            if not profile.emergency_contact.name or not profile.emergency_contact.phone:
                errors.append("Emergency contact must have a name and phone number.")

        if errors:
            raise ProfileValidationError("\n".join(errors))
