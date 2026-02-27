from dotenv import load_dotenv, dotenv_values
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents.structured_output import ToolStrategy
import os
from app.core.config import settings


SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location. Only use this tool if user don't provide a location.

If a user asks you for the weather, make sure you know the location from conversation context (1ST PRIORITY) or tools call (2nd priority)"""

@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!" if city == "Florida" else "It's foggy with a chance of code in SF."

@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"

@tool
def trigger_error(runtime: ToolRuntime[Context]) -> str:
    """Trigger an error for testing purposes."""
    raise RuntimeError("This is a test error.")

model = ChatOpenAI(
    model_name = "gpt-4o-mini",
    base_url=settings.get("AZURE_AI_ENDPOINT"),
    api_key=settings.get("AZURE_AI_CREDENTIAL"),
)

# We use a dataclass here, but Pydantic models are also supported.
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    # A punny response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    weather_conditions: str | None = None

checkpointer = InMemorySaver()

def build_agent():
    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[get_user_location, get_weather_for_location, trigger_error],
        context_schema=Context,
        response_format=ToolStrategy(ResponseFormat),
        checkpointer=checkpointer
    )
    return agent