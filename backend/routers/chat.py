from typing import Optional, Any

from fastapi import APIRouter, HTTPException, Body, Path
from pydantic import BaseModel
from starlette import status

from app.response_generator import EmotionChatbotResponseGenerator
from core.chatbot import TurnTakingChatSession, Dialogue, session_writer, DialogueTurn
from core.time import get_timestamp

router = APIRouter()

active_sessions: dict[str, TurnTakingChatSession] = dict()


def _restore_session_instance(session_id: str) -> TurnTakingChatSession | None:
    if session_writer.exists(session_id):
        session = TurnTakingChatSession(session_id, EmotionChatbotResponseGenerator())
        if session.load():
            return session
        else:
            return None
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
    id: str
    message: str
    is_user: bool
    metadata: Optional[dict]
    processing_time: Optional[float | None]
    timestamp: int

    @staticmethod
    def from_turn(turn: DialogueTurn)->Any:
        return ChatMessage(
            id=turn.id,
            message=turn.message,
            is_user=turn.is_user,
            metadata=turn.metadata,
            processing_time=turn.processing_time,
            timestamp=turn.timestamp
        )


class ChatSessionInitializeArgs(BaseModel):
    user_name: str
    user_age: int


@router.get("/sessions/{session_id}/messages")
async def get_messages(session_id: str = Path(...)) -> list[ChatMessage]:
    session = _assert_get_session(session_id)
    return [ChatMessage.from_turn(turn) for turn in session.dialog]


@router.post("/sessions/{session_id}/initialize", response_model=ChatMessage)
async def _initialize_chat_session(args: ChatSessionInitializeArgs, session_id: str = Path(...)):
    if session_id in active_sessions and active_sessions[session_id] is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate active session ID."
        )
    else:
        new_session = TurnTakingChatSession(session_id,
                                            EmotionChatbotResponseGenerator(user_name=args.user_name,
                                                                            user_age=args.user_age))
        active_sessions[session_id] = new_session
        system_turn = await new_session.initialize()

        new_session.save()

        return ChatMessage.from_turn(system_turn)


@router.post("/sessions/{session_id}/terminate")
def _terminate_chat_session(session_id: str = Path(...)):
    if session_id in active_sessions:
        del active_sessions[session_id]


@router.post("/sessions/{session_id}/message", response_model=ChatMessage)
async def user_message(args: ChatMessage, session_id:str = Path(...)):
    session = _assert_get_session(session_id)

    system_turn = await session.push_user_message(DialogueTurn(
        message=args.message,
        metadata=args.metadata,
        id=args.id,
        is_user=args.is_user,
        processing_time=args.processing_time
    ))
    return ChatMessage.from_turn(system_turn)