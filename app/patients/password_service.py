import abc
import bcrypt

class PasswordService(abc.ABC):
    """
    Interface for secure, deterministic password hashing and verification.
    """
    
    @abc.abstractmethod
    def hash_password(self, plain_password: str) -> str:
        pass

    @abc.abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass


class BcryptPasswordService(PasswordService):
    """
    Bcrypt implementation using the bcrypt library directly.
    """
    
    def hash_password(self, plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
