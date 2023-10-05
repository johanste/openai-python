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

