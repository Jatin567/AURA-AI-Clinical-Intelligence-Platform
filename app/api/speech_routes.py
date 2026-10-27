from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any

from app.patients.models import Session
from app.api.dependencies import get_auth_session, speech_service

router = APIRouter(prefix="/speech", tags=["speech"])

@router.post("/transcribe")
async def transcribe_speech(
    audio: UploadFile = File(...),
    session: Session = Depends(get_auth_session)
) -> Dict[str, Any]:
    try:
        audio_bytes = await audio.read()
        result = await speech_service.transcribe_audio(audio_bytes, audio.content_type)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {str(e)}")
