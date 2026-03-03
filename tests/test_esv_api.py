"""Tests for verse_slides.esv_api module."""

import pytest
import responses
from requests.exceptions import ConnectionError, Timeout, RequestException

from verse_slides.esv_api import ESVAPIClient, DEFAULT_API_ENDPOINT


@pytest.fixture
def api_client():
    """Create an ESV API client for testing."""
    return ESVAPIClient(api_key="test-api-key-123", include_headings=True)


@responses.activate
def test_fetch_passage_success(api_client):
    """Test successful passage fetch from ESV API."""
    # Mock successful API response
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={
            "passages": ["[1] For God so loved the world..."],
            "passage_meta": [{"canonical": "John 3:16"}],
        },
        status=200,
    )

    result = api_client.fetch_passage("John 3:16")

    assert result["text"] == "[1] For God so loved the world..."
    assert result["reference"] == "John 3:16"
    assert result["passages"] == ["[1] For God so loved the world..."]


@responses.activate
def test_fetch_passage_uses_correct_headers(api_client):
    """Test that fetch_passage sends correct authorization header."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={
            "passages": ["Test passage"],
            "passage_meta": [{"canonical": "John 3:16"}],
        },
        status=200,
    )

    api_client.fetch_passage("John 3:16")

    # Check that the request was made with correct headers
    assert len(responses.calls) == 1
    assert responses.calls[0].request.headers["Authorization"] == "Token test-api-key-123"


@responses.activate
def test_fetch_passage_uses_correct_parameters(api_client):
    """Test that fetch_passage sends correct query parameters."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={
            "passages": ["Test passage"],
            "passage_meta": [{"canonical": "John 3:16"}],
        },
        status=200,
    )

    api_client.fetch_passage("John 3:16")

    # Check query parameters
    request = responses.calls[0].request
    assert "q=John+3%3A16" in request.url or "q=John%203%3A16" in request.url
    assert "include-verse-numbers=True" in request.url
    assert "include-headings=True" in request.url
    assert "indent-poetry=True" in request.url


@responses.activate
def test_fetch_passage_without_headings():
    """Test fetch_passage with include_headings=False."""
    client = ESVAPIClient(api_key="test-key", include_headings=False)

    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={
            "passages": ["Test passage"],
            "passage_meta": [{"canonical": "John 3:16"}],
        },
        status=200,
    )

    client.fetch_passage("John 3:16")

    request = responses.calls[0].request
    assert "include-headings=False" in request.url


@responses.activate
def test_fetch_passage_401_unauthorized(api_client):
    """Test handling of 401 Unauthorized error (invalid API key)."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={"error": "Unauthorized"},
        status=401,
    )

    with pytest.raises(SystemExit) as exc_info:
        api_client.fetch_passage("John 3:16")

    assert exc_info.value.code == 1


@responses.activate
def test_fetch_passage_429_rate_limit(api_client):
    """Test handling of 429 Too Many Requests error (rate limit)."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={"error": "Rate limit exceeded"},
        status=429,
    )

    with pytest.raises(SystemExit) as exc_info:
        api_client.fetch_passage("John 3:16")

    assert exc_info.value.code == 1


@responses.activate
def test_fetch_passage_500_server_error(api_client):
    """Test handling of 500 server error."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={"error": "Internal server error"},
        status=500,
    )

    with pytest.raises(SystemExit) as exc_info:
        api_client.fetch_passage("John 3:16")

    assert exc_info.value.code == 1


@responses.activate
def test_fetch_passage_empty_response(api_client):
    """Test handling of empty passages in API response."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={
            "passages": [""],
            "passage_meta": [{"canonical": "Invalid Reference"}],
        },
        status=200,
    )

    with pytest.raises(SystemExit) as exc_info:
        api_client.fetch_passage("InvalidReference 999:999")

    assert exc_info.value.code == 1


@responses.activate
def test_fetch_passage_no_passages_key(api_client):
    """Test handling of response without passages key."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={"error": "Something went wrong"},
        status=200,
    )

    with pytest.raises(SystemExit) as exc_info:
        api_client.fetch_passage("John 3:16")

    assert exc_info.value.code == 1


@responses.activate
def test_fetch_passage_connection_error(api_client):
    """Test handling of connection errors."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        body=ConnectionError("Connection failed"),
    )

    with pytest.raises(SystemExit) as exc_info:
        api_client.fetch_passage("John 3:16")

    assert exc_info.value.code == 1


@responses.activate
def test_fetch_passage_timeout(api_client):
    """Test handling of request timeout."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        body=Timeout("Request timed out"),
    )

    with pytest.raises(SystemExit) as exc_info:
        api_client.fetch_passage("John 3:16")

    assert exc_info.value.code == 1


@responses.activate
def test_fetch_passage_uses_canonical_reference(api_client):
    """Test that fetch_passage uses canonical reference from API."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={
            "passages": ["Test passage"],
            "passage_meta": [{"canonical": "John 3:16–21"}],  # Note en-dash
        },
        status=200,
    )

    result = api_client.fetch_passage("John 3:16-21")

    # Should use canonical reference with en-dash from API
    assert result["reference"] == "John 3:16–21"


@responses.activate
def test_fetch_passage_falls_back_to_input_reference(api_client):
    """Test that fetch_passage uses input reference when canonical not available."""
    responses.add(
        responses.GET,
        DEFAULT_API_ENDPOINT,
        json={
            "passages": ["Test passage"],
            "passage_meta": [],  # No canonical reference
        },
        status=200,
    )

    result = api_client.fetch_passage("John 3:16")

    # Should fall back to input reference
    assert result["reference"] == "John 3:16"


@responses.activate
def test_custom_api_endpoint():
    """Test that custom API endpoint is used when provided."""
    custom_endpoint = "https://custom-bible-api.example.com/v1/text/"
    client = ESVAPIClient(api_key="test-key", api_endpoint=custom_endpoint)

    responses.add(
        responses.GET,
        custom_endpoint,
        json={
            "passages": ["Custom API passage"],
            "passage_meta": [{"canonical": "John 3:16"}],
        },
        status=200,
    )

    result = client.fetch_passage("John 3:16")

    # Verify it used the custom endpoint
    assert result["text"] == "Custom API passage"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(custom_endpoint)


def test_api_endpoint_defaults_to_esv():
    """Test that API endpoint defaults to ESV when not provided."""
    client = ESVAPIClient(api_key="test-key")
    assert client.api_endpoint == DEFAULT_API_ENDPOINT
