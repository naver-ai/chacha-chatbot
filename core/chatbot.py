from time import perf_counter
from abc import ABC, abstractmethod


class RegenerateRequestException(Exception):
    def __init__(self, reason: str):
        self.reason = reason


class DialogTurn:
    def __init__(self, message: str, is_user: bool = True):
        self.message = message
        self.is_user = is_user


class ResponseGenerator(ABC):

    async def initialize(self):
        pass

    def _pre_get_response(self, dialog: list[DialogTurn]):
        pass

    @abstractmethod
    async def _get_response_impl(self, dialog: list[DialogTurn]) -> str:
        pass

    async def get_response(self, dialog: list[DialogTurn]) -> tuple[str, int]:
        start = perf_counter()

        try:
            self._pre_get_response(dialog)
            response = await self._get_response_impl(dialog)
        except RegenerateRequestException as regen:
            print(f"Regenerate response. Reason: {regen.reason}")
            response = await self._get_response_impl(dialog)
        except Exception as ex:
            raise ex

        end = perf_counter()

        return response, int((end - start) * 1000)


class ChatSessionBase:
    def __init__(self, id: str, response_generator: ResponseGenerator):
        self.id = id
        self._response_generator = response_generator
        self._dialog: list[DialogTurn] = []

    @property
    def dialog(self):
        return self._dialog.copy()


# User and system can say one by one.
class TurnTakingChatSession(ChatSessionBase):
    def _push_new_turn(self, turn: DialogTurn):
        self._dialog.append(turn)

    async def initialize(self) -> str:
        self._dialog.clear()
        initial_message, elapsed = await self._response_generator.get_response(self._dialog)
        self._push_new_turn(DialogTurn(initial_message, is_user=False))
        return initial_message

    async def push_user_message(self, message: str) -> str:
        self._push_new_turn(DialogTurn(message, is_user=True))
        system_message, elapsed = await self._response_generator.get_response(self._dialog)
        self._push_new_turn(DialogTurn(system_message, is_user=False))
        return system_message
