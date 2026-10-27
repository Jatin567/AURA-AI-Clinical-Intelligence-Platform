from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class IntakeStage(str, Enum):
    DEMOGRAPHICS = "demographics"
    SYMPTOMS = "symptoms"
    HISTORY = "history"
    COMPLETE = "complete"


class PatientProfile(BaseModel):
    age: Optional[int] = None
    age_in_days: Optional[int] = None
    sex: Optional[str] = None
    is_infant: Optional[bool] = None
    known_conditions: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)

    @property
    def is_neonate(self) -> bool:
        """True if age is 0 and age_in_days is 28 or less (or missing)."""
        return self.age == 0 and (self.age_in_days is None or self.age_in_days <= 28)


class SessionState(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str
    created_at: datetime
    expires_at: datetime
    last_modified_at: Optional[datetime] = None
    intake_stage: IntakeStage = IntakeStage.DEMOGRAPHICS
    patient_profile: PatientProfile = Field(default_factory=PatientProfile)
    chief_complaint: Optional[str] = None
    symptom_duration: Optional[str] = None
    symptom_severity: Optional[int] = None
    symptoms: List[str] = Field(default_factory=list)
    red_flags_detected: List[str] = Field(default_factory=list)
    triage_result: Optional[dict] = None
    conversation_history: List[dict] = Field(default_factory=list, max_length=100)
