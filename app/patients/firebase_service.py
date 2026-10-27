import os
from typing import Dict, Any

from app.config import settings

class FirebaseService:
    def __init__(self):
        self._initialized = False
        self._initialization_attempted = False

    def _initialize_app(self):
        if self._initialization_attempted:
            return

        self._initialization_attempted = True
        firebase_admin, credentials, _ = self._get_firebase_modules()
        try:
            # Check if default app is already initialized
            firebase_admin.get_app()
            self._initialized = True
            return
        except ValueError:
            pass

        cred_path = settings.FIREBASE_CREDENTIALS_PATH or os.getenv("FIREBASE_CREDENTIALS_PATH")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            self._initialized = True
        else:
            print("WARNING: FIREBASE_CREDENTIALS_PATH not set or file not found. Google Sign-In will operate in MOCK mode.")
            self._initialized = False

    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verifies the Firebase ID token.
        """
        self._initialize_app()
        if not self._initialized:
            raise Exception("Google authentication is not configured on the backend.")

        try:
            _, _, auth = self._get_firebase_modules()
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            raise Exception(f"Firebase token verification failed: {str(e)}")

    @staticmethod
    def _get_firebase_modules():
        import firebase_admin
        from firebase_admin import credentials, auth

        return firebase_admin, credentials, auth
