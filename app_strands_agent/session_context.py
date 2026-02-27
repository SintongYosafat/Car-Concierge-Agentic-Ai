from contextvars import ContextVar
from typing import Dict
 
_current_session_id: ContextVar[str] = ContextVar(
    "current_session_id",
    default="anonymous",
)
 
_workflow_timings: ContextVar[Dict[str, float]] = ContextVar(
    "workflow_timings",
    default={},
)