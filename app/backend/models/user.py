"""Pydantic schemas for authentication and user profile APIs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UserRegistrationRequest(BaseModel):
    """Request payload for registering an account.

    Attributes:
        username: Unique login name.
        email: Unique account email address.
        password: Plaintext password that is hashed before storage.
    """

    username: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdateRequest(BaseModel):
    """Request payload for changing an authenticated user profile.

    Attributes:
        username: Optional replacement login name.
        email: Optional replacement account email address.
        password: Optional plaintext password to hash before storage.
    """

    username: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, min_length=3, max_length=254)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class User(BaseModel):
    """Public representation of a user account without its password.

    Attributes:
        id: Unique user identifier.
        username: User login name.
        email: User email address.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


class LoginRequest(BaseModel):
    """Credentials used to request an access token.

    Attributes:
        username: Account login name.
        password: Account plaintext password.
    """

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """Bearer access token issued after successful login.

    Attributes:
        access_token: Signed JWT access token.
        token_type: Authentication scheme.
        user_id: Authenticated user identifier.
        username: Authenticated user login name.
    """

    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str