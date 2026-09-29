"""Custom exception hierarchy for the service layer.

Services raise these exceptions instead of returning HTTP responses,
keeping business logic completely HTTP-agnostic.  Controllers catch
them and translate to the appropriate JSON error + status code.
"""


class AppError(Exception):
    """Base application error with an associated HTTP status code."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    """Raised when input validation fails (400)."""

    def __init__(self, message):
        super().__init__(message, 400)


class AuthenticationError(AppError):
    """Raised when authentication is required or credentials are invalid (401)."""

    def __init__(self, message='Authentication required.'):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    """Raised when the authenticated user lacks permission (403)."""

    def __init__(self, message='Forbidden.'):
        super().__init__(message, 403)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist (404)."""

    def __init__(self, message='Resource not found.'):
        super().__init__(message, 404)


class ModerationError(AppError):
    """Raised when content is flagged as toxic/hateful and blocked (422)."""

    def __init__(self, message):
        super().__init__(message, 422)


class ConflictError(AppError):
    """Raised when an operation conflicts with existing state (409)."""

    def __init__(self, message):
        super().__init__(message, 409)
