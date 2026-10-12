import pytest
from unittest.mock import patch
from tms.core.tcp_client import make_request


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_endpoint(self, client):
        """Test that root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "TMS API"}


class TestLoadQueryEndpoint:
    """Test the /load_query endpoint."""

    def test_load_query_success(self, client, env_vars):
        """Test load_query with valid parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {"load1": "value1"}}
            
            response = client.get("/load_query?param1=value1&param2=value2")
            
            assert response.status_code == 200
            assert response.json() == {"loads": {"load1": "value1"}}
            mock_request.assert_called_once_with("LOAD_QUERY", {"param1": "value1", "param2": "value2"})

    def test_load_query_empty_params(self, client, env_vars):
        """Test load_query with no parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {}}
            
            response = client.get("/load_query")
            
            assert response.status_code == 200
            assert response.json() == {"loads": {}}
            mock_request.assert_called_once_with("LOAD_QUERY", {})

    def test_load_query_tcp_error(self, client, env_vars):
        """Test load_query when TCP client returns error."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"error": {"code": "INVALID", "message": "Bad request"}}
            
            response = client.get("/load_query?param1=value1")
            
            assert response.status_code == 200
            assert response.json() == {"error": {"code": "INVALID", "message": "Bad request"}}

    def test_load_query_multiple_params(self, client, env_vars):
        """Test load_query with multiple query parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {"result": "success"}}
            
            response = client.get("/load_query?key1=val1&key2=val2&key3=val3")
            
            assert response.status_code == 200
            mock_request.assert_called_once_with("LOAD_QUERY", {"key1": "val1", "key2": "val2", "key3": "val3"})


class TestLoadGetEndpoint:
    """Test the /load_get endpoint."""

    def test_load_get_success(self, client, env_vars):
        """Test load_get with valid parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {"load1": "data1"}}
            
            response = client.get("/load_get?id=123")
            
            assert response.status_code == 200
            assert response.json() == {"loads": {"load1": "data1"}}
            mock_request.assert_called_once_with("LOAD_GET", {"id": "123"})

    def test_load_get_empty_params(self, client, env_vars):
        """Test load_get with no parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {}}
            
            response = client.get("/load_get")
            
            assert response.status_code == 200
            mock_request.assert_called_once_with("LOAD_GET", {})

    def test_load_get_tcp_error(self, client, env_vars):
        """Test load_get when TCP client returns error."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"error": {"code": "NOT_FOUND", "message": "Load not found"}}
            
            response = client.get("/load_get?id=999")
            
            assert response.status_code == 200
            assert response.json() == {"error": {"code": "NOT_FOUND", "message": "Load not found"}}


class TestLoadBookEndpoint:
    """Test the /load_book endpoint."""

    def test_load_book_success(self, client, env_vars):
        """Test load_book with valid parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {"booking": "confirmed"}}
            
            response = client.get("/load_book?load_id=123&customer=ABC")
            
            assert response.status_code == 200
            assert response.json() == {"loads": {"booking": "confirmed"}}
            mock_request.assert_called_once_with("LOAD_BOOK", {"load_id": "123", "customer": "ABC"})

    def test_load_book_empty_params(self, client, env_vars):
        """Test load_book with no parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {}}
            
            response = client.get("/load_book")
            
            assert response.status_code == 200
            mock_request.assert_called_once_with("LOAD_BOOK", {})

    def test_load_book_tcp_error(self, client, env_vars):
        """Test load_book when TCP client returns error."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"error": {"code": "UNAVAILABLE", "message": "Load not available"}}
            
            response = client.get("/load_book?load_id=123")
            
            assert response.status_code == 200
            assert response.json() == {"error": {"code": "UNAVAILABLE", "message": "Load not available"}}


class TestRouteEdgeCases:
    """Test edge cases for routes."""

    def test_special_characters_in_params(self, client, env_vars):
        """Test routes with special characters in parameters."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {"result": "ok"}}
            
            response = client.get("/load_query?param=test%20value&other=abc%40def")
            
            assert response.status_code == 200
            mock_request.assert_called_once()
            call_params = mock_request.call_args[0][1]
            assert "param" in call_params
            assert "other" in call_params

    def test_long_parameter_values(self, client, env_vars):
        """Test routes with very long parameter values."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {"result": "ok"}}
            long_value = "a" * 1000
            
            response = client.get(f"/load_query?param={long_value}")
            
            assert response.status_code == 200
            mock_request.assert_called_once()

    def test_duplicate_parameter_names(self, client, env_vars):
        """Test routes with duplicate parameter names (FastAPI behavior)."""
        with patch('tms.api.routes.make_request') as mock_request:
            mock_request.return_value = {"loads": {"result": "ok"}}
            
            response = client.get("/load_query?key=value1&key=value2")
            
            assert response.status_code == 200
            # FastAPI typically takes the last value for duplicate keys
            mock_request.assert_called_once()
