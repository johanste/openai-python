import os
import pytest
import functools
import openai.client

API_TYPE = ["azure", "openai", "azuredefault"]


API_BASE = os.environ["AZURE_API_BASE"]
AZURE_API_KEY = os.environ["AZURE_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_KEY"]
API_VERSION  = "2023-06-01-preview"
COMPLETION_MODEL = "text-davinci-003"
CHAT_COMPLETION_MODEL = "gpt-35-turbo"
CHAT_COMPLETION_MODEL_OPENAI = "gpt-3.5-turbo"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
IMAGE_PATH = ""
MASK_IMAGE_PATH = ""


def configure_client(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        if api_type == "azure":
            client = openai.client.OpenAIClient(
                api_base=API_BASE,
                auth=AZURE_API_KEY,
                api_version=API_VERSION,
                backend="azure"
            )
        elif api_type == "azuredefault":
            api_type = "azure"
            client = openai.client.OpenAIClient(
                api_base=API_BASE,
                auth="azuredefault",
                api_version=API_VERSION,
                backend="azure"
            )
        elif api_type == "openai":
            client = openai.client.OpenAIClient(
                auth=OPENAI_API_KEY,
                backend="openai"
            )
        kwargs = {"client": client}
        return f(api_type, **kwargs)

    return wrapper


@pytest.fixture
def clear_oai_module(monkeypatch: pytest.MonkeyPatch):
    for key in [ 'api_base', 'api_key', 'api_type', 'api_version']:
        ...
    monkeypatch.setattr(openai, 'api_base', "https://api.openai.com/v1")
    monkeypatch.setattr(openai, 'api_key', None)
    monkeypatch.setattr(openai, 'api_type', "open_ai")
    monkeypatch.setattr(openai, 'api_version', None)

def setup_oai_module(monkeypatch: pytest.MonkeyPatch, **kwargs):
    for n, v in kwargs.items():
        monkeypatch.setattr(openai, n, v)

@pytest.fixture
def embedding_response():
    return   {
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


# MOCK TESTS ------------------------------------------------
def test_construct_client(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    setup_oai_module(monkeypatch, api_key=None)
    client = openai.client.OpenAIClient()
    assert client.api_base == openai.api_base
    assert client.api_type == openai.api_type
    assert client.auth.get_token() is None

def test_construct_azure_client(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    setup_oai_module(monkeypatch, api_key=None, api_base='something different')

    provided_api_base = 'https://contoso.microsoft.com'
    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure')
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() is None

def test_construct_azure_client_aad(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)

    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure', auth=openai.client.AzureTokenAuth(credential='dummy'))
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure_ad'
    assert client.auth.get_token() == 'expected token'

def test_construct_azure_client_api_key(monkeypatch: pytest.MonkeyPatch, clear_oai_module):
    provided_api_base = 'https://contoso.microsoft.com'
    client = openai.client.OpenAIClient(api_base=provided_api_base, backend='azure', auth='secret key')
    assert client.api_base == provided_api_base
    assert client.api_type == 'azure'
    assert client.auth.get_token() == 'secret key'

def test_construct_openai_client_api_key():
    client = openai.client.OpenAIClient(auth='secret key')
    assert client.api_base == openai.api_base
    assert client.api_type == 'open_ai'
    assert client.auth.get_token() == 'secret key'

def test_make_call_client_aad(monkeypatch: pytest.MonkeyPatch, clear_oai_module, embedding_response):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    
    def mock_embeddings_response(*args, **kwargs):
        assert kwargs.get('deployment_id') == 'das deployment'
        assert kwargs.get('api_version') == openai.client.LATEST_AZURE_API_VERSION
        assert kwargs.get('api_type') == 'azure_ad'
        return embedding_response

    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(backend='azure', api_base = provided_api_base, auth=openai.client.AzureTokenAuth(credential='dummy'))
    client.embeddings("some data", model='das deployment')


def test_make_call_client_azure_key(monkeypatch: pytest.MonkeyPatch, clear_oai_module, embedding_response):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    def mock_embeddings_response(*args, **kwargs):
        assert kwargs.get('deployment_id') == 'das deployment'
        assert kwargs.get('api_version') == openai.client.LATEST_AZURE_API_VERSION
        assert kwargs.get('api_type') == 'azure'
        assert kwargs.get('api_key', 'secret key')
        return embedding_response
    
    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(backend='azure', api_base = provided_api_base, auth="secret key")
    client.embeddings("some data", model='das deployment')


def test_make_call_client_oai_key(monkeypatch: pytest.MonkeyPatch, clear_oai_module, embedding_response):
    provided_api_base = 'https://contoso.microsoft.com'
    def mock_get_token(*args, **kwargs):
        return 'expected token'
    def mock_embeddings_response(*args, **kwargs):
        assert kwargs.get('model') == 'das model'
        assert kwargs.get('api_type') == 'open_ai'
        assert kwargs.get('api_key', 'secret key')
        return embedding_response
    

    monkeypatch.setattr(openai.client.AzureTokenAuth, 'get_token', mock_get_token)
    monkeypatch.setattr(openai.Embedding, 'create', mock_embeddings_response)

    client = openai.client.OpenAIClient(auth="secret key")
    client.embeddings("some data", model='das model')


def test_populate_args():
    client = openai.client.OpenAIClient()

    # valid override
    kwargs = {
        "api_base": "expected",
        "api_key": "expected",
        "api_version": "expected",
        "prompt": "expected",
    }

    overrides = {
        "temperature": 0.1
    }

    client._populate_args(kwargs, **overrides)

    assert kwargs == {
        "api_base": "expected",
        "api_key": "expected",
        "api_type": "open_ai",
        "api_version": "expected",
        "prompt": "expected",
        "temperature": 0.1
    }


    # unexpected override by user
    kwargs = {
        "prompt": "expected",
        "api_base": "expected",
        "api_key": "expected",
        "api_type": "expected",
        "api_version": "expected",
        "stream": True
    }

    overrides = {
        "stream": False
    }

    with pytest.raises(TypeError):
        client._populate_args(kwargs, **overrides)

    # attempt to change api_base on per-method call
    kwargs = {
        "prompt": "expected",
        "api_base": "expected",
        "api_key": "expected",
        "api_type": "expected",
        "api_version": "expected",
        "stream": True
    }

    overrides = {
        "api_base": "update",
    }

    with pytest.raises(TypeError):
        client._populate_args(kwargs, **overrides)


def test_normalize_model():
    client = openai.client.OpenAIClient(backend="azure", api_base="azurebase")

    # azure: deployment_id --> deployment_id
    kwargs = {"deployment_id": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"deployment_id": "ada"}

    # azure: engine --> engine
    kwargs = {"engine": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"engine": "ada"}

    # azure: model --> deployment_id (normalized)
    kwargs = {"model": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"deployment_id": "ada"}

    client = openai.client.OpenAIClient(backend="openai")
    # openai: deployment_id --> model
    kwargs = {"deployment_id": "ada"}
    client._normalize_model(kwargs)
    # incorrect arg raised by library
    assert kwargs == {"deployment_id": "ada"}

    # openai: engine --> engine
    kwargs = {"engine": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"engine": "ada"}

    # openai: model --> model
    kwargs = {"model": "ada"}
    client._normalize_model(kwargs)
    assert kwargs == {"model": "ada"}

    # too many args
    kwargs = {"model": "ada", "deployment_id": "ada"}
    with pytest.raises(TypeError):
        client._normalize_model(kwargs)

# LIVE TESTS ------------------------------------------------
# COMPLETION TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
def test_client_completion(api_type, **kwargs):
    client = kwargs.pop("client")
    completion = client.completion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    assert completion


@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
def test_client_completion_stream(api_type, **kwargs):
    client = kwargs.pop("client")
    completion = client.iter_completion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    for c in completion:
        assert c

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
async def test_client_acompletion(api_type, **kwargs):
    client = kwargs.pop("client")
    completion = await client.acompletion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    assert completion

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
async def test_client_acompletion_stream(api_type, **kwargs):
    client = kwargs.pop("client")
    completion = await client.aiter_completion(
        prompt="hello world",
        model=COMPLETION_MODEL
    )
    async for c in completion:
        assert c


# CHAT COMPLETION TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
def test_client_chatcompletion(api_type, **kwargs):
    client = kwargs.pop("client")
    chat_completion = client.chatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if api_type == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    assert chat_completion

@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
def test_client_chat_completion_stream(api_type, **kwargs):
    client = kwargs.pop("client")
    chat_completion = client.iter_chatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if api_type == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    for c in chat_completion:
        assert c

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
async def test_client_achatcompletion(api_type, **kwargs):
    client = kwargs.pop("client")
    chat_completion = await client.achatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if api_type == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    assert chat_completion

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
async def test_client_achat_completion_stream(api_type, **kwargs):
    client = kwargs.pop("client")
    chat_completion = await client.aiter_chatcompletion(
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ],
        model=CHAT_COMPLETION_MODEL if api_type == "azure" else CHAT_COMPLETION_MODEL_OPENAI
    )
    async for c in chat_completion:
        assert c


# EMBEDDING TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
def test_client_embeddings(api_type, **kwargs):
    client = kwargs.pop("client")
    embeddings = client.embeddings(
        input="hello world",
        model=EMBEDDINGS_MODEL
    )
    assert embeddings

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
async def test_client_aembeddings(api_type, **kwargs):
    client = kwargs.pop("client")
    embeddings = await client.aembeddings(
        input="hello world",
        model=EMBEDDINGS_MODEL
    )
    assert embeddings


# IMAGE CREATE TESTS
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
def test_client_image_create(api_type, **kwargs):
    client = kwargs.pop("client")
    image = client.image(
        prompt="A cute baby sea otter",
        n=1
    )
    assert image

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
async def test_client_aimage_create(api_type, **kwargs):
    client = kwargs.pop("client")
    image = await client.aimage(
        prompt="A cute baby sea otter",
        n=1
    )
    assert image


# IMAGE VARIATION TESTS
@pytest.mark.parametrize("api_type", ["openai"])
@configure_client
def test_client_image_variation(api_type, **kwargs):
    client = kwargs.pop("client")
    variation = client.image_variation(
        image=open(IMAGE_PATH, "rb"),
        n=2,
        size="1024x1024"
    )
    assert variation

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", ["openai"])
@configure_client
async def test_client_aimage_variation(api_type, **kwargs):
    client = kwargs.pop("client")
    variation = await client.aimage_variation(
        image=open(IMAGE_PATH, "rb"),
        n=2,
        size="1024x1024"
    )
    assert variation

# IMAGE EDIT TESTS
@pytest.mark.parametrize("api_type", ["openai"])
@configure_client
def test_client_image_edit(api_type, **kwargs):
    client = kwargs.pop("client")
    edit = client.image_edit(
        image=open(IMAGE_PATH, "rb"),
        mask=open(MASK_IMAGE_PATH, "rb"),
        prompt="A cute baby sea otter wearing a beret",
        n=2,
        size="1024x1024"
    )
    assert edit

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", ["openai"])
@configure_client
async def test_client_aimage_edit(api_type, **kwargs):
    client = kwargs.pop("client")
    edit = await client.aimage_edit(
        image=open(IMAGE_PATH, "rb"),
        mask=open(MASK_IMAGE_PATH, "rb"),
        prompt="A cute baby sea otter wearing a beret",
        n=2,
        size="1024x1024"
    )
    assert edit
