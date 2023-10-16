# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import TYPE_CHECKING

from ..._resource import SyncAPIResource, AsyncAPIResource
from .completions import Completions, AsyncCompletions

if TYPE_CHECKING:
    from ..._client import OpenAI, AsyncOpenAI

__all__ = ["Chat", "AsyncChat"]


class Chat(SyncAPIResource):

    @property
    def completions(self) -> Completions:
        return self._completions

    def __init__(self, client: OpenAI) -> None:
        super().__init__(client)
        self._completions = Completions(client)


class AsyncChat(AsyncAPIResource):
    
    @property
    def completions(self) -> AsyncCompletions:
        return self._completions
    
    def __init__(self, client: AsyncOpenAI) -> None:
        super().__init__(client)
        self._completions = AsyncCompletions(client)
