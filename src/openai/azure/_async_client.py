from __future__ import annotations

from typing_extensions import Literal, override
from typing import Any, Callable, cast, List, Mapping, Dict, Optional, overload, Type, Union
import time

import httpx

from openai import AsyncClient, OpenAIError
from openai.resources.chat import AsyncChat, AsyncCompletions
from openai.types import ImagesResponse
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion, ChatCompletionChunk
from openai.types.chat.completion_create_params import FunctionCall, Function
from openai.types.completion import Completion as _Completion

# These types are needed for correct typing of overrides
from openai._types import NotGiven, NOT_GIVEN, Headers, Query, Body, ResponseT

# These are types used in the public API surface area that are not exported as public
from openai._models import FinalRequestOptions
from openai._streaming import AsyncStream

# Azure specific types
from ._credential import TokenCredential, TokenAuth
from ._azuremodels import ChatExtensionConfiguration, AzureChatCompletion, AzureChatCompletionChunk, Completion

TIMEOUT_SECS = 600

class AsyncAzureChat(AsyncChat):

    @property
    def completions(self) -> "AsyncAzureCompletions":
        return self._completions
    
    def __init__(self, client: "AsyncAzureOpenAIClient"):
        self._completions = AsyncAzureCompletions(client)

class AsyncAzureCompletions(AsyncCompletions):
    
    @overload
    async def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Union[
            str,
            Literal[
                "gpt-4",
                "gpt-4-0314",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0314",
                "gpt-4-32k-0613",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k-0613",
            ],
        ],
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: FunctionCall | NotGiven = NOT_GIVEN,
        functions: List[Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        data_sources: List[ChatExtensionConfiguration] | NotGiven = NOT_GIVEN, # TODO
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> AzureChatCompletion:
        """
        Creates a model response for the given chat conversation.

        Args:
          messages: A list of messages comprising the conversation so far.
              [Example Python code](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb).

          model: ID of the model to use. See the
              [model endpoint compatibility](https://platform.openai.com/docs/models/model-endpoint-compatibility)
              table for details on which models work with the Chat API.

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              [See more information about frequency and presence penalties.](https://platform.openai.com/docs/guides/gpt/parameter-details)

          function_call: Controls how the model responds to function calls. `none` means the model does
              not call a function, and responds to the end-user. `auto` means the model can
              pick between an end-user or calling a function. Specifying a particular function
              via `{"name": "my_function"}` forces the model to call that function. `none` is
              the default when no functions are present. `auto` is the default if functions
              are present.

          functions: A list of functions the model may generate JSON inputs for.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion.

              Accepts a json object that maps tokens (specified by their token ID in the
              tokenizer) to an associated bias value from -100 to 100. Mathematically, the
              bias is added to the logits generated by the model prior to sampling. The exact
              effect will vary per model, but values between -1 and 1 should decrease or
              increase likelihood of selection; values like -100 or 100 should result in a ban
              or exclusive selection of the relevant token.

          max_tokens: The maximum number of [tokens](/tokenizer) to generate in the chat completion.

              The total length of input tokens and generated tokens is limited by the model's
              context length.
              [Example Python code](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
              for counting tokens.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              [See more information about frequency and presence penalties.](https://platform.openai.com/docs/guides/gpt/parameter-details)

          stop: Up to 4 sequences where the API will stop generating further tokens.

          stream: If set, partial message deltas will be sent, like in ChatGPT. Tokens will be
              sent as data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.
              [Example Python code](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb).

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or `top_p` but not both.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Union[
            str,
            Literal[
                "gpt-4",
                "gpt-4-0314",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0314",
                "gpt-4-32k-0613",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k-0613",
            ],
        ],
        stream: Literal[True],
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: FunctionCall | NotGiven = NOT_GIVEN,
        functions: List[Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        data_sources: List[ChatExtensionConfiguration] | NotGiven = NOT_GIVEN, # TODO
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[AzureChatCompletionChunk]:
        """
        Creates a model response for the given chat conversation.

        Args:
          messages: A list of messages comprising the conversation so far.
              [Example Python code](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb).

          model: ID of the model to use. See the
              [model endpoint compatibility](https://platform.openai.com/docs/models/model-endpoint-compatibility)
              table for details on which models work with the Chat API.

          stream: If set, partial message deltas will be sent, like in ChatGPT. Tokens will be
              sent as data-only
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format)
              as they become available, with the stream terminated by a `data: [DONE]`
              message.
              [Example Python code](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb).

          frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their
              existing frequency in the text so far, decreasing the model's likelihood to
              repeat the same line verbatim.

              [See more information about frequency and presence penalties.](https://platform.openai.com/docs/guides/gpt/parameter-details)

          function_call: Controls how the model responds to function calls. `none` means the model does
              not call a function, and responds to the end-user. `auto` means the model can
              pick between an end-user or calling a function. Specifying a particular function
              via `{"name": "my_function"}` forces the model to call that function. `none` is
              the default when no functions are present. `auto` is the default if functions
              are present.

          functions: A list of functions the model may generate JSON inputs for.

          logit_bias: Modify the likelihood of specified tokens appearing in the completion.

              Accepts a json object that maps tokens (specified by their token ID in the
              tokenizer) to an associated bias value from -100 to 100. Mathematically, the
              bias is added to the logits generated by the model prior to sampling. The exact
              effect will vary per model, but values between -1 and 1 should decrease or
              increase likelihood of selection; values like -100 or 100 should result in a ban
              or exclusive selection of the relevant token.

          max_tokens: The maximum number of [tokens](/tokenizer) to generate in the chat completion.

              The total length of input tokens and generated tokens is limited by the model's
              context length.
              [Example Python code](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
              for counting tokens.

          n: How many chat completion choices to generate for each input message.

          presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on
              whether they appear in the text so far, increasing the model's likelihood to
              talk about new topics.

              [See more information about frequency and presence penalties.](https://platform.openai.com/docs/guides/gpt/parameter-details)

          stop: Up to 4 sequences where the API will stop generating further tokens.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic.

              We generally recommend altering this or `top_p` but not both.

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...
    @override
    async def create(
        self,
        *,
        messages: List[ChatCompletionMessageParam],
        model: Union[
            str,
            Literal[
                "gpt-4",
                "gpt-4-0314",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0314",
                "gpt-4-32k-0613",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-16k-0613",
            ],
        ],
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: FunctionCall | NotGiven = NOT_GIVEN,
        functions: List[Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        data_sources: List[ChatExtensionConfiguration] | NotGiven = NOT_GIVEN, # TODO
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> AzureChatCompletion | AsyncStream[AzureChatCompletionChunk]:
        if data_sources:
            if extra_body is None:
                extra_body= {}
            cast(Dict[str, Any], extra_body)['dataSources'] = data_sources
        stream_dict: Dict[str, Literal[True]] = { # TODO: pylance is upset if I pass through the parameter value. Overload + override combination is problematic
            "stream": True
        } if stream else {}
        response = cast(
            Union[ChatCompletion, ChatCompletionChunk],
            await super().create(
                messages=messages,
                model=model,
                frequency_penalty = frequency_penalty,
                function_call=function_call,
                functions=functions,
                logit_bias=logit_bias,
                max_tokens=max_tokens,
                n=n,
                presence_penalty=presence_penalty,
                stop=stop,
                **stream_dict,
                temperature=temperature,
                top_p=top_p,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout
            )
        )
        if isinstance(response, AsyncStream):
            response._cast_to = AzureChatCompletionChunk  # or rebuild the stream?
        else:
            response_json = response.model_dump(mode="json")
            response = AzureChatCompletion.construct(**response_json)
        return response  # type: ignore


class AsyncAzureOpenAIClient(AsyncClient):

    @property
    @override
    def chat(self) -> AsyncAzureChat:
        return self._chat
    
    def __init__(self, *args: Any, credential: Optional["TokenCredential"] = None, api_version: str = '2023-09-01-preview', **kwargs: Any):
        default_query = kwargs.get('default_query', {})
        default_query.setdefault('api-version', api_version)
        kwargs['default_query'] = default_query
        self.credential = credential
        if credential:
            kwargs['api_key'] = 'Placeholder: AAD' # TODO: There is an assumption/validation there is always an API key.
        super().__init__(*args, **kwargs)
        self._chat = AsyncAzureChat(self)

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {"api-key": self.api_key}

    @property
    def custom_auth(self) -> httpx.Auth | None:
        if self.credential:
            return TokenAuth(self.credential)

    def _check_polling_response(self, response: httpx.Response, predicate: Callable[[httpx.Response], bool]) -> bool:
        if not predicate(response):
            return False
        error_data = response.json()['error']
        message: str = cast(str, error_data.get('message', 'Operation failed'))
        code = error_data.get('code')
        raise OpenAIError(f'Error: {message} ({code})')

    async def _poll(
        self,
        method: str,
        url: str,
        until: Callable[[httpx.Response], bool],
        failed: Callable[[httpx.Response], bool],
        interval: Optional[float] = None,
        delay: Optional[float] = None,
    ) -> ImagesResponse:
        if delay:
            time.sleep(delay)

        opts = FinalRequestOptions.construct(method=method, url=url)
        response = await super().request(httpx.Response, opts)
        self._check_polling_response(response, failed)
        start_time = time.time()
        while not until(response):
            if time.time() - start_time > TIMEOUT_SECS:
                raise Exception("Operation polling timed out.") # TODO: Fix up exception type. 

            time.sleep(interval or int(response.headers.get("retry-after")) or 10)
            response = await super().request(httpx.Response, opts)
            self._check_polling_response(response, failed)

        response_json = response.json()
        return ImagesResponse.construct(**response_json["result"])

    # NOTE: We override the internal method because `@overrid`ing `@overload`ed methods and keeping typing happy is a pain. Most typing tools are lacking...
    async def _request(self, cast_to: Type[ResponseT], options: FinalRequestOptions, **kwargs: Any) -> Any:
        if options.url == "/images/generations":
            options.url = "openai/images/generations:submit"
            response = await super()._request(cast_to=cast_to, options=options, **kwargs)
            model_extra = cast(Mapping[str, Any], getattr(response, 'model_extra')) or {}
            operation_id = cast(str, model_extra['id'])
            return await self._poll(
                "get", f"openai/operations/images/{operation_id}",
                until=lambda response: response.json()["status"] in ["succeeded"],
                failed=lambda response: response.json()["status"] in ["failed"],
            )
        if isinstance(options.json_data, Mapping):
            model = cast(str, options.json_data["model"])
            if not options.url.startswith(f'openai/deployments/{model}'):
                if options.extra_json and options.extra_json.get("dataSources"):
                    options.url = f'openai/deployments/{model}/extensions' + options.url
                else:
                    options.url = f'openai/deployments/{model}' + options.url
        if options.url.startswith(("/models", "/fine_tuning", "/files", "/fine-tunes")):
            options.url = f"openai{options.url}"
        response = await super()._request(cast_to=cast_to, options=options, **kwargs)
        # TODO: cheating here by "aliasing" azure's completion type to a Completion
        # because I don't want to redefine the method on the client
        if isinstance(response, AsyncStream):
            if isinstance(response._cast_to, type(_Completion)):
                response._cast_to = Completion
        if isinstance(response, _Completion):
            response_json = response.model_dump(mode="json")
            response = Completion.construct(**response_json)
        return response  # type: ignore
