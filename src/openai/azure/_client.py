import httpx
from typing import Any, Optional, Dict

from openai import Client, AsyncClient
from ._credential import TokenAuth


class AzureOpenAIClient(Client):

    def __init__(self, *args: Any, base_url: str, credential: Optional["TokenCredential"] = None, api_version: str = '2023-09-01-preview', **kwargs: Any):
        default_query = kwargs.get('default_query', {})
        default_query.setdefault('api-version', api_version)
        kwargs['default_query'] = default_query
        self.credential = credential
        if credential:
            kwargs['api_key'] = 'Placeholder: AAD'
        super().__init__(*args, base_url=base_url, **kwargs)

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {"api-key": self.api_key}

    @property
    def custom_auth(self) -> Optional[httpx.Auth]:
        if self.credential:
            return TokenAuth(self.credential)


class AsyncAzureOpenAIClient(AsyncClient):

    def __init__(self, *args: Any, credential: Optional["TokenCredential"] = None, api_version: str = '2023-09-01-preview', **kwargs: Any):
        default_query = kwargs.get('default_query', {})
        default_query.setdefault('api-version', api_version)
        kwargs['default_query'] = default_query
        self.credential = credential
        if credential:
            kwargs['api_key'] = 'Placeholder: AAD'
        super().__init__(*args, **kwargs)

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {"api-key": self.api_key}

    @property
    def custom_auth(self) -> httpx.Auth | None:
        if self.credential:
            return TokenAuth(self.credential)