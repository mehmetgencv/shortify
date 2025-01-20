import pytest
from unittest.mock import patch, Mock
from app.services.url_service import URLService

# Test constants
TEST_ORIGINAL_URL = "https://www.example.com"
TEST_BASE_URL = "http://localhost"
TEST_SHORT_CODE = "abc123"

@pytest.fixture
def url_service(db):
    """Create URLService instance with test database session"""
    return URLService(db)

def test_create_short_url(url_service, mocker):
    """Test creating a new short URL"""
    # Arrange
    # Mock Redis cache
    mock_get_cache = mocker.patch('app.services.url_service.get_cache', return_value=None)
    mock_set_cache = mocker.patch('app.services.url_service.set_cache')
    
    # Mock database query
    mock_db_query = mocker.patch.object(
        url_service.db,
        'query',
        return_value=Mock(
            filter=Mock(
                return_value=Mock(
                    first=Mock(return_value=None)
                )
            )
        )
    )
    
    # Mock random code generation
    mocker.patch.object(
        url_service,
        'create_random_code',
        return_value=TEST_SHORT_CODE
    )

    # Act
    result = url_service.create_short_url(TEST_ORIGINAL_URL, TEST_BASE_URL)
    
    # Assert
    assert result is not None
    assert result["short_url"] == f"{TEST_BASE_URL}/{TEST_SHORT_CODE}"
    assert result["original_url"] == TEST_ORIGINAL_URL
    
    # Verify cache operations
    mock_get_cache.assert_called_once_with(f"url:{TEST_ORIGINAL_URL}")
    mock_set_cache.assert_called()
    
    # Verify database operations
    mock_db_query.assert_called() 