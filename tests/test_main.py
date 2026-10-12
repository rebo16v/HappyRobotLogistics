from tms.main import app


def test_app_creation():
    """Test that the FastAPI app is created correctly."""
    assert app is not None
    assert app.title == "HappyRobot Logistics API"


def test_app_includes_router():
    """Test that the TMS router is included in the app."""
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/load_query" in routes
    assert "/load_get" in routes
    assert "/load_book" in routes
