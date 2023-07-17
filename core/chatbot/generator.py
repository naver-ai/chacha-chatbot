from abc import ABC, abstractmethod
from time import perf_counter

from .types import Dialogue, RegenerateRequestException


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

    @abstractmethod
    def write_to_json(self, parcel: dict):
        pass

    @abstractmethod
    def restore_from_json(self, parcel: dict):
        pass
