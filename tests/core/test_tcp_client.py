import pytest
from unittest.mock import MagicMock, patch
from tms.core.tcp_client import make_request


class TestMakeRequestSuccess:
    """Test successful TCP requests."""

    def test_make_request_with_params(self, env_vars, mock_tcp_success):
        """Test make_request with valid parameters."""
        params = {"param1": "value1", "param2": "value2"}
        result = make_request("LOAD_QUERY", params)
        
        assert "loads" in result
        assert isinstance(result["loads"], dict)
        mock_tcp_success.connect.assert_called_once()
        mock_tcp_success.send.assert_called_once()
        mock_tcp_success.close.assert_called_once()

    def test_make_request_empty_params(self, env_vars, mock_tcp_success):
        """Test make_request with empty parameters."""
        params = {}
        result = make_request("LOAD_GET", params)
        
        assert "loads" in result
        mock_tcp_success.connect.assert_called_once()

    def test_make_request_multiple_response_fields(self, env_vars):
        """Test make_request with multiple fields in response."""
        with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
            mock_instance = MagicMock()
            mock_instance.recv.return_value = b"field1:value1|field2:value2\r\nfield3:value3|field4:value4\r\nEND\r\n"
            mock_socket_class.return_value = mock_instance
            
            result = make_request("LOAD_QUERY", {"test": "param"})
            
            assert "loads" in result
            assert len(result["loads"]) == 4
            assert result["loads"]["field1"] == "value1"
            assert result["loads"]["field2"] == "value2"
            assert result["loads"]["field3"] == "value3"
            assert result["loads"]["field4"] == "value4"

    def test_make_request_with_end_marker(self, env_vars):
        """Test make_request handles END marker correctly."""
        with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
            mock_instance = MagicMock()
            mock_instance.recv.return_value = b"load1:value1\r\nEND\r\n"
            mock_socket_class.return_value = mock_instance
            
            result = make_request("LOAD_QUERY", {"test": "param"})
            
            assert "loads" in result
            assert len(result["loads"]) == 1
            assert result["loads"]["load1"] == "value1"


class TestMakeRequestErrors:
    """Test error handling in TCP requests."""

    def test_make_request_error_response(self, env_vars, mock_tcp_error):
        """Test make_request with error response from server."""
        params = {"param1": "value1"}
        result = make_request("LOAD_QUERY", params)
        
        assert "error" in result
        assert "code" in result["error"]
        assert result["error"]["code"] == "INVALID_PARAM"
        assert "message" in result["error"]

    def test_make_request_multiple_error_fields(self, env_vars):
        """Test make_request with multiple error fields."""
        with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
            mock_instance = MagicMock()
            mock_instance.recv.return_value = b"ERR|code:INVALID|message:Bad request|detail:Field missing\r\n"
            mock_socket_class.return_value = mock_instance
            
            result = make_request("LOAD_QUERY", {"test": "param"})
            
            assert "error" in result
            assert result["error"]["code"] == "INVALID"
            assert result["error"]["message"] == "Bad request"
            assert result["error"]["detail"] == "Field missing"

    def test_make_request_connection_failure(self, env_vars, mock_tcp_connection_failure):
        """Test make_request with connection failure."""
        params = {"param1": "value1"}
        
        with pytest.raises(ConnectionRefusedError):
            make_request("LOAD_QUERY", params)

    def test_make_request_missing_auth_token(self, monkeypatch):
        """Test make_request with missing AUTH_TOKEN."""
        monkeypatch.setenv("TMS_ADDRESS", "localhost")
        monkeypatch.setenv("TMS_PORT", "9999")
        monkeypatch.delenv("AUTH_TOKEN", raising=False)
        
        with pytest.raises(KeyError):
            make_request("LOAD_QUERY", {"test": "param"})

    def test_make_request_missing_tms_address(self, monkeypatch):
        """Test make_request with missing TMS_ADDRESS."""
        monkeypatch.setenv("AUTH_TOKEN", "test_token")
        monkeypatch.setenv("TMS_PORT", "9999")
        monkeypatch.delenv("TMS_ADDRESS", raising=False)
        
        with pytest.raises(KeyError):
            make_request("LOAD_QUERY", {"test": "param"})

    def test_make_request_missing_tms_port(self, monkeypatch):
        """Test make_request with missing TMS_PORT."""
        monkeypatch.setenv("AUTH_TOKEN", "test_token")
        monkeypatch.setenv("TMS_ADDRESS", "localhost")
        monkeypatch.delenv("TMS_PORT", raising=False)
        
        with pytest.raises(KeyError):
            make_request("LOAD_QUERY", {"test": "param"})


class TestMakeRequestEdgeCases:
    """Test edge cases in TCP requests."""

    def test_make_request_empty_response(self, env_vars):
        """Test make_request with empty response."""
        with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
            mock_instance = MagicMock()
            mock_instance.recv.return_value = b""
            mock_socket_class.return_value = mock_instance
            
            result = make_request("LOAD_QUERY", {"test": "param"})
            
            assert "loads" in result
            assert len(result["loads"]) == 0

    def test_make_request_only_end_marker(self, env_vars):
        """Test make_request with only END marker."""
        with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
            mock_instance = MagicMock()
            mock_instance.recv.return_value = b"END\r\n"
            mock_socket_class.return_value = mock_instance
            
            result = make_request("LOAD_QUERY", {"test": "param"})
            
            assert "loads" in result
            assert len(result["loads"]) == 0

    def test_make_request_large_response(self, env_vars):
        """Test make_request with response larger than buffer size."""
        with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
            mock_instance = MagicMock()
            large_data = "|".join([f"field{i}:value{i}" for i in range(100)])
            mock_instance.recv.return_value = f"{large_data}\r\nEND\r\n".encode('ascii')
            mock_socket_class.return_value = mock_instance
            
            result = make_request("LOAD_QUERY", {"test": "param"})
            
            assert "loads" in result
            assert len(result["loads"]) == 100

    def test_make_request_command_format(self, env_vars):
        """Test that command is formatted correctly."""
        with patch('tms.core.tcp_client.socket.socket') as mock_socket_class:
            mock_instance = MagicMock()
            mock_instance.recv.return_value = b"load1:value1\r\nEND\r\n"
            mock_socket_class.return_value = mock_instance
            
            params = {"key1": "val1", "key2": "val2"}
            make_request("LOAD_QUERY", params)
            
            sent_data = mock_instance.send.call_args[0][0]
            sent_str = sent_data.decode('utf-8')
            
            assert "CMD:LOAD_QUERY" in sent_str
            assert "AUTH:test_auth_token" in sent_str
            assert "key1:val1" in sent_str
            assert "key2:val2" in sent_str
            assert sent_str.endswith("\r\n")
