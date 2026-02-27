
from fastapi.security import HTTPBasicCredentials
from app.api.v1.schema import ExperimentConversationRequest, ConversationRequest
from app.api.v1.schema import Context
from app.core.logger import logger
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from app.core.exceptions import AcHttpException
from fastapi.responses import StreamingResponse
from app.core.config import settings, SYSTEM_PROMPT
import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from app.llm.model_resolver import resolve
from app.security.basic import validate_credentials
from app.workflow.base_workflow import BaseWorkflow
from app.workflow.workflow_resolver import resolve as resolve_workflow
import json
from app.repository.conversation_repository import ConversationRepository, ConversationRow
from app.repository.message_repository import MessageRepository
from langchain.messages import HumanMessage
from langchain_core.messages.base import BaseMessage
from app.stream.dispatcher import StreamDispatcher
from typing import Annotated

router = APIRouter()

async def stream_workflow_response(thread_id: str, dispatcher: StreamDispatcher):
    last_sent_index = -1
    async for chunk in dispatcher.get_stream(thread_id):
        last_sent_index += 1
        chunk_type = chunk.get("type")
        
        if chunk_type == "error":
            # Send error to client and close connection
            logger.error(f"Streaming error for thread_id {thread_id}: {chunk.get('payload')}")
            data_payload = json.dumps(chunk)
            yield f"data: {data_payload}\n\n"
            break
        elif chunk_type == "token":
            data_payload = json.dumps(chunk)
            logger.info(f"Streaming chunk {last_sent_index + 1} for thread_id {thread_id}")
            yield f"data: {data_payload}\n\n"
        elif chunk_type == "node":
            data_payload = json.dumps(chunk)
            logger.info(f"Streaming chunk {last_sent_index + 1} for thread_id {thread_id}")
            yield f"data: {data_payload}\n\n"
        else:
            data_payload = json.dumps(chunk)
            logger.info(f"Streaming chunk {last_sent_index + 1} for thread_id {thread_id}")
            yield f"data: {data_payload}\n\n"


async def _process_chat_request(
    conversation_id: str,
    prompt: str,
    user_id: str,
    model_id: str,
    workflow_id: str,
    checkpointer: InMemorySaver,
    conversation_repository: ConversationRepository,
    message_repository: MessageRepository,
    dispatcher: StreamDispatcher
) -> StreamingResponse:
    """Internal function to process chat requests with specified model and workflow."""
    message_id = uuid.uuid4().hex
    conversation: ConversationRow = None
    workflow: BaseWorkflow = None
    messages: list[BaseMessage] = []
    
    try:
        model = resolve(model_id)
        workflow_class = resolve_workflow(workflow_id)
        
        workflow = workflow_class(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=checkpointer,
            # response_format=ToolStrategy(ChatResponse),
            context_schema=Context
        )

        # Update converstation last update timestamp or create if not exists
        # Retrieve last N messages for LLM context
        conversation = conversation_repository.get(user_id, conversation_id)
        
        if not conversation:
            conversation = conversation_repository.create(conversation_id, user_id)
        else:
            # TODO: Filter out initial tool message as LLM will raise error
            messages = message_repository.list_last_n(conversation_id, settings['CONVERSATION_WINDOW_SIZE'])
        
        # Save user message immediately before workflow started
        message = HumanMessage(id=message_id, content=prompt)
        message_repository.insert(conversation, [message])
        messages.append(message)
    except ValueError as e:
        raise AcHttpException("INVALID_REQUEST", detail=str(e))
    except Exception as e:
        raise AcHttpException("INTERNAL_SERVER_ERROR", detail="Failed to initialize workflow")
    
    # Execute workflow in background, so it doesn't terminated when client disconnects
    asyncio.create_task(
        workflow.invoke(
            conversation_id, 
            messages, 
            conversation, 
            user_id, 
            dispatcher, 
            message_repository, 
            checkpointer
        )
    )

    return StreamingResponse(stream_workflow_response(conversation_id, dispatcher), media_type="text/event-stream")


@router.post("/submit")
async def submit_then_stream(
        fastapi_request: Request,
        request: ConversationRequest, 
        background_tasks: BackgroundTasks, 
        credentials: Annotated[HTTPBasicCredentials, Depends(validate_credentials)],
    ):
    checkpointer: InMemorySaver = fastapi_request.app.state.checkpointer
    conversation_repository: ConversationRepository = fastapi_request.app.state.conversation_repository
    message_repository: MessageRepository = fastapi_request.app.state.message_repository
    dispatcher: StreamDispatcher = fastapi_request.app.state.dispatcher

    return await _process_chat_request(
        conversation_id=request.conversation_id,
        prompt=request.prompt,
        user_id=credentials.username,
        model_id=settings['DEFAULT_MODEL_ID'],
        workflow_id=settings['DEFAULT_WORKFLOW_ID'],
        checkpointer=checkpointer,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        dispatcher=dispatcher
    )


@router.post("/submit-experiment")
async def submit_then_stream_experiment(
        fastapi_request: Request,
        request: ExperimentConversationRequest, 
        background_tasks: BackgroundTasks, 
        credentials: Annotated[HTTPBasicCredentials, Depends(validate_credentials)],
    ):

    checkpointer: InMemorySaver = fastapi_request.app.state.checkpointer
    conversation_repository: ConversationRepository = fastapi_request.app.state.conversation_repository
    message_repository: MessageRepository = fastapi_request.app.state.message_repository
    dispatcher: StreamDispatcher = fastapi_request.app.state.dispatcher
    

    # LOAD TEST Purpose   
    # Override thread_id with random string if random_thread_id is True
    conversation_id = request.conversation_id
    if request.random_thread_id:
        conversation_id = str(uuid.uuid4())
        logger.info(f"Generated random thread_id: {conversation_id}")
    
    return await _process_chat_request(
        conversation_id=conversation_id,
        prompt=request.prompt,
        user_id=credentials.username,
        model_id=request.model_id,
        workflow_id=request.workflow_id,
        checkpointer=checkpointer,
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        dispatcher=dispatcher
    )
