import os
import functools
import pytest
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
        prompt="a cat yowling for food",
        n=1
    )
    assert image

@pytest.mark.asyncio
@pytest.mark.parametrize("api_type", API_TYPE)
@configure_client
async def test_client_aimage_create(api_type, **kwargs):
    client = kwargs.pop("client")
    image = await client.aimage(
        prompt="a cat yowling for food",
        n=1
    )
    assert image
