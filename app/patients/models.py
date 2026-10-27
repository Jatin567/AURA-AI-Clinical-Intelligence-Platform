from datetime import datetime, date, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

class Identity(BaseModel):
    """Stores authentication credentials/provider details."""
    user_id: str
    email: str
    password_hash: str
    provider: str = "local"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserAccount(BaseModel):
    """Represents the authenticated user account, which can own multiple PatientProfiles."""
    user_id: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    is_verified: bool = False

class Session(BaseModel):
    """Tracks active user sessions."""
    session_id: str
    user_id: str
    refresh_token: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str

class MedicalHistory(BaseModel):
    chronic_conditions: List[str] = Field(default_factory=list)
    previous_surgeries: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    smoking_status: Optional[str] = None
    alcohol_use: Optional[str] = None
    pregnancy_status: Optional[str] = None
    vaccination_status: List[str] = Field(default_factory=list)

class MedicationList(BaseModel):
    current_medications: List[str] = Field(default_factory=list)

class AllergyList(BaseModel):
    allergies: List[str] = Field(default_factory=list)

class PatientProfile(BaseModel):
    """The patient profile, one UserAccount can own multiple profiles."""
    patient_id: str
    user_id: str
    full_name: str
    date_of_birth: date
    biological_sex: str
    height: Optional[float] = None  # in cm
    weight: Optional[float] = None  # in kg
    blood_group: Optional[str] = None
    preferred_language: str = "en"
    
    emergency_contact: Optional[EmergencyContact] = None
    medical_history: MedicalHistory = Field(default_factory=MedicalHistory)
    medications: MedicationList = Field(default_factory=MedicationList)
    allergies: AllergyList = Field(default_factory=AllergyList)

    profile_version: str = "1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
