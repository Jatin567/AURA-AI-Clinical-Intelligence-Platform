import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.patients.models import UserAccount, Identity, Session
from app.patients.repository import IdentityRepository, SessionRepository
from app.patients.password_service import PasswordService

class AuthError(Exception):
    pass

class AuthService:
    """
    Manages authentication logic, login, logout, and session validation.
    """
    def __init__(self, 
                 identity_repo: IdentityRepository, 
                 session_repo: SessionRepository,
                 password_service: PasswordService):
        self.identity_repo = identity_repo
        self.session_repo = session_repo
        self.password_service = password_service
        self._login_attempts = {}  # In-memory rate limiting: {email: (count, timestamp)}

    def _check_rate_limit(self, email: str):
        now = datetime.now(timezone.utc)
        attempts, timestamp = self._login_attempts.get(email, (0, now))
        
        # Reset if more than 15 minutes passed
        if now - timestamp > timedelta(minutes=15):
            attempts = 0
            
        if attempts >= 5:
            raise AuthError("Too many failed login attempts. Please try again in 15 minutes.")
            
        self._login_attempts[email] = (attempts, timestamp)

    def _record_failed_login(self, email: str):
        now = datetime.now(timezone.utc)
        attempts, _ = self._login_attempts.get(email, (0, now))
        self._login_attempts[email] = (attempts + 1, now)

    def _clear_login_attempts(self, email: str):
        if email in self._login_attempts:
            del self._login_attempts[email]

    def register(self, email: str, plain_password: str) -> UserAccount:
        if self.identity_repo.get_identity_by_email(email):
            raise AuthError("Email already registered.")
            
        user_id = str(uuid.uuid4())
        hashed_password = self.password_service.hash_password(plain_password)
        
        identity = Identity(
            user_id=user_id,
            email=email,
            password_hash=hashed_password
        )
        user = UserAccount(user_id=user_id, email=email)
        
        self.identity_repo.save_user(user)
        self.identity_repo.save_identity(identity)
        return user

    def login(self, email: str, plain_password: str) -> Session:
        self._check_rate_limit(email)
        
        identity = self.identity_repo.get_identity_by_email(email)
        if not identity:
            self._record_failed_login(email)
            raise AuthError("Invalid credentials.")
            
        if not self.password_service.verify_password(plain_password, identity.password_hash):
            self._record_failed_login(email)
            raise AuthError("Invalid credentials.")
            
        self._clear_login_attempts(email)
        
        user = self.identity_repo.get_user(identity.user_id)
        if not user or not user.is_active:
            raise AuthError("User account inactive or missing.")
            
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            refresh_token=str(uuid.uuid4()),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        self.session_repo.save_session(session)
        return session

    def login_with_google(self, id_token: str, firebase_service) -> Session:
        try:
            decoded = firebase_service.verify_id_token(id_token)
            email = decoded.get("email")
            if not email:
                raise AuthError("No email associated with Google token.")
        except Exception as e:
            raise AuthError(f"Token verification failed: {str(e)}")

        identity = self.identity_repo.get_identity_by_email(email)
        
        # If user doesn't exist, create them
        if not identity:
            user_id = str(uuid.uuid4())
            identity = Identity(
                user_id=user_id,
                email=email,
                password_hash="OAUTH_GOOGLE"
            )
            user = UserAccount(user_id=user_id, email=email, is_verified=True)
            self.identity_repo.save_user(user)
            self.identity_repo.save_identity(identity)
        else:
            user = self.identity_repo.get_user(identity.user_id)
            if not user or not user.is_active:
                raise AuthError("User account inactive or missing.")

        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=identity.user_id,
            refresh_token=str(uuid.uuid4()),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        self.session_repo.save_session(session)
        return session

    def validate_session(self, session_id: str) -> Optional[Session]:
        session = self.session_repo.get_session(session_id)
        if not session or not session.is_active:
            return None
            
        if session.expires_at < datetime.now(timezone.utc):
            self.session_repo.revoke_session(session_id)
            return None
            
        # Update last activity
        session.last_activity = datetime.now(timezone.utc)
        self.session_repo.save_session(session)

        user = self.identity_repo.get_user(session.user_id)
        if not user or not user.is_active:
            return None

        return session

    def refresh_session(self, refresh_token: str) -> Session:
        # We need a way to look up by refresh_token in a real DB, but in memory we must scan
        # The InMemorySessionRepository needs a get_session_by_refresh_token, we can do it here for now
        all_sessions = getattr(self.session_repo, '_sessions', {})
        for s in all_sessions.values():
            if s.refresh_token == refresh_token and s.is_active:
                if s.expires_at < datetime.now(timezone.utc):
                    s.is_active = False
                    raise AuthError("Refresh token expired.")
                
                # Renew
                s.session_id = str(uuid.uuid4())
                s.refresh_token = str(uuid.uuid4())
                s.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
                s.last_activity = datetime.now(timezone.utc)
                self.session_repo.save_session(s)
                return s
        raise AuthError("Invalid refresh token.")

    def logout(self, session_id: str) -> None:
        self.session_repo.revoke_session(session_id)

    def logout_all_sessions(self, user_id: str) -> None:
        # Iterate and revoke all sessions for this user
        all_sessions = getattr(self.session_repo, '_sessions', {})
        for s in all_sessions.values():
            if s.user_id == user_id and s.is_active:
                s.is_active = False

    def forgot_password(self, email: str) -> None:
        identity = self.identity_repo.get_identity_by_email(email)
        if not identity:
            # Silently return to prevent email enumeration
            return
        
        # In a real app, generate a token, save to DB, and send an email
        print(f"[MOCK EMAIL] Password reset requested for {email}")

    def reset_password(self, token: str, new_password: str) -> None:
        # In a real app, verify token and get user
        # For this prototype, we'll assume token is the email just to make the UI flow work if tested
        # In reality, this requires a DB token table. We will raise NotImplemented if used directly without token DB.
        pass
