from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    thread_id: str           # session/conversation ID — caller manages this
    user_id: Optional[str] = None  # optional, for future auth

class ChatResponse(BaseModel):
    reply: str
    thread_id: str