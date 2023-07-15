from abc import ABC, abstractmethod
from time import perf_counter
from typing import Callable, TypeAlias


class RegenerateRequestException(Exception):
    def __init__(self, reason: str):
        self.reason = reason


class DialogueTurn:
    def __init__(self, message: str, is_user: bool = True):
        self.message = message
        self.is_user = is_user

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


class ChatSessionBase:
    def __init__(self, id: str, response_generator: ResponseGenerator):
        self.id = id
        self._response_generator = response_generator
        self._dialog: Dialogue = []

    @property
    def dialog(self):
        return self._dialog.copy()

    def _push_new_turn(self, turn: DialogueTurn):
        self._dialog.append(turn)


# User and system can say one by one.
class TurnTakingChatSession(ChatSessionBase):

    async def initialize(self) -> tuple[str, dict | None, int]:
        self._dialog.clear()
        initial_message, metadata, elapsed = await self._response_generator.get_response(self._dialog)
        self._push_new_turn(DialogueTurn(initial_message, is_user=False))
        return initial_message, metadata, elapsed

    async def push_user_message(self, message: str) -> tuple[str, dict | None, int]:
        self._push_new_turn(DialogueTurn(message, is_user=True))
        system_message, metadata, elapsed = await self._response_generator.get_response(self._dialog)
        self._push_new_turn(DialogueTurn(system_message, is_user=False))
        return system_message, metadata, elapsed


class MultiAgentChatSession(ChatSessionBase):
    def __init__(self, id: str,
                 response_generator: ResponseGenerator,
                 user_generator: ResponseGenerator):
        super().__init__(id, response_generator)
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
                                    on_message: Callable[[DialogueTurn, dict | None, int], None]
                                    ) -> list[tuple[DialogueTurn, dict | None, int]]:
        self.dialog.clear()
        self.__is_running = True
        self.__is_stop_requested = False

        dialog_with_metadata = []
        turn_count = 0
        while self.__is_stop_requested == False and max_turns > turn_count:
            turn_count += 1
            system_message, payload, elapsed = await self._response_generator.get_response(self.dialog)
            system_turn = DialogueTurn(system_message, False)
            self._push_new_turn(system_turn)
            dialog_with_metadata.append((system_turn, payload, elapsed))
            on_message(system_turn, payload, elapsed)

            role_reverted_dialog = [DialogueTurn(message=turn.message, is_user=turn.is_user is False) for turn in
                                    self.dialog]

            user_message, payload, elapsed = await self.__user_generator.get_response(role_reverted_dialog)

            user_turn = DialogueTurn(user_message, True)
            self._push_new_turn(user_turn)
            dialog_with_metadata.append((user_turn, payload, elapsed))
            on_message(user_turn, payload, elapsed)

        return dialog_with_metadata
