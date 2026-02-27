from fastapi import HTTPException, status
from typing import Any, Dict, Optional
from app_strands_agent.core import logger


# Error definitions registry
ERROR_DEFINITIONS = {
    "CONVERSATION_NOT_FOUND": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "Conversation not found",
        "key": "CONVERSATION_NOT_FOUND",
        "exc_info": False
    },
    "INVALID_REQUEST": {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "Invalid request",
        "key": "INVALID_REQUEST",
        "exc_info": False
    },
    "INVALID_MODEL_NAME": {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "Invalid model name",
        "key": "INVALID_MODEL_NAME",
        "exc_info": False
    },
    "INVALID_WORKFLOW_ID": {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "detail": "Invalid workflow ID",
        "key": "INVALID_WORKFLOW_ID",
        "exc_info": False
    },
    "INTERNAL_SERVER_ERROR": {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "Internal server error",
        "key": "INTERNAL_SERVER_ERROR",
        "exc_info": True
    },
}


class AcHttpException(HTTPException):
    """
    Custom HTTP exception with additional error key field.
    
    Can be used in two ways:
    1. With error_code (looks up predefined error from ERROR_DEFINITIONS):
       raise AcHttpException("INVALID_MODEL_ID", detail="Custom detail")
       
    2. With explicit parameters:
       raise AcHttpException(status_code=400, detail="Error", key="CUSTOM_ERROR")
    """
    
    def __init__(
        self,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        detail: Optional[Any] = None,
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        exc_info: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        # If error_code provided, use predefined error definition
        if error_code and error_code in ERROR_DEFINITIONS:
            error_def = ERROR_DEFINITIONS[error_code]
            status_code = status_code or error_def["status_code"]
            detail = detail or error_def["detail"]
            key = key or error_def["key"]
            exc_info = exc_info if exc_info is not None else error_def.get("exc_info", False)
            
            # Format detail with kwargs if provided
            if kwargs and isinstance(detail, str):
                try:
                    detail = detail.format(**kwargs)
                except (KeyError, ValueError):
                    # If format fails, append kwargs to detail
                    detail = f"{detail}: {', '.join(f'{k}={v}' for k, v in kwargs.items())}"
        else:
            # Use provided parameters or defaults
            status_code = status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = detail or "An error occurred"
            key = key or error_code or "API_ERROR"
            exc_info = exc_info if exc_info is not None else True
        
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.key = key
        self.exc_info = exc_info
        
        # Log the exception when it's created
        log_message = f"Exception raised: {key} - {detail}"
        if exc_info:
            logger.error(log_message, exc_info=True)
        else:
            logger.warning(log_message)


# Special exception classes that require custom behavior
class InvalidCredentialsException(AcHttpException):
    """Raised when authentication credentials are invalid."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            key="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Basic"},
            exc_info=False,
        )