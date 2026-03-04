"""
Centralised exception types and error response helpers.
"""

from fastapi import HTTPException, status


class AppError(Exception):
    """Base application error."""

    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} '{resource_id}' not found",
            status_code=404,
        )


class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(code="CONFLICT", message=message, status_code=409)


class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(code="VALIDATION_ERROR", message=message, status_code=422)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ProviderError(AppError):
    """Error from an external provider (Gmail, Outlook, etc.)."""

    def __init__(self, provider: str, message: str):
        super().__init__(
            code="PROVIDER_ERROR",
            message=f"[{provider}] {message}",
            status_code=502,
        )


class ApprovalRequiredError(AppError):
    """Attempt to execute an action without approval."""

    def __init__(self, action_id: str):
        super().__init__(
            code="APPROVAL_REQUIRED",
            message=f"Action '{action_id}' requires explicit user approval",
            status_code=403,
        )


class AIBudgetExceededError(AppError):
    def __init__(self):
        super().__init__(
            code="AI_BUDGET_EXCEEDED",
            message="AI cost budget has been exceeded",
            status_code=429,
        )


def raise_not_found(resource: str, resource_id: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": "NOT_FOUND", "message": f"{resource} '{resource_id}' not found"},
    )
