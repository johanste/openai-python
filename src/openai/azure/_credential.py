import time
import asyncio
import httpx
from typing import Any, Generator, AsyncGenerator


class TokenAuth(httpx.Auth):
    def __init__(self, credential: "TokenCredential") -> None:
        self._credential = credential
        self._async_lock = asyncio.Lock()
        self.cached_token = None

    def sync_get_token(self) -> str:
        if not self.cached_token or self.cached_token.expires_on - time.time() < 300:
            return self._credential.get_token("https://cognitiveservices.azure.com/.default").token
        return self.cached_token.token

    def sync_auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, Any, Any]:
        token = self.sync_get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

    async def async_get_token(self) -> str:
        async with self._async_lock:
            if not self.cached_token or self.cached_token.expires_on - time.time() < 300:
                return (await self._credential.get_token("https://cognitiveservices.azure.com/.default")).token
        return self.cached_token.token

    async def async_auth_flow(self, request: httpx.Request) -> AsyncGenerator[httpx.Request, Any]:
        token = await self.async_get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request
