from fastapi import HTTPException, status


class ErrorMsg:
    AUTH_REQUIRED = 'Authentication required.'
    AUTH_FAILED = 'Authorization failed.'
    AUTH_ADMIN_FAILED = 'Admin required.'
    INVALID_TOKEN = 'Invalid token.'
    INVALID_CREDENTIALS = 'Invalid credentials.'
    DATA_TAKEN = 'Email or username is already taken.'
    INVALID_REFRESH_TOKEN = 'Refresh token is not valid.'
    NOT_FOUND = 'Object not found.'
    NO_DATA = 'No data given.'


class BaseHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = 'Server error'

    def __init__(self) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL)


class InvalidTokenException(BaseHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = ErrorMsg.INVALID_TOKEN


class AuthRequiredException(InvalidTokenException):
    DETAIL = ErrorMsg.INVALID_CREDENTIALS


class AuthAdminRequiredException(InvalidTokenException):
    DETAIL = ErrorMsg.AUTH_ADMIN_FAILED


class UserDataTakenException(BaseHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = ErrorMsg.DATA_TAKEN


class InvalidCredentialsException(UserDataTakenException):
    DETAIL = ErrorMsg.INVALID_CREDENTIALS


class InvalidRefreshTokenException(UserDataTakenException):
    DETAIL = ErrorMsg.INVALID_REFRESH_TOKEN


class ObjNotFoundException(BaseHTTPException):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL = ErrorMsg.NOT_FOUND


class InvalidDataException(BaseHTTPException):
    STATUS_CODE = status.HTTP_422_UNPROCESSABLE_ENTITY
    DETAIL = ErrorMsg.NO_DATA
