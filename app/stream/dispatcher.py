import asyncio
from typing import Dict, List, Any, Literal
from cachetools import TTLCache
from pydantic import BaseModel

class StreamDispatcher:
    def __init__(self):
        # Maps conversation_id -> List of subscriber queues
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        # Stores history for late-joiners
        self.buffers: Dict[str, List[Any]] = TTLCache(maxsize=20000, ttl=180)

    async def get_stream(self, conversation_id: str):
        """Register a new listener and yield existing + new chunks."""
        queue = asyncio.Queue()
        
        # Catch up with history
        if conversation_id in self.buffers:
            for chunk in self.buffers[conversation_id]:
                queue.put_nowait(chunk)
        
        # Register for live updates
        if conversation_id not in self.subscribers:
            self.subscribers[conversation_id] = []
        self.subscribers[conversation_id].append(queue)

        try:
            while True:
                chunk = await queue.get()
                if chunk is None:  # Sentinel value for 'End of Stream'
                    break
                yield chunk
        finally:
            self.subscribers[conversation_id].remove(queue)

    def emit(self, conversation_id: str, chunk: Any):
        """Push a chunk to all active listeners and the buffer."""
        if conversation_id not in self.buffers:
            self.buffers[conversation_id] = []
        
        self.buffers[conversation_id].append(chunk)
        
        if conversation_id in self.subscribers:
            for queue in self.subscribers[conversation_id]:
                queue.put_nowait(chunk)

    def finalize(self, conversation_id: str):
        """Signal all listeners that the stream is done."""
        if conversation_id in self.subscribers:
            for queue in self.subscribers[conversation_id]:
                queue.put_nowait(None)
        if conversation_id in self.buffers:
            self.buffers.pop(conversation_id)
    
    def reset(self):
        """Delete all subscribers and buffers."""
        self.subscribers.clear()
        self.buffers.clear()