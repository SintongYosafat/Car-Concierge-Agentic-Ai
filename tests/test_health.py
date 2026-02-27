"""
Tests for health check endpoint
"""


def test_health_check(client):
    """Test the health check endpoint returns 200 and correct structure"""
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-concierge-backend"
    assert "version" in data


def test_health_check_response_structure(client):
    """Test the health check response has all required fields"""
    response = client.get("/health")
    data = response.json()
    
    required_fields = ["status", "service", "version"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
