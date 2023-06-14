import pytest

import openai.client

def test_construct_client(monkeypatch: pytest.MonkeyPatch):
    client = openai.client.OpenAIClient()
    assert client.api_base == openai.api_base
    assert client.api_type == openai.api_type
    assert client.auth.get_token() is None

def test_construct_azure_client(monkeypatch: pytest.MonkeyPatch):
    client = openai.client.OpenAIClient(backend='azure')
    assert client.api_base == openai.api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() is None

def test_construct_azure_client_aad(monkeypatch: pytest.MonkeyPatch):
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)

    client = openai.client.OpenAIClient(backend='azure', auth=openai.client.AzureTokenAuth('dummy'))
    assert client.api_base == openai.api_base
    assert client.api_type == 'azure_ad'
    assert client.auth.get_token() == 'expected token'

def test_construct_azure_client_api_key():
    client = openai.client.OpenAIClient(backend='azure', auth='secret key')
    assert client.api_base == openai.api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() == 'secret key'

def test_construct_openai_client_api_key():
    client = openai.client.OpenAIClient(auth='secret key')
    assert client.api_base == openai.api_base
    assert client.api_type == 'open_ai'
    assert client.auth.get_token() == 'secret key'

def test_make_call_client_aad(monkeypatch: pytest.MonkeyPatch):
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    def mock_embeddings_response(*args, **kwargs):
        assert kwargs.get('deployment_id') == 'das deployment'
        assert kwargs.get('api_version') == openai.client.LATEST_AZURE_API_VERSION
        assert kwargs.get('api_type') == 'azure_ad'

        return {
                "object": "list",
                "data": [
                    {
                    "object": "embedding",
                    "embedding": [
                        0.0023064255,
                        -0.009327292,
                        -0.0028842222,
                    ],
                    "index": 0
                    }
                ],
                "model": "text-embedding-ada-002",
                "usage": {
                    "prompt_tokens": 8,
                    "total_tokens": 8
                }
        }
    
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(backend='azure', auth=openai.client.AzureTokenAuth('dummy'))
    client.embeddings("some data", model='das deployment')
