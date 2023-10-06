from typing import AsyncGenerator, Generator, Any
import asyncio
import httpx


class TokenCredential:
    """Placeholder/example token credential class
    
       A real implementation would be compatible with e.g. azure-identity and also should be easily
       adaptible to other token credential implementations.
    """
    def __init__(self):
        import azure.identity
        self._credential = azure.identity.DefaultAzureCredential()

    def get_token(self):
        return self._credential.get_token('https://cognitiveservices.azure.com/.default').token


class TokenAuth(httpx.Auth):
    def __init__(self, credential: "TokenCredential") -> None:
        self._credential = credential
        self._async_lock = asyncio.Lock()

    def sync_get_token(self) -> str:
        return self._credential.get_token('https://cognitiveservices.azure.com/.default').token

    def sync_auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, Any, Any]:
        token = self.sync_get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

    async def async_get_token(self) -> str:
        async with self._async_lock:
            return await self._credential.get_token('https://cognitiveservices.azure.com/.default').token

    async def async_auth_flow(self, request: httpx.Request) -> AsyncGenerator[httpx.Request, Any, Any]:
        token = await self.async_get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request
