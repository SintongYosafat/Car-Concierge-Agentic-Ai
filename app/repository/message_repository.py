from datetime import datetime, timedelta
from cassandra.query import BatchStatement, BatchType
from cassandra.cluster import Session
from langchain_core.messages.base import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel
from app.core.logger import logger
from ..core.config import settings
from .conversation_repository import ConversationRow


class MessageRow(BaseModel):
    conversation_id: str
    created_at: datetime
    id: str
    message_type: str
    message_body: str


class MessageEnvelope(BaseModel):
    message: BaseMessage
    type: str
    conversation_id: str
    created_at: datetime


class MessageRepository:
    def __init__(self, session: Session):
        self.session = session
        self.session.set_keyspace(settings['CASSANDRA_KEYSPACE'])
        self._prepare_statements()

    def _prepare_statements(self):
        # Insert message
        self.insert_msg = self.session.prepare("""
            INSERT INTO messages (conversation_id, created_at, id, message_body, message_type)
            VALUES (?, ?, ?, ?, ?)
        """)
        
        # List messages for a conversation
        self.list_msg = self.session.prepare("""
            SELECT * FROM messages WHERE conversation_id = ?
        """)

        # List messages for a conversation with timestamp range
        self.list_last_n_msg = self.session.prepare("""
            SELECT * 
            FROM messages 
            WHERE conversation_id = ? and created_at < ? and created_at > ?
            ORDER BY created_at DESC LIMIT ?
        """)
        
        # Update conversation last_updated timestamp
        self.update_conv = self.session.prepare("""
            UPDATE conversations 
            SET last_updated = ? 
            WHERE user_id = ? AND created_at = ? AND id = ?
        """)

    def insert(self, conversation: ConversationRow, message_rows: list[BaseMessage]):
        now = datetime.now()

        rows = [self.convert_message_to_row(conversation.id, msg) for msg in message_rows]
        
        # AWS Keyspaces only supports UNLOGGED batches
        batch = BatchStatement(batch_type=BatchType.UNLOGGED)

        batch.add(self.update_conv, (now, conversation.user_id, conversation.created_at, conversation.id))
        
        # Increment timestamp by 1 millisecond for each message to ensure uniqueness
        for i, message_row in enumerate(rows):
            message_timestamp = now + timedelta(milliseconds=i)
            logger.info("Inserting message: %s, %s", message_row.id, message_row.message_type)
            batch.add(self.insert_msg, 
                      (
                          message_row.conversation_id, 
                          message_timestamp, 
                          message_row.id, 
                          message_row.message_body, 
                          message_row.message_type
                        )
            )
        
        self.session.execute(batch)
        return True
    
    def list_last_n(self, conversation_id: str, n: int, before_timestamp: datetime = None) -> list[BaseMessage]:
        if before_timestamp is None:
            before_timestamp = datetime.now() + timedelta(seconds=1)
        after_timestamp = datetime(1970, 1, 1)  # Epoch time as default
        rows = self.session.execute(self.list_last_n_msg, (conversation_id, before_timestamp, after_timestamp, n))
        messages = [self.convert_row_to_message(row) for row in rows]
        return list(reversed(messages))
    
    def list_last_n_envelopes(self, conversation_id: str, n: int, before_timestamp: datetime = None, after_timestamp: datetime = None, filter_tool_messages: bool = True) -> list[MessageEnvelope]:
        if before_timestamp is None:
            before_timestamp = datetime.now() + timedelta(seconds=1)
        if after_timestamp is None:
            after_timestamp = datetime(1970, 1, 1)  # Epoch time as default
        
        original_rows = self.session.execute(self.list_last_n_msg, (conversation_id, before_timestamp, after_timestamp, n * 3))
        
        rows = []
        if filter_tool_messages:
            rows = [row for row in original_rows if row.message_type != 'tool'][:n]
        else:
            rows = list(original_rows)[:n]
        
        message_envelopes = [self.convert_row_to_message_envelope(row) for row in rows]
        return list(reversed(message_envelopes))
    
    def convert_row_to_message_envelope(self, row) -> MessageEnvelope:
        message = None
        if row.message_type == 'human':
            message = HumanMessage.model_validate_json(row.message_body)
        elif row.message_type == 'ai':
            message = AIMessage.model_validate_json(row.message_body)
        elif row.message_type == 'tool':
            message = ToolMessage.model_validate_json(row.message_body)
        else:
            raise ValueError(f"Unknown message type: {row.message_type}")
        
        return MessageEnvelope(
            message=message,
            conversation_id=row.conversation_id,
            created_at=row.created_at,
            type=row.message_type
        )
    
    def convert_row_to_message(self, row) -> BaseMessage:
        if row.message_type == 'human':
            return HumanMessage.model_validate_json(row.message_body)
        elif row.message_type == 'ai':
            return AIMessage.model_validate_json(row.message_body)
        elif row.message_type == 'tool':
            return ToolMessage.model_validate_json(row.message_body)
        else:
            raise ValueError(f"Unknown message type: {row.message_type}")
        
    def convert_message_to_row(self, conversation_id: str, message: BaseMessage) -> MessageRow:
        if isinstance(message, HumanMessage):
            message_type = 'human'
        elif isinstance(message, AIMessage):
            message_type = 'ai'
        elif isinstance(message, ToolMessage):
            message_type = 'tool'
        else:
            raise ValueError(f"Unknown message type: {type(message)}")  
        return MessageRow(
            conversation_id=conversation_id,
            created_at=datetime.now(),
            id=message.id,
            message_type=message_type,
            message_body=message.model_dump_json()
        )
