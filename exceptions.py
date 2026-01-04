from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class QuizException(Exception):
    """Base exception for the quiz application"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(QuizException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AuthorizationError(QuizException):
    """Authorization related errors"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

class NotFoundError(QuizException):
    """Resource not found errors"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class ValidationError(QuizException):
    """Validation errors"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

class ConflictError(QuizException):
    """Conflict errors (e.g., duplicate resources)"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )

class ExamNotActiveError(QuizException):
    """Exam not active errors"""
    def __init__(self, message: str = "Exam is not active"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ExamTimeExpiredError(QuizException):
    """Exam time expired errors"""
    def __init__(self, message: str = "Exam time has expired"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )
