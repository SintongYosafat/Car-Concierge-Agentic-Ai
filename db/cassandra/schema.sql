-- ================================================
-- Keyspace: concierge (used by app_strands_agent)
-- ================================================
CREATE KEYSPACE IF NOT EXISTS concierge
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};
 
USE concierge;
 
CREATE TABLE IF NOT EXISTS chat_messages (
  user_id text,
  session_id text,
  timestamp timestamp,
  role text,
  message text,
  PRIMARY KEY (user_id, session_id, timestamp)
) WITH CLUSTERING ORDER BY (session_id ASC, timestamp DESC);
 
 
-- ================================================
-- Keyspace: ai_concierge (used by app)
-- ================================================
CREATE KEYSPACE IF NOT EXISTS ai_concierge
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};
 
USE ai_concierge;
 
CREATE TABLE IF NOT EXISTS conversations (
  user_id text,
  created_at timestamp,
  id text,
  last_updated timestamp,
  PRIMARY KEY (user_id, created_at, id)
) WITH CLUSTERING ORDER BY (created_at DESC);
 
CREATE INDEX IF NOT EXISTS conversations_id_idx ON conversations (id);
 
CREATE TABLE IF NOT EXISTS messages (
  conversation_id text,
  created_at timestamp,
  id text,
  message_type text,
  message_body text,
  PRIMARY KEY (conversation_id, created_at, id)
) WITH CLUSTERING ORDER BY (created_at DESC, id ASC);