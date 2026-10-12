import pytest
from pydantic import ValidationError
from tms.models.schemas import ErrorResponse, LoadResponse, ResponseModel


class TestErrorResponse:
    """Test ErrorResponse schema."""

    def test_error_response_valid(self):
        """Test valid ErrorResponse."""
        error_data = {"error": {"code": "INVALID", "message": "Bad request"}}
        response = ErrorResponse(**error_data)
        
        assert response.error == {"code": "INVALID", "message": "Bad request"}

    def test_error_response_multiple_fields(self):
        """Test ErrorResponse with multiple error fields."""
        error_data = {"error": {"code": "INVALID", "message": "Bad request", "detail": "Field missing"}}
        response = ErrorResponse(**error_data)
        
        assert len(response.error) == 3
        assert "code" in response.error
        assert "message" in response.error
        assert "detail" in response.error

    def test_error_response_missing_error_field(self):
        """Test ErrorResponse without error field raises validation error."""
        with pytest.raises(ValidationError):
            ErrorResponse(**{})


class TestLoadResponse:
    """Test LoadResponse schema."""

    def test_load_response_valid(self):
        """Test valid LoadResponse."""
        load_data = {"loads": {"load1": "value1", "load2": "value2"}}
        response = LoadResponse(**load_data)
        
        assert response.loads == {"load1": "value1", "load2": "value2"}

    def test_load_response_empty(self):
        """Test LoadResponse with empty loads."""
        load_data = {"loads": {}}
        response = LoadResponse(**load_data)
        
        assert response.loads == {}

    def test_load_response_single_load(self):
        """Test LoadResponse with single load."""
        load_data = {"loads": {"load1": "value1"}}
        response = LoadResponse(**load_data)
        
        assert len(response.loads) == 1
        assert response.loads["load1"] == "value1"

    def test_load_response_missing_loads_field(self):
        """Test LoadResponse without loads field raises validation error."""
        with pytest.raises(ValidationError):
            LoadResponse(**{})


class TestResponseModel:
    """Test ResponseModel schema."""

    def test_response_model_with_result_only(self):
        """Test ResponseModel with only result field."""
        data = {"result": {"key1": "value1", "key2": "value2"}}
        response = ResponseModel(**data)
        
        assert response.result == {"key1": "value1", "key2": "value2"}
        assert response.error is None

    def test_response_model_with_error_only(self):
        """Test ResponseModel with only error field."""
        data = {"error": {"code": "INVALID", "message": "Bad request"}}
        response = ResponseModel(**data)
        
        assert response.error == {"code": "INVALID", "message": "Bad request"}
        assert response.result is None

    def test_response_model_with_both_fields(self):
        """Test ResponseModel with both result and error fields."""
        data = {
            "result": {"data": "success"},
            "error": {"code": "WARNING", "message": "Partial success"}
        }
        response = ResponseModel(**data)
        
        assert response.result == {"data": "success"}
        assert response.error == {"code": "WARNING", "message": "Partial success"}

    def test_response_model_empty(self):
        """Test ResponseModel with no fields (both optional)."""
        response = ResponseModel()
        
        assert response.result is None
        assert response.error is None

    def test_response_model_with_empty_result(self):
        """Test ResponseModel with empty result dict."""
        data = {"result": {}}
        response = ResponseModel(**data)
        
        assert response.result == {}
        assert response.error is None

    def test_response_model_with_empty_error(self):
        """Test ResponseModel with empty error dict."""
        data = {"error": {}}
        response = ResponseModel(**data)
        
        assert response.error == {}
        assert response.result is None

    def test_response_model_complex_result(self):
        """Test ResponseModel with complex nested result."""
        data = {
            "result": {
                "loads": {"load1": "value1"},
                "metadata": {"count": 1, "total": 100}
            }
        }
        response = ResponseModel(**data)
        
        assert response.result["loads"] == {"load1": "value1"}
        assert response.result["metadata"]["count"] == 1
