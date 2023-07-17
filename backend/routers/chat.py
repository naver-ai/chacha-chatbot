from typing import Optional

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from starlette import status

from app.response_generator import EmotionChatbotResponseGenerator
from core.chatbot import TurnTakingChatSession, Dialogue
from core.time import get_timestamp

router = APIRouter()

active_sessions: dict[str, TurnTakingChatSession] = dict()


def _restore_session_instance(session_id: str) -> TurnTakingChatSession | None:
    session = TurnTakingChatSession(session_id,
                                    EmotionChatbotResponseGenerator())
    if session.load():
        return session
    else:
        return None


def _assert_get_session(session_id: str) -> TurnTakingChatSession:
    if session_id in active_sessions and active_sessions[session_id] is not None:
        return active_sessions[session_id]
    else:
        instance = _restore_session_instance(session_id)
        if instance is not None:
            active_sessions[session_id] = instance
            return instance
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sessions with that ID."
            )


# APIs==========================================================================================

class ChatMessage(BaseModel):
    message: str
    is_user: bool
    metadata: Optional[dict]
    processing_time: float | None
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
                                            EmotionChatbotResponseGenerator(user_name=args.user_name,
                                                                            user_age=args.user_age))
        active_sessions[session_id] = new_session
        message, metadata, elapsed = await new_session.initialize()

        new_session.save()

        return ChatMessage(
            message=message,
            is_user=False,
            metadata=metadata,
            processing_time=elapsed,
            timestamp=get_timestamp()
        )


@router.post("/{session_id}/terminate")
def _terminate_chat_session(session_id: str):
    if session_id in active_sessions:
        del active_sessions[session_id]


@router.post("/{session_id}/message", response_model=ChatMessage)
async def user_message(session_id, message: str = Body()):
    print(message)
    session = _assert_get_session(session_id)

    system_turn = await session.push_user_message(message)
    return system_turn


@router.get("/{session_id}/messages")
async def get_messages(session_id) -> Dialogue:
    session = _assert_get_session(session_id)
    return session.dialog
