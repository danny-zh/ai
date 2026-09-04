"""Password hashing helpers."""

from passlib.context import CryptContext


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt.

    Args:
        password: Plaintext password to hash.

    Returns:
        Bcrypt password hash.
    """
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        password: Candidate plaintext password.
        password_hash: Stored bcrypt password hash.

    Returns:
        Whether the password matches the hash.
    """
    try:
        return password_context.verify(password, password_hash)
    except (TypeError, ValueError):
        return False