import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from tms.main import app


@pytest.fixture
def env_vars(monkeypatch):
    """Set required environment variables for tests."""
    monkeypatch.setenv("AUTH_TOKEN", "test_auth_token")
    monkeypatch.setenv("TMS_ADDRESS", "localhost")
    monkeypatch.setenv("TMS_PORT", "9999")
    return {
        "AUTH_TOKEN": "test_auth_token",
        "TMS_ADDRESS": "localhost",
        "TMS_PORT": "9999"
    }


@pytest.fixture
def client(env_vars):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_tcp_success_response():
    """Sample successful TCP response data."""
    return "load1:value1|load2:value2\r\nload3:value3\r\nEND\r\n"


@pytest.fixture
def sample_tcp_error_response():
    """Sample error TCP response data."""
    return "ERR|code:INVALID_PARAM|message:Missing required field\r\n"


@pytest.fixture
def mock_socket():
    """Mock socket for TCP client tests."""
    mock = MagicMock()
    mock.recv.return_value = b"load1:value1|load2:value2\r\nEND\r\n"
    return mock


@pytest.fixture
def mock_tcp_success():
    """Mock TCP client with successful response."""
    with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
        mock_instance = MagicMock()
        mock_instance.recv.return_value = b"load1:value1|load2:value2\r\nEND\r\n"
        mock_socket_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_tcp_error():
    """Mock TCP client with error response."""
    with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
        mock_instance = MagicMock()
        mock_instance.recv.return_value = b"ERR|code:INVALID_PARAM|message:Missing required field\r\n"
        mock_socket_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_tcp_connection_failure():
    """Mock TCP client with connection failure."""
    with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
        mock_instance = MagicMock()
        mock_instance.connect.side_effect = ConnectionRefusedError("Connection refused")
        mock_socket_class.return_value = mock_instance
        yield mock_instance
