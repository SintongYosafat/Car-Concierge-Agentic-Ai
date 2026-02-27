from strands.session.s3_session_manager import S3SessionManager
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SummarizingConversationManager
import os, re
from app_strands_agent.core import settings
 
def load_instruction(file_name: str) -> str:
    """
    Load instruction file from the prompts directory.
    Args:
        file_name: Name of the instruction file
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(current_dir, "..", "instruction")
    file_path = os.path.join(prompts_dir, file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Instruction file '{file_name}' not found in {prompts_dir}"
        )
 
def conversation_manager() -> SummarizingConversationManager:
    """Create conversation manager"""
    return SummarizingConversationManager(
        summary_ratio=settings.SUMMARY_RATIO,
        preserve_recent_messages=settings.MAX_SESSION_MESSAGES
    )
 
def session_manager(session_id: str, user_id:str) -> S3SessionManager | FileSessionManager:
    """
    Create session manager for agent
    - dev: Uses FileSessionManager (local storage)
    - production: Uses S3SessionManager (cloud storage)
 
    Args:
        session_id: unique session identifier
        user_id: user identifier for prefix
    """
    env = settings.current_env
    storage_path = settings.get('AGENT_SESSION')
    if env == "dev":
        storage_path += f"/{user_id}"
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
        return FileSessionManager(
            session_id=session_id,
            storage_dir=storage_path
        )
    return S3SessionManager(
        session_id=session_id,
        bucket=storage_path,
        prefix=user_id
    )
 
 
def strip_internal_reasoning(text: str) -> str:
    """
    Remove internal reasoning or chain-of-thought
    from LLM output before returning it to the user.
    """
    _REASONING_PATTERN = re.compile(
        r"<thinking>.*?</thinking>|<analysis>.*?</analysis>|<reasoning>.*?</reasoning>",
        re.DOTALL | re.IGNORECASE,
    )
    return _REASONING_PATTERN.sub("", text).strip()