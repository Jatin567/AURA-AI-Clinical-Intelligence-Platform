from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Dict, Any

from app.patients.models import Session
from app.api.dependencies import get_auth_session, file_pipeline

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload")
async def upload_file(
    patient_id: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_auth_session)
) -> Dict[str, Any]:
    try:
        file_bytes = await file.read()
        result = file_pipeline.process_file(
            patient_id=patient_id,
            filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
