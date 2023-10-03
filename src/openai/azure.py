import openai

class TokenCredential:

    def __init__(self):
        import azure.identity
        self._credential = azure.identity.DefaultAzureCredential()

    def get_token(self):
        return self._credential.get_token('https://cognitiveservices.azure.com/.default').token


class AzureClient(openai.Client):

    def __init__(self, *args, deployment: str, credential: TokenCredential | None, api_version: str = '2023-03-15-preview', **kwargs):
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
    

    def request(self, *args, **kwargs):
        if self.deployment:
            args = list(args)
            options = args[1] if len(args) >= 2 else kwargs.get('options')
            options.url = f'openai/deployments/{self.deployment}' + options.url
        return super().request(*args, **kwargs)

