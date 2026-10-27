from typing import Optional
from app.patients.profile_service import ProfileService
from app.timeline.timeline_engine import TimelineEngine
from app.workspace.workspace_service import WorkspaceService
from app.conversations.service import ConversationService

class MemoryService:
    """
    Constructs contextual memory for the AI Orchestrator by aggregating:
    - Short-term Conversation Memory
    - Long-term Patient Memory (Profile)
    - Timeline Context
    - Workspace Context
    """
    def __init__(
        self, 
        profile_service: ProfileService,
        timeline_engine: TimelineEngine,
        workspace_service: WorkspaceService,
        conversation_service: ConversationService
    ):
        self.profile_service = profile_service
        self.timeline_engine = timeline_engine
        self.workspace_service = workspace_service
        self.conversation_service = conversation_service

    def build_prompt_context(self, user_id: str, patient_id: str, conversation_id: Optional[str] = None) -> str:
        # 1. Fetch Long-Term Patient Profile
        profile = None
        for p in self.profile_service.get_profiles_for_user(user_id):
            if p.patient_id == patient_id:
                profile = p
                break
        
        # 2. Fetch Timeline Data
        try:
            entries = self.timeline_engine.get_patient_timeline(patient_id)
            timeline = self.timeline_engine.generate_summary(patient_id) if entries else None
        except Exception:
            timeline = None

        # 3. Compile context string
        context = "=== PATIENT MEDICAL CONTEXT ===\n"
        if profile:
            context += f"Name: {profile.full_name}\n"
            context += f"Age/DOB: {profile.date_of_birth}\n"
            context += f"Sex: {profile.biological_sex}\n"
            context += f"Known Conditions: {', '.join(profile.medical_history.chronic_conditions)}\n"
            context += f"Medications: {', '.join(profile.medications.current_medications)}\n"
            context += f"Allergies: {', '.join(profile.allergies.allergies)}\n"
        else:
            context += "No detailed profile found.\n"

        context += "\n=== TIMELINE SUMMARY ===\n"
        if timeline:
            context += f"Overall Health: {timeline.overall_summary or 'None'}\n"
            context += f"Recent Conditions: {timeline.condition_summary or 'None'}\n"
        else:
            context += "No timeline data available.\n"

        # 4. We do not inject raw Workspace objects, as they contain deep technical reasoning details,
        # but the orchestrator knows the workspace is driven by the Timeline/Assessment engines.
        
        return context

    def get_conversation_history(self, conversation_id: str, max_messages: int = 10) -> list:
        """Returns the most recent messages for short-term memory context."""
        conversation = self.conversation_service.get_conversation(conversation_id)
        if not conversation:
            return []
        
        # Return last N messages
        recent = conversation.messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent]
