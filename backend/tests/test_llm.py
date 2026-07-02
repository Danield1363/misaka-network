import pytest
import asyncio
from app.llm.gateway import LLMGateway
from app.llm.errors import ProviderNotFoundError, ProviderUnavailableError
from app.llm.providers.mock import MockProvider


@pytest.fixture
def gateway():
    return LLMGateway()


@pytest.fixture
def mock_provider():
    return MockProvider()


def test_gateway_has_providers(gateway):
    assert "mock" in gateway.providers
    assert "gemini" in gateway.providers


def test_gateway_default_provider(gateway):
    assert gateway.default_provider == "mock"


def test_get_mock_provider(gateway):
    provider = gateway.get_provider("mock")
    assert provider.name == "mock"
    assert provider.is_available()


def test_get_default_provider(gateway):
    provider = gateway.get_provider()
    assert provider.name == "mock"


def test_get_unknown_provider_raises(gateway):
    with pytest.raises(ProviderNotFoundError):
        gateway.get_provider("unknown")


@pytest.mark.asyncio
async def test_mock_provider_generate(mock_provider):
    response = await mock_provider.generate("Olá", {})
    assert "Misaka" in response
    assert "Brain Engine" in response


@pytest.mark.asyncio
async def test_mock_provider_general_message(mock_provider):
    response = await mock_provider.generate("Como vai?", {})
    assert "Recebi sua mensagem" in response


@pytest.mark.asyncio
async def test_gateway_generate(gateway):
    result = await gateway.generate("Olá", {})
    assert "response" in result
    assert "provider" in result
    assert result["provider"] == "mock"
    assert "Misaka" in result["response"]


@pytest.mark.asyncio
async def test_gateway_generate_with_provider(gateway):
    result = await gateway.generate("Olá", {}, provider_name="mock")
    assert result["provider"] == "mock"


def test_mock_provider_always_available(mock_provider):
    assert mock_provider.is_available() is True