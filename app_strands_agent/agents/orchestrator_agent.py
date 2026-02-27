import functools
from pathlib import Path
 
from strands import Agent
from strands.handlers import null_callback_handler
from app_strands_agent.core import settings
from app_strands_agent.tools.search_vehicles import search_vehicles
from app_strands_agent.llm.model_resolver import resolve
from app_strands_agent.agents._helper import session_manager, conversation_manager
 
 
PROMPT_PATH = Path("app_strands_agent/instruction/orchestrator_v2_prompt.txt")
 
 
@functools.lru_cache(maxsize=1)
def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")
 
 
model_name = settings.get("DEFAULT_MODEL")
model = resolve(model_name)
 
 
def orchestrator_agent(session_id: str, user_id: str) -> Agent:
    """Create a orchestrator agent.
 
    - Comprehensive car consultant (answers knowledge questions directly)
    - Uses search_vehicles tool only for OLX listing discovery
    - Extracts structured parameters (no second LLM call)
    - Responds in Bahasa Indonesia with friendly tone
    """
    return Agent(
        model=model,
        system_prompt=_load_system_prompt(),
        tools=[search_vehicles],
        callback_handler=null_callback_handler,
        session_manager=session_manager(session_id=session_id, user_id=user_id),
        conversation_manager=conversation_manager(),
    )