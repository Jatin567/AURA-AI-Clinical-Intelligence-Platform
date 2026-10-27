from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.patients.models import Session
from app.api.dependencies import timeline_engine, get_auth_session
from app.timeline.models import TimelineSummary

router = APIRouter(tags=["timeline"])

@router.get("/timeline/{patient_id}", response_model=TimelineSummary)
async def get_patient_timeline(
    patient_id: str,
    session: Session = Depends(get_auth_session)
):
    try:
        # In a real app we'd check if the user is authorized for this patient
        summary = timeline_engine.generate_summary(patient_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
