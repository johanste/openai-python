from __future__ import annotations
import httpx
from openai import BadRequestError
from ._azuremodels import ContentFilterResults


class ContentPolicyError(BadRequestError):
    code: str
    message: str
    content_filter_result: ContentFilterResults

    def __init__(self, message: str, *, response: httpx.Response, body: object | None) -> None:
        super().__init__(message=message, response=response, body=body)
        self.code = body["error"]["code"]
        self.message = body["error"]["message"]
        self.error = body["error"]
        self.content_filter_result = ContentFilterResults.construct(**body["error"]["innererror"]["content_filter_result"])
