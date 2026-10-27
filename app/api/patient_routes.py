from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from app.patients.models import UserAccount, PatientProfile, Session
from app.api.dependencies import auth_service, profile_service, get_auth_session
from app.patients.auth_service import AuthError

router = APIRouter(tags=["patients"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str

class SessionResponse(BaseModel):
    session_id: str
    refresh_token: Optional[str] = None

class GoogleLoginRequest(BaseModel):
    token: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/auth/register", response_model=SessionResponse)
async def register(req: RegisterRequest):
    try:
        user = auth_service.register(req.email, req.password)
        session = auth_service.login(req.email, req.password)
        return SessionResponse(session_id=session.session_id, refresh_token=session.refresh_token)
    except (ValueError, AuthError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.post("/auth/login", response_model=SessionResponse)
async def login(req: LoginRequest):
    try:
        session = auth_service.login(req.email, req.password)
        return SessionResponse(session_id=session.session_id, refresh_token=session.refresh_token)
    except (ValueError, AuthError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.post("/auth/google", response_model=SessionResponse)
async def login_google(req: GoogleLoginRequest):
    from app.api.dependencies import firebase_service
    try:
        session = auth_service.login_with_google(req.token, firebase_service)
        return SessionResponse(session_id=session.session_id, refresh_token=session.refresh_token)
    except (ValueError, AuthError) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    try:
        auth_service.forgot_password(req.email)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.post("/auth/reset-password")
async def reset_password(req: ResetPasswordRequest):
    try:
        auth_service.reset_password(req.token, req.new_password)
        return {"status": "ok"}
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

class VerifyEmailRequest(BaseModel):
    token: str

@router.post("/auth/verify-email")
async def verify_email(req: VerifyEmailRequest):
    # Mock endpoint for development
    return {"status": "ok"}

@router.post("/auth/refresh", response_model=SessionResponse)
async def refresh_session(req: RefreshRequest):
    try:
        session = auth_service.refresh_session(req.refresh_token)
        return SessionResponse(session_id=session.session_id, refresh_token=session.refresh_token)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.post("/auth/logout")
async def logout(session: Session = Depends(get_auth_session)):
    try:
        auth_service.logout(session.session_id)
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

@router.delete("/auth/logout-all")
async def logout_all(session: Session = Depends(get_auth_session)):
    try:
        auth_service.logout_all_sessions(session.user_id)
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")

@router.get("/auth/me")
async def auth_me(session: Session = Depends(get_auth_session)):
    return {"user_id": session.user_id, "is_active": session.is_active}

@router.get("/patients/me", response_model=List[PatientProfile])
async def get_me(session: Session = Depends(get_auth_session)):
    profiles = profile_service.get_profiles_for_user(session.user_id)
    return profiles
