"""Logging configuration with support for both JSON and console formats."""

import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Dict

from app.core.config import settings

# Map log level string to logging constants
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class JsonFormatter(logging.Formatter):
    """Simplified JSONL formatter for Kubernetes deployment."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as a JSON string.
        
        Args:
            record: The log record to format
            
        Returns:
            str: JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": "".join(traceback.format_exception(*record.exc_info)),
            }
        
        # Add any extra fields passed to the logger
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Human-readable formatter for local development."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with simplified output.
        
        Args:
            record: The log record to format
            
        Returns:
            str: Formatted log string
        """
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Basic format: time - level - module:function:line - message
        log_line = f"{timestamp} - {record.levelname:8s} - {record.module}:{record.funcName}:{record.lineno} - {record.getMessage()}"
        
        # Add exception traceback if present
        if record.exc_info:
            log_line += "\n" + "".join(traceback.format_exception(*record.exc_info))
        
        return log_line


def setup_logging() -> logging.Logger:
    """Configure logging with JSON or console format based on settings.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get log level from settings, default to INFO
    log_level_str = getattr(settings, "log_level", "INFO").upper()
    log_level = LOG_LEVELS.get(log_level_str, logging.INFO)
    
    # Get log format from settings (json or console), default to console for dev
    log_format = getattr(settings, "log_format", "console").lower()
    
    # Create console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter based on log_format setting
    if log_format == "json":
        console_handler.setFormatter(JsonFormatter())
    else:
        console_handler.setFormatter(ConsoleFormatter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Create app logger
    app_logger = logging.getLogger("ai-concierge")
    app_logger.info(
        f"Logging initialized - Level: {log_level_str}, Format: {log_format}, Environment: {getattr(settings, 'AC_ENV', 'default')}"
    )
    
    return app_logger


# Initialize and export logger
logger = setup_logging()