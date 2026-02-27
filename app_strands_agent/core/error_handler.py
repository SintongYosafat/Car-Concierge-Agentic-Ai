from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app_strands_agent.core import logger, AcHttpException


def _create_error_response(
    request: Request,
    exc: HTTPException,
    error_key: str
) -> JSONResponse:
    # Determine if we should include exc_info in logs
    exc_info = getattr(exc, 'exc_info', True)
    
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        exc_info=exc_info,
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "error_key": error_key
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "key": error_key,
                "detail": exc.detail,
                "status": exc.status_code
            }
        }
    )


async def ac_http_exception_handler(request: Request, exc: AcHttpException) -> JSONResponse:
    """
    Custom exception handler for AcHttpException.
    Formats exceptions with custom error keys.
    """
    return _create_error_response(request, exc, exc.key)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Generic exception handler for standard HTTPException.
    Formats all HTTP exceptions to follow a consistent error response structure.
    """
    return _create_error_response(request, exc, "HTTP_ERROR")


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Custom exception handler for RequestValidationError (Pydantic validation errors).
    Formats validation errors to follow a consistent error response structure.
    """
    validation_errors = []
    
    for error in exc.errors():
        # Extract field name from location (skip 'body', 'query', etc.)
        loc = error.get("loc", ())
        field = ".".join(str(item) for item in loc[1:]) if len(loc) > 1 else str(loc[0]) if loc else "unknown"
        
        # Get error type (use built-in Pydantic error type)
        error_key = error.get("type", "validation_error")
        
        # Get error message
        message = error.get("msg", "Validation error")
        
        validation_errors.append({
            "field": field,
            "message": message,
            "key": error_key
        })
    
    logger.warning(
        f"Request Validation Error: {len(validation_errors)} validation error(s)",
        extra={
            "path": request.url.path,
            "method": request.method,
            "validation_errors": validation_errors
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "key": "REQUEST_VALIDATION_ERROR",
                "detail": "Request validation failed",
                "status": 422,
                "validation": validation_errors
            }
        }
    )


def setup_exception_handlers(app):
    app.add_exception_handler(AcHttpException, ac_http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)