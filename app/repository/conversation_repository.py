from datetime import datetime
from cassandra.cluster import Session
from pydantic import BaseModel
from ..core.config import settings


class ConversationRow(BaseModel):
    user_id: str
    created_at: datetime
    id: str
    last_updated: datetime


class ConversationRepository:
    def __init__(self, session: Session):
        self.session = session
        self.session.set_keyspace(settings['CASSANDRA_KEYSPACE'])
        self._prepare_statements()

    def _prepare_statements(self):
        # Insert new conversation
        self.insert_conv = self.session.prepare("""
            INSERT INTO conversations (user_id, created_at, id, last_updated)
            VALUES (?, ?, ?, ?)
        """)
        
        # Update conversation last_updated timestamp
        self.update_conv = self.session.prepare("""
            UPDATE conversations 
            SET last_updated = ? 
            WHERE user_id = ? AND created_at = ? AND id = ?
        """)
        
        # Get specific conversation (uses index on id)
        self.get_conv = self.session.prepare("""
            SELECT * FROM conversations WHERE user_id = ? AND id = ?
        """)
        
        # List conversations for a user
        self.list_conv = self.session.prepare("""
            SELECT * FROM conversations WHERE user_id = ? LIMIT ? ALLOW FILTERING
        """)

    def create(self, conversation_id: str, user_id: str) -> ConversationRow:
        now = datetime.now()
        self.session.execute(
            self.insert_conv, 
            (user_id, now, conversation_id, now)
        )
        return ConversationRow(
            user_id=user_id, 
            created_at=now, 
            id=conversation_id, 
            last_updated=now
        )
    
    def update(self, conversation: ConversationRow) -> ConversationRow:
        now = datetime.now()
        self.session.execute(
            self.update_conv, 
            (now, conversation.user_id, conversation.created_at, conversation.id)
        )
        return ConversationRow(
            user_id=conversation.user_id, 
            created_at=conversation.created_at, 
            id=conversation.id, 
            last_updated=now
        )

    def get(self, user_id: str, conversation_id: str) -> ConversationRow:
        row = self.session.execute(self.get_conv, (user_id, conversation_id)).one()
        return self.convert_row_to_conversation(row) if row else None
    
    def list(self, user_id: str, limit: int = 50) -> list[ConversationRow]:
        rows = self.session.execute(self.list_conv, (user_id, limit))
        return [self.convert_row_to_conversation(row) for row in rows]
    
    def get_latest(self, user_id: str) -> ConversationRow:
        rows = self.session.execute(self.list_conv, (user_id, 1))
        row = rows.one()
        return self.convert_row_to_conversation(row) if row else None
    
    def convert_row_to_conversation(self, row) -> ConversationRow:
        return ConversationRow(
            user_id=row.user_id,
            created_at=row.created_at,
            id=row.id,
            last_updated=row.last_updated
        )
