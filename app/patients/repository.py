import abc
from typing import List, Optional
from app.patients.models import UserAccount, PatientProfile, Identity, Session

class IdentityRepository(abc.ABC):
    @abc.abstractmethod
    def save_identity(self, identity: Identity) -> None: pass
    
    @abc.abstractmethod
    def get_identity_by_email(self, email: str) -> Optional[Identity]: pass
    
    @abc.abstractmethod
    def save_user(self, user: UserAccount) -> None: pass
    
    @abc.abstractmethod
    def get_user(self, user_id: str) -> Optional[UserAccount]: pass

class PatientRepository(abc.ABC):
    @abc.abstractmethod
    def save_profile(self, profile: PatientProfile) -> None: pass
    
    @abc.abstractmethod
    def get_profile(self, patient_id: str) -> Optional[PatientProfile]: pass
    
    @abc.abstractmethod
    def get_profiles_by_user(self, user_id: str) -> List[PatientProfile]: pass

class SessionRepository(abc.ABC):
    @abc.abstractmethod
    def save_session(self, session: Session) -> None: pass
    
    @abc.abstractmethod
    def get_session(self, session_id: str) -> Optional[Session]: pass
    
    @abc.abstractmethod
    def revoke_session(self, session_id: str) -> None: pass


# In-Memory Implementations for Phase 1

class InMemoryIdentityRepository(IdentityRepository):
    def __init__(self):
        self._identities = {}
        self._users = {}

    def save_identity(self, identity: Identity) -> None:
        self._identities[identity.email] = identity

    def get_identity_by_email(self, email: str) -> Optional[Identity]:
        return self._identities.get(email)

    def save_user(self, user: UserAccount) -> None:
        self._users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[UserAccount]:
        return self._users.get(user_id)


class InMemoryPatientRepository(PatientRepository):
    def __init__(self):
        self._profiles = {}

    def save_profile(self, profile: PatientProfile) -> None:
        self._profiles[profile.patient_id] = profile

    def get_profile(self, patient_id: str) -> Optional[PatientProfile]:
        return self._profiles.get(patient_id)

    def get_profiles_by_user(self, user_id: str) -> List[PatientProfile]:
        return [p for p in self._profiles.values() if p.user_id == user_id]


class InMemorySessionRepository(SessionRepository):
    def __init__(self):
        self._sessions = {}

    def save_session(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def revoke_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id].is_active = False

import os
import json
import threading

class FileBasedIdentityRepository(IdentityRepository):
    def __init__(self, directory: str = "app/data/identities"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self._lock = threading.Lock()

    def _get_identity_path(self, email: str) -> str:
        return os.path.join(self.directory, f"id_{email}.json")
        
    def _get_user_path(self, user_id: str) -> str:
        return os.path.join(self.directory, f"user_{user_id}.json")

    def save_identity(self, identity: Identity) -> None:
        with self._lock:
            with open(self._get_identity_path(identity.email), "w") as f:
                f.write(identity.model_dump_json())

    def get_identity_by_email(self, email: str) -> Optional[Identity]:
        with self._lock:
            path = self._get_identity_path(email)
            if not os.path.exists(path):
                return None
            try:
                with open(path, "r") as f:
                    return Identity.model_validate_json(f.read())
            except Exception:
                return None

    def save_user(self, user: UserAccount) -> None:
        with self._lock:
            with open(self._get_user_path(user.user_id), "w") as f:
                f.write(user.model_dump_json())

    def get_user(self, user_id: str) -> Optional[UserAccount]:
        with self._lock:
            path = self._get_user_path(user_id)
            if not os.path.exists(path):
                return None
            try:
                with open(path, "r") as f:
                    return UserAccount.model_validate_json(f.read())
            except Exception:
                return None

class FileBasedPatientRepository(PatientRepository):
    def __init__(self, directory: str = "app/data/patients"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self._lock = threading.Lock()

    def _get_path(self, patient_id: str) -> str:
        return os.path.join(self.directory, f"{patient_id}.json")

    def save_profile(self, profile: PatientProfile) -> None:
        with self._lock:
            with open(self._get_path(profile.patient_id), "w") as f:
                f.write(profile.model_dump_json())

    def get_profile(self, patient_id: str) -> Optional[PatientProfile]:
        with self._lock:
            path = self._get_path(patient_id)
            if not os.path.exists(path):
                return None
            try:
                with open(path, "r") as f:
                    return PatientProfile.model_validate_json(f.read())
            except Exception:
                return None

    def get_profiles_by_user(self, user_id: str) -> List[PatientProfile]:
        with self._lock:
            profiles = []
            for filename in os.listdir(self.directory):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.directory, filename), "r") as f:
                            p = PatientProfile.model_validate_json(f.read())
                            if p.user_id == user_id:
                                profiles.append(p)
                    except Exception:
                        pass
            return profiles

class FileBasedSessionRepository(SessionRepository):
    def __init__(self, directory: str = "app/data/sessions"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self._lock = threading.Lock()

    def _get_path(self, session_id: str) -> str:
        return os.path.join(self.directory, f"{session_id}.json")

    def save_session(self, session: Session) -> None:
        with self._lock:
            with open(self._get_path(session.session_id), "w") as f:
                f.write(session.model_dump_json())

    def get_session(self, session_id: str) -> Optional[Session]:
        with self._lock:
            path = self._get_path(session_id)
            if not os.path.exists(path):
                return None
            try:
                with open(path, "r") as f:
                    return Session.model_validate_json(f.read())
            except Exception:
                return None

    def revoke_session(self, session_id: str) -> None:
        with self._lock:
            path = self._get_path(session_id)
            if not os.path.exists(path):
                return
            try:
                with open(path, "r") as f:
                    session = Session.model_validate_json(f.read())
                session.is_active = False
                with open(path, "w") as f:
                    f.write(session.model_dump_json())
            except Exception:
                pass
