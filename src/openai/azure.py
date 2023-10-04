import openai
import time
import httpx

TIMEOUT_SECS = 600

class TokenCredential:

    def __init__(self):
        import azure.identity
        self._credential = azure.identity.DefaultAzureCredential()

    def get_token(self):
        return self._credential.get_token('https://cognitiveservices.azure.com/.default').token


class AzureClient(openai.Client):

    def __init__(self, *args, deployment: str = "", credential: TokenCredential | None = None, api_version: str = '2023-09-01-preview', **kwargs):
        default_query = kwargs.get('default_query', {})
        default_query.setdefault('api-version', api_version)
        kwargs['default_query'] = default_query
        self.credential = credential
        if credential:
            kwargs['api_key'] = 'Placeholder: AAD'
        super().__init__(*args, **kwargs)
        self.deployment = deployment

    @property
    def auth_headers(self) -> dict[str, str]:
        if self.credential:
            return { 'Authorization': f'Bearer {self.credential.get_token()}'}
        return {"api-key": self.api_key}

    def _check_polling_response(self, response, predicate):
        if not predicate(response):
            return
        error_data = response.json()['error']
        message = error_data.get('message', 'Operation failed')
        code = error_data.get('code')
        raise openai.OpenAIError(message=message, code=code)

    def _poll(
        self,
        method,
        url,
        until,
        failed,
        cast_to,
        interval = None,
        delay = None,
    ):
        if delay:
            time.sleep(delay)

        opts = openai._models.FinalRequestOptions.construct(method=method, url=url)
        response = super().request(cast_to, opts)
        self._check_polling_response(response, failed)
        start_time = time.time()
        while not until(response):
            if time.time() - start_time > TIMEOUT_SECS:
                raise openai.Timeout("Operation polling timed out.")

            time.sleep(interval or int(response.headers.get("retry-after")) or 10)
            response = super().request(cast_to, opts)
            self._check_polling_response(response, failed)

        response_json = response.json()
        return openai.types.ImagesResponse.construct(**response_json["result"])

    def request(self, *args, **kwargs):
        args = list(args)
        options = args[1] if len(args) >= 2 else kwargs.get('options')
        if options.url == "/images/generations":
            options.url = "openai/images/generations:submit"
            response = super().request(*args, **kwargs)
            operation_id = response.model_extra['id']
            return self._poll(
                "get", f"openai/operations/images/{operation_id}", cast_to=httpx.Response,
                until=lambda response: response.json()["status"] in ["succeeded"],
                failed=lambda response: response.json()["status"] in ["failed"],
            )
        elif options.extra_json and options.extra_json.get("dataSources"):
            model = options.json_data["model"]
            options.url = f'openai/deployments/{model}/extensions' + options.url
        else:
            model = options.json_data["model"]
            options.url = f'openai/deployments/{model}' + options.url
        return super().request(*args, **kwargs)



class AzureAsyncClient(openai.AsyncClient):

    def __init__(self, *args, deployment: str = "", credential: TokenCredential | None = None, api_version: str = '2023-09-01-preview', **kwargs):
        default_query = kwargs.get('default_query', {})
        default_query.setdefault('api-version', api_version)
        kwargs['default_query'] = default_query
        self.credential = credential
        if credential:
            kwargs['api_key'] = 'Placeholder: AAD'
        super().__init__(*args, **kwargs)
        self.deployment = deployment

    @property
    def auth_headers(self) -> dict[str, str]:
        if self.credential:
            return { 'Authorization': f'Bearer {self.credential.get_token()}'}
        return {"api-key": self.api_key}

    def _check_polling_response(self, response, predicate):
        if not predicate(response):
            return
        error_data = response.json()['error']
        message = error_data.get('message', 'Operation failed')
        code = error_data.get('code')
        raise openai.OpenAIError(message=message, code=code)

    async def _poll(
        self,
        method,
        url,
        until,
        failed,
        cast_to,
        interval = None,
        delay = None,
    ):
        if delay:
            time.sleep(delay)

        opts = openai._models.FinalRequestOptions.construct(method=method, url=url)
        response = await super().request(cast_to, opts)
        self._check_polling_response(response, failed)
        start_time = time.time()
        while not until(response):
            if time.time() - start_time > TIMEOUT_SECS:
                raise openai.Timeout("Operation polling timed out.")

            time.sleep(interval or int(response.headers.get("retry-after")) or 10)
            response = await super().request(cast_to, opts)
            self._check_polling_response(response, failed)

        response_json = response.json()
        return openai.types.ImagesResponse.construct(**response_json["result"])

    async def request(self, *args, **kwargs):
        args = list(args)
        options = args[1] if len(args) >= 2 else kwargs.get('options')
        if options.url == "/images/generations":
            options.url = "openai/images/generations:submit"
            response = await super().request(*args, **kwargs)
            operation_id = response.model_extra['id']
            return await self._poll(
                "get", f"openai/operations/images/{operation_id}", cast_to=httpx.Response,
                until=lambda response: response.json()["status"] in ["succeeded"],
                failed=lambda response: response.json()["status"] in ["failed"],
            )
        elif options.extra_json and options.extra_json.get("dataSources"):
            model = options.json_data["model"]
            options.url = f'openai/deployments/{model}/extensions' + options.url
        else:
            model = options.json_data["model"]
            options.url = f'openai/deployments/{model}' + options.url
        return await super().request(*args, **kwargs)

