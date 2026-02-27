from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from ..tool.dummy_booking_kb import get_olx_booking_terms
from ..tool.dummy_search_vehicle import search_vehicle_ads
from .base_workflow import BaseWorkflow


class LangchainBasicWorkflow(BaseWorkflow):
    """Basic LangChain agent workflow."""

    def __init__(
        self,
        model: BaseChatModel,
        system_prompt: str,
        checkpointer: BaseCheckpointSaver,
        response_format: any = None,
        context_schema: any = None,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.checkpointer = checkpointer
        self.response_format = response_format
        self.context_schema = context_schema
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=[get_olx_booking_terms, search_vehicle_ads],
            response_format=self.response_format,
            checkpointer=self.checkpointer,
            context_schema=self.context_schema,
        )