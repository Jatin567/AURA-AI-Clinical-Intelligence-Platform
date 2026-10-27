from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.patients.models import Session
from app.api.dependencies import workspace_service, get_auth_session
from app.workspace.models import Workspace
from app.reporting.models import ClinicalReport
from app.explanation.models import ClinicalExplanation

# Reconstruct models from dicts saved in the redis session
from app.api.schemas import AnswerResponse # placeholder

router = APIRouter(tags=["workspace"])

@router.post("/workspace/{patient_id}/build", response_model=Workspace)
async def build_workspace(
    patient_id: str,
    payload: dict,
    session: Session = Depends(get_auth_session)
):
    """
    Builds the workspace projection for a given patient.
    Requires current_report and current_explanation provided by the client,
    or fetched from the active redis session.
    For simplicity in this phase, we accept them in the payload.
    """
    try:
        current_report_data = payload.get("current_report")
        current_explanation_data = payload.get("current_explanation")
        
        if not current_report_data or not current_explanation_data:
            raise HTTPException(status_code=400, detail="Missing report or explanation data")

        # In a real system, these would be fetched from a persistent store or the redis session
        # using the session ID. We parse them here.
        report = ClinicalReport.model_validate(current_report_data)
        explanation = ClinicalExplanation.model_validate(current_explanation_data)

        workspace = workspace_service.build_workspace(
            patient_id=patient_id,
            current_report=report,
            current_explanation=explanation
        )
        return workspace
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
