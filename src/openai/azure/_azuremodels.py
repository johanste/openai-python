from typing import Optional
from typing_extensions import TypedDict, Literal
from openai._models import BaseModel as BaseModel


class ChatExtensionConfiguration(TypedDict):
    type: str
    parameters: object

# TODO: just copying in from other PR
class ContentFilterResult(BaseModel):
    severity: Literal["safe", "low", "medium", "high"]
    filtered: bool


class Error(BaseModel):
    code: str
    message: str


class ContentFilterResults(BaseModel):
    hate: Optional[ContentFilterResult]
    self_harm: Optional[ContentFilterResult]
    violence: Optional[ContentFilterResult]
    sexual: Optional[ContentFilterResult]
    error: Optional[Error]
