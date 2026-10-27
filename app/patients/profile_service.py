import uuid
from typing import List, Optional
from app.patients.models import PatientProfile
from app.patients.repository import PatientRepository
from app.patients.validators import ProfileValidator

class ProfileService:
    """
    Manages patient profiles and enforces business rules.
    """
    def __init__(self, repository: PatientRepository):
        self.repository = repository

    def create_profile(self, profile: PatientProfile) -> PatientProfile:
        ProfileValidator.validate(profile)
        self.repository.save_profile(profile)
        return profile

    def update_profile(self, profile: PatientProfile) -> PatientProfile:
        ProfileValidator.validate(profile)
        # Assuming the caller has updated the `updated_at` field, 
        # or we could force it here. We'll rely on the caller or just save it.
        self.repository.save_profile(profile)
        return profile

    def get_profile(self, patient_id: str) -> Optional[PatientProfile]:
        return self.repository.get_profile(patient_id)

    def get_profiles_for_user(self, user_id: str) -> List[PatientProfile]:
        return self.repository.get_profiles_by_user(user_id)
