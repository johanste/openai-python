import logging
import typing

if typing.TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

try:
    from requests import PreparedRequest, Response, Session
    from requests.adapters import HTTPAdapter
except ModuleNotFoundError:
    print("You have to install the `requests` library (pip install requests) in order to use easyaz.requests")
    exit(-1)

import azure.identity
import openai

log = logging.getLogger(__name__)

def init(endpoint: str, *, credential=None, api_version='2022-12-01'):
    openai.api_type = 'azure_ad'
    openai.api_key = 'dummy'
    openai.api_base = endpoint
    openai.api_version = api_version

    if not credential:
        credential = azure.identity.DefaultAzureCredential()

    session = Session()
    adapter = AzHttpAdapter(credential=credential, scopes=[ "https://cognitiveservices.azure.com/.default" ])
    session.mount(endpoint, adapter)
    openai.requestssession.set(session)


class AzHttpAdapter(HTTPAdapter):
    
    def __init__(self, *, credential: "TokenCredential", scopes: list[str] | str, **kwargs: typing.Any):
        super().__init__(**kwargs)
        self.credential = credential
        self.scopes = [ scopes ] if isinstance(scopes, str) else scopes
        self.max_recurse = 1

    def send(self, request: PreparedRequest, stream: bool = ..., timeout: None | float | tuple[float, float] | tuple[float, None] = ..., verify: bool | str = ..., cert: None | bytes | str | tuple[bytes | str, bytes | str] = ..., proxies: typing.Mapping[str, str] | None = ..., *, recurse:int=0) -> Response:
        initial_response = super().send(request, stream, timeout, verify, cert, proxies)
        if initial_response.status_code != 401 or recurse > self.max_recurse:
            # Only do the auth dance if we are challenged...
            return initial_response
        
        log.info('Received 401 response from service - grabbing a token!')

        # Drain response
        initial_response.content 

        # Fill in a token
        new_request = request.copy()
        access_token = self.credential.get_token(*self.scopes) # TODO: sniff out claims from response
        new_request.headers['Authorization'] = 'Bearer ' + access_token.token
        return self.send(new_request, stream, timeout, verify, cert, proxies, recurse=recurse + 1)