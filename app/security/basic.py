import secrets
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.core.config import settings
from app.core.exceptions import InvalidCredentialsException

security = HTTPBasic()


def validate_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> HTTPBasicCredentials:
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = settings.BASIC_AUTH_PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not is_correct_password:
        raise InvalidCredentialsException()
    return credentials
