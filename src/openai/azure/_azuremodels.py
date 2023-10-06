from typing import List, Optional
from typing_extensions import TypedDict, Literal
from openai._models import BaseModel as BaseModel

from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice as ChatChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta, Choice as ChatChoiceDelta
from openai.types.completion import Completion as _Completion
from openai.types.completion_choice import CompletionChoice as _CompletionChoice


AzureChatCompletionRole = Literal["system", "user", "assistant", "function", "tool"]


class ChatExtensionConfiguration(TypedDict):
    type: Literal["AzureCognitiveSearch"]
    parameters: object


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


class PromptFilterResult(BaseModel):
    prompt_index: int
    content_filter_results: Optional[ContentFilterResults]


class AzureChatExtensionsMessageContext(BaseModel):
    messages: Optional[List[ChatCompletionMessage]]


class AzureChatCompletionMessage(ChatCompletionMessage):
    context: Optional[AzureChatExtensionsMessageContext]
    role: AzureChatCompletionRole  # type: ignore


class AzureChatCompletionChoice(ChatChoice):
    content_filter_results: Optional[ContentFilterResults]
    message: AzureChatCompletionMessage  # type: ignore


class AzureChatCompletion(ChatCompletion):
    choices: List[AzureChatCompletionChoice]  # type: ignore
    prompt_filter_results: Optional[List[PromptFilterResult]]


class AzureChoiceDelta(ChoiceDelta):
    context: Optional[AzureChatExtensionsMessageContext]


class AzureChatCompletionChoiceDelta(ChatChoiceDelta):
    delta: AzureChoiceDelta  # type: ignore
    content_filter_results: Optional[ContentFilterResults]


class AzureChatCompletionChunk(ChatCompletionChunk):
    choices: List[AzureChatCompletionChoiceDelta]  # type: ignore
    prompt_filter_results: Optional[List[PromptFilterResult]]


class CompletionChoice(_CompletionChoice):
    content_filter_results: Optional[ContentFilterResults]


class Completion(_Completion):
    choices: List[CompletionChoice]  # type: ignore
    prompt_filter_results: Optional[List[PromptFilterResult]]
