"""Database-backed user account operations."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.backend.models.orm import UserRecord
from app.backend.models.user import UserRegistrationRequest, UserUpdateRequest
from app.backend.security.passwords import hash_password, verify_password
from app.backend.services.errors import DuplicateUserError, ResourceNotFoundError


class UserService:
    """Manage user accounts through a SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        """Initialize the service.

        Args:
            session: Open database session used by service methods.
        """
        self.session = session

    def register(self, payload: UserRegistrationRequest) -> UserRecord:
        """Create an account with a bcrypt password hash.

        Args:
            payload: Validated registration request.

        Returns:
            Newly persisted user record.

        Raises:
            DuplicateUserError: If username or email already exists.
        """
        user = UserRecord(
            username=payload.username,
            email=payload.email,
            password=hash_password(payload.password),
        )
        self.session.add(user)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise DuplicateUserError("Username or email already exists") from exc
        self.session.refresh(user)
        return user

    def authenticate(self, username: str, password: str) -> UserRecord | None:
        """Return the user when supplied credentials are valid.

        Args:
            username: Account login name.
            password: Candidate plaintext password.

        Returns:
            Authenticated user record, or None for invalid credentials.
        """
        user = self.session.scalar(select(UserRecord).where(UserRecord.username == username))
        if user is None or not verify_password(password, user.password):
            return None
        return user

    def get(self, user_id: int) -> UserRecord:
        """Return an existing user.

        Args:
            user_id: User identifier.

        Returns:
            Persisted user record.

        Raises:
            ResourceNotFoundError: If the user does not exist.
        """
        user = self.session.get(UserRecord, user_id)
        if user is None:
            raise ResourceNotFoundError("User not found")
        return user

    def update(self, user_id: int, payload: UserUpdateRequest) -> UserRecord:
        """Update an existing user's profile.

        Args:
            user_id: User identifier.
            payload: Validated partial profile update.

        Returns:
            Updated user record.

        Raises:
            DuplicateUserError: If username or email already exists.
            ResourceNotFoundError: If the user does not exist.
        """
        user = self.get(user_id)
        changes = payload.model_dump(exclude_unset=True)
        password = changes.pop("password", None)
        for field_name, value in changes.items():
            setattr(user, field_name, value)
        if password is not None:
            user.password = hash_password(password)
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise DuplicateUserError("Username or email already exists") from exc
        self.session.refresh(user)
        return user

    def delete(self, user_id: int) -> None:
        """Delete a user and their database-cascaded resources.

        Args:
            user_id: User identifier.

        Raises:
            ResourceNotFoundError: If the user does not exist.
        """
        self.session.delete(self.get(user_id))
        self.session.commit()