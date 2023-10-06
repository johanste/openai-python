from typing import List, Optional
from typing_extensions import TypedDict
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice as ChatChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta, Choice as ChatChoiceDelta
from openai._models import BaseModel


class ChatExtensionConfiguration(TypedDict):
    type: str
    parameters: object


class ContentFilterResult(BaseModel):
    severity: str
    filtered: bool


class ContentFilterResults(BaseModel):
    hate: ContentFilterResult
    self_harm: ContentFilterResult
    violence: ContentFilterResult
    sexual: ContentFilterResult

class PromptFilterResult(BaseModel):
    prompt_index: int
    content_filter_results: ContentFilterResults

class AzureChatExtensionsMessageContext(BaseModel):
    messages: List[ChatCompletionMessage]


class AzureChatCompletionMessage(ChatCompletionMessage):
    context: Optional[AzureChatExtensionsMessageContext] = None


class AzureChatCompletionChoice(ChatChoice):
    content_filter_results: Optional[ContentFilterResults] = None
    message: AzureChatCompletionMessage  # TODO typing hates this


class AzureChatCompletion(ChatCompletion):
    choices: List[AzureChatCompletionChoice]  # TODO typing hates this
    # TODO service is still returning prompt_filter_results OR prompt_annotations
    # prompt_filter_results: Optional[List[PromptFilterResult]] = None  
    prompt_annotations: Optional[List[PromptFilterResult]] = None

class AzureChoiceDelta(ChoiceDelta):
    context: Optional[AzureChatExtensionsMessageContext] = None


class AzureChoice(ChatChoiceDelta):
    delta: AzureChoiceDelta  # TODO typing hates this


class AzureChatCompletionChunk(ChatCompletionChunk):
    choices: List[AzureChoice]  # TODO typing hates this
    prompt_filter_results: Optional[List[PromptFilterResult]] = None