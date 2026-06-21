from fastapi import HTTPException, status


# ================= BASE EXCEPTION =================
class AppException(HTTPException):
    """Base application exception (optional future extension)"""
    def __init__(self, status_code: int, message: str, error_code: str):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "message": message,
                "error_code": error_code
            }
        )

class NotFoundException(AppException):
    def __init__(self, message="Resource not found", error_code="NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            error_code=error_code
        )


class ConflictException(AppException):
    def __init__(self, message="Conflict occurred", error_code="CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code=error_code
        )


class UnauthorizedException(AppException):
    def __init__(self, message="Unauthorized", error_code="UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code=error_code
        )


class ValidationException(AppException):
    def __init__(self, message="Validation error", error_code="VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            error_code=error_code
        )