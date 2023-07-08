from abc import ABC, abstractmethod

from core.chatbot import ResponseGenerator, DialogTurn


class StateBasedResponseGenerator(ResponseGenerator, ABC):

    def __init__(self, initial_state: str, initial_state_payload: dict | None = None):
        self.__current_state = initial_state
        self.__current_state_payload : dict | None = initial_state_payload
        self.__current_generator: ResponseGenerator | None = None

    # Return response generator for a state
    @abstractmethod
    async def get_generator(self, state: str, payload: dict | None)->ResponseGenerator:
        pass

    # Calculate the next state based on the current state and the dialog.
    # Return None if the state does not change.
    @abstractmethod
    async def calc_next_state_info(self, current: str, dialog: list[DialogTurn])->tuple[str, dict | None] | None:
        pass

    async def _get_response_impl(self, dialog: list[DialogTurn]) -> str:

        # Calculate state and update response generator if the state was changed:
        next_state_info = await self.calc_next_state_info(self.__current_state, dialog)
        if next_state_info is not None:
            self.__current_state = next_state_info[0]
            self.__current_state_payload = next_state_info[1]
            self.__current_generator = await self.get_generator(self.__current_state, self.__current_state_payload)
        elif self.__current_generator is None:
            self.__current_generator = await self.get_generator(self.__current_state, self.__current_state_payload)

        # Generate response from the child generator:
        return (await self.__current_generator.get_response(dialog))[0]
