from enum import Enum
from typing import Optional

import pendulum
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status

from app.response_generator import EmotionChatbotResponseGenerator
from core.chatbot import TurnTakingChatSession
from core.time import get_timestamp

router = APIRouter()

active_sessions: dict[str, TurnTakingChatSession] = dict()


# APIs==========================================================================================

class ChatMessage(BaseModel):
    message: str
    is_user: bool
    metadata: Optional[dict]
    processing_time: float
    timestamp: int


class ChatSessionInitializeArgs(BaseModel):
    user_name: str
    user_age: int


@router.post("/{session_id}/initialize", response_model=ChatMessage)
async def _initialize_chat_session(session_id: str, args: ChatSessionInitializeArgs) -> ChatMessage:
    if session_id in active_sessions and active_sessions[session_id] is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate active session ID."
        )
    else:
        new_session = TurnTakingChatSession(session_id,
                                            EmotionChatbotResponseGenerator(user_name=args.user_name, user_age=args.user_age))
        active_sessions[session_id] = new_session
        message, metadata, elapsed = await new_session.initialize()
        return ChatMessage(
            message= message,
            is_user=False,
            metadata=metadata,
            processing_time=elapsed,
            timestamp=get_timestamp()
        )

@router.post("/{session_id}/terminate")
def _terminate_chat_session(session_id: str):
    if session_id in active_sessions:
       del active_sessions[session_id]