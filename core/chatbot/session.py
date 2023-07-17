from abc import ABC, abstractmethod
from typing import Callable

from .generator import ResponseGenerator
from .types import Dialogue, DialogueTurn
from .session_writer import SessionWriterBase, session_writer


class ChatSessionBase(ABC):
    def __init__(self, id: str,
                 response_generator: ResponseGenerator,
                 session_writer: SessionWriterBase | None = session_writer
                 ):
        self.id = id
        self._response_generator = response_generator
        self._dialog: Dialogue = []
        self._session_writer = session_writer

    def __del__(self):
        if self._session_writer is not None:
            print("======Write session info.======")
            self._session_writer.write_session_info(self.id, self._to_info_dict())

    def load(self) -> bool:
        if self._session_writer is not None and self._session_writer.exists(self.id):
            dialogue = self._session_writer.read_dialogue(self.id)
            if dialogue is not None:
                self._dialog = dialogue

            session_info = self._session_writer.read_session_info(self.id)
            if session_info is not None:
                self._restore_from_info_dict(session_info)
            return True
        else:
            return False

    def save(self) -> bool:
        if self._session_writer is not None:
            session_info = self._to_info_dict()
            self._session_writer.write_session_info(self.id, session_info)
            return True
        else:
            return False

    def _restore_from_info_dict(self, data: dict):
        if "response_generator" in data:
            self._response_generator.restore_from_json(data["response_generator"])

    def _to_info_dict(self)->dict:
        parcel = dict(id=self.id, turns=len(self.dialog), response_generator = dict())
        self._response_generator.write_to_json(parcel["response_generator"])
        return parcel

    @property
    def dialog(self):
        return self._dialog.copy()

    def _push_new_turn(self, turn: DialogueTurn):
        self._dialog.append(turn)
        if self._session_writer is not None:
            self._session_writer.write_turn(self.id, turn)
        self.save()


class TurnTakingChatSession(ChatSessionBase):

    async def initialize(self) -> DialogueTurn:
        self._dialog.clear()
        initial_message, metadata, elapsed = await self._response_generator.get_response(self._dialog)
        system_turn = DialogueTurn(initial_message, is_user=False, processing_time=elapsed, metadata=metadata)
        self._push_new_turn(system_turn)
        return system_turn

    async def push_user_message(self, message: str) -> DialogueTurn:
        self._push_new_turn(DialogueTurn(message, is_user=True))
        system_message, metadata, elapsed = await self._response_generator.get_response(self._dialog)
        system_turn = DialogueTurn(system_message, is_user=False, processing_time=elapsed, metadata=metadata)
        self._push_new_turn(system_turn)
        return system_turn


class MultiAgentChatSession(ChatSessionBase):

    def __init__(self, id: str,
                 response_generator: ResponseGenerator,
                 user_generator: ResponseGenerator,
                 session_writer: SessionWriterBase | None = session_writer
                 ):
        super().__init__(id, response_generator, session_writer)
        self.__user_generator = user_generator

        self.__is_running = False
        self.__is_stop_requested = False

    def _restore_from_info_dict(self, data: dict):
        super()._restore_from_info_dict(data)
        if "user_generator" in data:
            self.__user_generator.restore_from_json(data["user_generator"])

    def _to_info_dict(self) -> dict:
        parcel = super()._to_info_dict()
        user_gen_parcel = dict()
        self.__user_generator.write_to_json(user_gen_parcel)
        parcel["user_generator"] = user_gen_parcel

        return parcel

    @property
    def is_running(self) -> bool:
        return self.__is_running

    def stop(self):
        if self.__is_running:
            self.__is_stop_requested = True
        else:
            self.__is_stop_requested = False

    async def generate_conversation(self,
                                    max_turns: int,
                                    on_message: Callable[[DialogueTurn], None]
                                    ) -> Dialogue:
        self.dialog.clear()
        self.__is_running = True
        self.__is_stop_requested = False

        turn_count = 0
        while self.__is_stop_requested == False and max_turns > turn_count:
            turn_count += 1
            system_message, payload, elapsed = await self._response_generator.get_response(self.dialog)
            system_turn = DialogueTurn(system_message, False, processing_time=elapsed, metadata=payload)
            self._push_new_turn(system_turn)
            on_message(system_turn)

            role_reverted_dialog = [DialogueTurn(message=turn.message, is_user=turn.is_user is False) for turn in
                                    self.dialog]

            user_message, payload, elapsed = await self.__user_generator.get_response(role_reverted_dialog)

            user_turn = DialogueTurn(user_message, True, processing_time=elapsed, metadata=payload)
            self._push_new_turn(user_turn)
            on_message(user_turn)

        return self.dialog
