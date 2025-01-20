from random import randint
import pytest
from fastapi.testclient import TestClient
from ..main import app

# Test constants
TEST_ORIGINAL_URL = "https://www.example.com"
TEST_SHORT_CODE = "abc123"

@pytest.fixture
def test_app():
    return TestClient(app)

def test_create_short_url(test_app):
    response = test_app.post(
        "/shorten",
        json={"url": TEST_ORIGINAL_URL}
    )
    assert response.status_code == 200
    assert "short_url" in response.json()
    assert "original_url" in response.json()
    assert response.json()["original_url"] == TEST_ORIGINAL_URL

def test_invalid_url(test_app):
    response = test_app.post(
        "/shorten",
        json={"url": "not-a-valid-url"}
    )
    assert response.status_code == 422

def test_redirect_url(test_app):
    create_response = test_app.post(
        "/shorten",
        json={"url": TEST_ORIGINAL_URL}
    )
    short_code = create_response.json()["short_url"].split("/")[-1]
    
    response = test_app.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == TEST_ORIGINAL_URL

def test_url_stats(test_app):
    rand_num = randint(0, 1000)
    example_url = f"https://www.example{rand_num}.com"
    create_response = test_app.post(
        "/shorten",
        json={"url": example_url}
    )
    short_code = create_response.json()["short_url"].split("/")[-1]
    
    response = test_app.get(f"/url/{short_code}/stats")
    assert response.status_code == 200
    assert response.json()["original_url"] == example_url
    assert response.json()["clicks"] == 0

def test_nonexistent_url(test_app):
    response = test_app.get("/nonexistent")
    assert response.status_code == 404 