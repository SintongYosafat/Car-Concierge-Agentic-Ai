from abc import ABC, abstractmethod
from langgraph.graph.state import CompiledStateGraph

from app.api.v1.schema import ExperimentConversationRequest
from app.api.v1.schema import Context

from app.core.logger import logger
from app.repository.conversation_repository import ConversationRow
from app.repository.message_repository import MessageRepository
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from app.stream.dispatcher import StreamDispatcher
from app.api.v1.schema import ErrorDetail


class BaseWorkflow(ABC):
    async def invoke(
            self,
            conversation_id: str,
            messages: list[HumanMessage], 
            conversation: ConversationRow, 
            user_id: str, 
            dispatcher: StreamDispatcher, 
            message_repository: MessageRepository, 
            checkpointer: InMemorySaver
        ) :
        prompt_message = messages[-1]
        config = {"configurable": {"thread_id": conversation_id}}
    
        try:
            async for stream_node, chunk in self.agent.astream(
                {"messages": messages},
                config=config,
                stream_mode=["updates", "messages"],
                context=Context(user_id=user_id),
            ):
                
                if stream_node == "messages":
                    chunk_data, chunk_step = chunk
                    content = chunk_data.content_blocks
                    response_object = {
                        "type": "token",
                        "payload": content,
                        "node": chunk_step['langgraph_node'],
                    }
                    dispatcher.emit(conversation_id, response_object)
                elif stream_node == "updates":
                    for step, data in chunk.items():
                        last_data = data['messages'][-1]
                        content = last_data.content_blocks
                        response_object = {
                            "type": "node",
                            "payload": content,
                            "node": step,
                        }
                        dispatcher.emit(conversation_id, response_object)
                else:
                    response_object = {
                        "type": stream_node,
                        "payload": chunk,
                    }
                    dispatcher.emit(conversation_id, response_object)
            
            # Retrieve all messages from agent state
            messages = self.agent.get_state(config).values["messages"]
            
            last_index = -1
            for i in range(len(messages)):
                if hasattr(messages[i], 'id') and messages[i].id == prompt_message.id:
                    last_index = i
                    break
            
            if last_index > -1 and last_index < len(messages) - 1:
                # Save all new messages starting after the initial message
                message_repository.insert(
                    conversation,
                    messages[last_index + 1 :]
                )
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            error_detail = ErrorDetail(
                key="workflow_error", 
                detail="An error occurred during workflow execution", 
                status=500
            )
            dispatcher.emit(conversation_id, {"type": "error", "error": error_detail.model_dump()})
            
        finally:
            # Clean up thread state from checkpointer
            try:
                dispatcher.finalize(conversation_id)
                checkpointer.delete_thread(conversation_id)
                logger.info(f"Deleted thread state for {conversation_id}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup thread state: {cleanup_error}")
