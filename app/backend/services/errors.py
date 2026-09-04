"""Domain exceptions raised by backend persistence services."""


class DuplicateUserError(Exception):
    """Raised when a username or email already belongs to another user."""


class ResourceNotFoundError(Exception):
    """Raised when an owned resource cannot be found."""