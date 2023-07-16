from abc import ABC, abstractmethod
from os import path, getcwd, makedirs
from time import perf_counter
from typing import Callable, TypeAlias

import nanoid
import jsonlines

from core.time import get_timestamp


class RegenerateRequestException(Exception):
    def __init__(self, reason: str):
        self.reason = reason


class DialogueTurn:
    def __init__(self, message: str,
                 is_user: bool = True,
                 id: str = None,
                 timestamp: int = None,
                 processing_time: int | None=None,
                 metadata: dict | None = None
                 ):
        self.message = message
        self.is_user = is_user
        self.id = id if id is not None else nanoid.generate(size=20)
        self.timestamp = timestamp if timestamp is not None else get_timestamp()
        self.processing_time = processing_time
        self.metadata = metadata

Dialogue: TypeAlias = list[DialogueTurn]

class ResponseGenerator(ABC):

    async def initialize(self):
        pass

    def _pre_get_response(self, dialog: Dialogue):
        pass

    @abstractmethod
    async def _get_response_impl(self, dialog: Dialogue) -> tuple[str, dict | None]:
        pass

    async def get_response(self, dialog: Dialogue) -> tuple[str, dict | None, int]:
        start = perf_counter()

        try:
            self._pre_get_response(dialog)
            response, metadata = await self._get_response_impl(dialog)
        except RegenerateRequestException as regen:
            print(f"Regenerate response. Reason: {regen.reason}")
            response, metadata = await self._get_response_impl(dialog)
        except Exception as ex:
            raise ex

        end = perf_counter()

        return response, metadata, int((end - start) * 1000)

class SessionWriterBase(ABC):
    @abstractmethod
    def write_turn(self, session_id: str, turn: DialogueTurn):
        pass

    @abstractmethod
    def read_dialogue(self, session_id: str)->Dialogue:
        pass

class SessionFileWriter(SessionWriterBase):

    @staticmethod
    def __get_dialogue_directory_path(session_id: str)->str:
        p = path.join(getcwd(), "data/sessions/", session_id)
        if not path.exists(p):
            makedirs(p)
        return p

    @staticmethod
    def __get_dialogue_file_path(session_id: str)->str:
        dir_path = SessionFileWriter.__get_dialogue_directory_path(session_id)
        return path.join(dir_path, "dialogue.jsonl")

    def write_turn(self, session_id: str, turn: DialogueTurn):
        with jsonlines.open(self.__get_dialogue_file_path(session_id), 'a') as writer:
            writer.write(turn.__dict__)

    def read_dialogue(self, session_id: str) -> Dialogue | None:
        fp = self.__get_dialogue_file_path(session_id)
        if path.exists(fp):
            with jsonlines.open(fp, "r") as reader:
                return [row for row in reader]
        else:
            return None

session_writer = SessionFileWriter()

class ChatSessionBase:
    def __init__(self, id: str,
                 response_generator: ResponseGenerator,
                 session_writer: SessionWriterBase | None = session_writer
                 ):
        self.id = id
        self._response_generator = response_generator
        self._dialog: Dialogue = []
        self._session_writer = session_writer

    def load(self)->bool:
        if self._session_writer is not None:
            dialogue = self._session_writer.read_dialogue(self.id)
            if dialogue is not None:
                self._dialog = dialogue
                return True
        return False

    @property
    def dialog(self):
        return self._dialog.copy()

    def _push_new_turn(self, turn: DialogueTurn):
        self._dialog.append(turn)
        if self._session_writer is not None: self._session_writer.write_turn(self.id, turn)


# User and system can say one by one.
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
