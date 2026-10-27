from app.patients.repository import FileBasedIdentityRepository, FileBasedSessionRepository, FileBasedPatientRepository
from app.patients.password_service import BcryptPasswordService
from app.patients.auth_service import AuthService
from app.patients.profile_service import ProfileService

from app.timeline.timeline_repository import FileBasedTimelineRepository
from app.timeline.timeline_engine import TimelineEngine
from app.workspace.workspace_service import WorkspaceService
from app.patients.firebase_service import FirebaseService
from app.conversations.repository import FileBasedConversationRepository
from app.conversations.service import ConversationService
from app.memory.service import MemoryService
from app.orchestrator.events import EventBus

from app.file_processing.pipeline import FileProcessingPipeline
from app.speech.service import SpeechService

# Global shared repositories
identity_repo = FileBasedIdentityRepository()
session_repo = FileBasedSessionRepository()
patient_repo = FileBasedPatientRepository()
password_service = BcryptPasswordService()
firebase_service = FirebaseService()
conversation_repo = FileBasedConversationRepository()

timeline_repo = FileBasedTimelineRepository()

event_bus = EventBus()

# Global shared services
auth_service = AuthService(identity_repo, session_repo, password_service)
profile_service = ProfileService(patient_repo)
conversation_service = ConversationService(conversation_repo)

timeline_engine = TimelineEngine(timeline_repo)
workspace_service = WorkspaceService(profile_service, timeline_engine)

memory_service = MemoryService(profile_service, timeline_engine, workspace_service, conversation_service)
from app.orchestrator.service import orchestrator_service
from app.orchestrator.gateway import ConversationGateway

conversation_gateway = ConversationGateway()
file_pipeline = FileProcessingPipeline(timeline_engine, workspace_service)
speech_service = SpeechService(provider="whisper")

def on_assessment_completed(payload: dict):
    if "patient_id" in payload and "report" in payload:
        timeline_engine.add_assessment(payload["patient_id"], payload["report"])

event_bus.subscribe("AssessmentCompleted", on_assessment_completed)

from fastapi import HTTPException, status, Header
from typing import Optional

def get_auth_session(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization")
    token = authorization.replace("Bearer ", "")
    session = auth_service.validate_session(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return session
