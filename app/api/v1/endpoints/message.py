
from fastapi.security import HTTPBasicCredentials
from fastapi import APIRouter
from app.security.basic import validate_credentials
from app.core.exceptions import AcHttpException
from app.api.v1.schema import AcBaseResponse
from app.repository.database import get_session
from app.repository.conversation_repository import ConversationRepository
from app.repository.message_repository import MessageRepository, MessageEnvelope, MessageRow
from datetime import datetime
from typing import Annotated, Any
from pydantic import BaseModel
from langchain_core.messages.base import BaseMessage
from langchain_core.messages import AIMessage
from fastapi import Request
from app.llm.model_catalog import get_model_info

from fastapi import Depends, HTTPException

router = APIRouter()

class UsageMetadata(BaseModel):
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    model_id: str | None = None
    input_token_price: float | None = None
    cached_input_token_price: float | None = None
    output_token_price: float | None = None
    total_cost: float | None = None

class MessageResponse(BaseModel):
    id: str
    type: str
    content_blocks: list[Any]
    created_at: datetime
    conversation_id: str
    usage_metadata: UsageMetadata | None = None

class ListMessagesResponse(BaseModel):
    messages: list[MessageResponse]

def _get_messages_internal(
    user_id: str,
    conversation_id: str,
    limit: int,
    before: datetime | None,
    after: datetime | None,
    filter_tool_messages: bool,
    message_repository: MessageRepository,
    conversation_repository: ConversationRepository,
    include_usage_metadata: bool = False,
) -> ListMessagesResponse:
    """Internal helper to retrieve messages with optional tool message filtering."""
    conversation = conversation_repository.get(user_id=user_id, conversation_id=conversation_id)

    if not conversation:
        raise AcHttpException("CONVERSATION_NOT_FOUND", detail=f"Conversation {conversation_id} not found")
    
    envelopes: list[MessageEnvelope] = message_repository.list_last_n_envelopes(
        conversation_id=conversation_id,
        n=limit,
        before_timestamp=before,
        after_timestamp=after,
        filter_tool_messages=filter_tool_messages
    )

    messages = [convert_to_response(envelope, include_usage_metadata=include_usage_metadata) for envelope in envelopes]  

    return ListMessagesResponse(messages=messages)

@router.get("/")
async def get_messages(
        request: Request,
        credentials: Annotated[HTTPBasicCredentials, Depends(validate_credentials)],
        conversation_id: str, 
        limit: int = 10, 
        before: datetime | None = None,
        after: datetime | None = None
    ) -> AcBaseResponse[ListMessagesResponse]:
    result = _get_messages_internal(
        user_id=credentials.username,
        conversation_id=conversation_id,
        limit=limit,
        before=before,
        after=after,
        filter_tool_messages=True,
        message_repository=request.app.state.message_repository,
        conversation_repository=request.app.state.conversation_repository,
    )
    return AcBaseResponse(data=result)

@router.get("/latest-conversation")
async def get_messages(
        request: Request,
        credentials: Annotated[HTTPBasicCredentials, Depends(validate_credentials)],
        limit: int = 10, 
        before: datetime | None = None,
        after: datetime | None = None
    ) -> AcBaseResponse[ListMessagesResponse]:

    conversation_repository=request.app.state.conversation_repository
    message_repository=request.app.state.message_repository

    latest_conversation = conversation_repository.get_latest(user_id=credentials.username)

    if not latest_conversation:
        raise AcHttpException("CONVERSATION_NOT_FOUND")

    result = _get_messages_internal(
        user_id=credentials.username,
        conversation_id=latest_conversation.id,
        limit=limit,
        before=before,
        after=after,
        filter_tool_messages=True,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
    )
    return AcBaseResponse(data=result)

@router.get("/experiment-unfiltered")
async def get_messages_unfiltered(
        request: Request,
        credentials: Annotated[HTTPBasicCredentials, Depends(validate_credentials)],
        conversation_id: str, 
        limit: int = 10, 
        before: datetime | None = None,
        after: datetime | None = None
    ) -> AcBaseResponse[ListMessagesResponse]:
    result = _get_messages_internal(
        user_id=credentials.username,
        conversation_id=conversation_id,
        limit=limit,
        before=before,
        after=after,
        filter_tool_messages=False,
        message_repository=request.app.state.message_repository,
        conversation_repository=request.app.state.conversation_repository,
        include_usage_metadata=True,
    )
    return AcBaseResponse(data=result)

def convert_to_response(envelope: MessageEnvelope, include_usage_metadata: bool = False) -> MessageResponse:
    original_content_blocks = envelope.message.content_blocks
    filtered_content_blocks = []

    for block in original_content_blocks:
        if block["type"] != "text":
            continue
        filtered_content_blocks.append({"type": block["type"], "text": block["text"]})
    
    # Extract usage metadata for AI messages only if requested
    usage_metadata = None
    if include_usage_metadata and envelope.type == "ai" and isinstance(envelope.message, AIMessage):
        msg_usage = getattr(envelope.message, "usage_metadata", None)
        if msg_usage:
            input_tokens = msg_usage.get("input_tokens", 0)
            output_tokens = msg_usage.get("output_tokens", 0)
            
            # Extract cached input tokens from input_token_details
            input_token_details = msg_usage.get("input_token_details", {})
            cached_input_tokens = input_token_details.get("cache_read", 0)
            
            # Get model_id from response_metadata
            response_metadata = getattr(envelope.message, "response_metadata", {})
            model_id = response_metadata.get("model_name")
            
            # Get pricing info from catalog
            model_info = get_model_info(model_id) if model_id else None
            
            # Calculate costs (prices are per million tokens)
            total_cost = None
            input_token_price = None
            cached_input_token_price = None
            output_token_price = None
            
            if model_info:
                input_token_price = model_info["input_token_price"]
                cached_input_token_price = model_info["cached_input_token_price"]
                output_token_price = model_info["output_token_price"]
                
                # Calculate total cost
                regular_input_tokens = input_tokens - cached_input_tokens
                input_cost = (regular_input_tokens / 1_000_000) * input_token_price
                cached_cost = (cached_input_tokens / 1_000_000) * cached_input_token_price
                output_cost = (output_tokens / 1_000_000) * output_token_price
                total_cost = input_cost + cached_cost + output_cost
            
            usage_metadata = UsageMetadata(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_input_tokens=cached_input_tokens,
                model_id=model_id,
                input_token_price=input_token_price,
                cached_input_token_price=cached_input_token_price,
                output_token_price=output_token_price,
                total_cost=total_cost
            )
        
    return MessageResponse(
        id=envelope.message.id,
        type=envelope.type,
        content_blocks=filtered_content_blocks,
        created_at=envelope.created_at,
        conversation_id=envelope.conversation_id,
        usage_metadata=usage_metadata
    )