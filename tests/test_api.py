"""
Tests for API endpoints
"""


def test_hello_chat_endpoint(client):
    """Test the hello-chat endpoint is accessible"""
    response = client.get("/api/v1/chat/hello-chat")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Hello from chat endpoint"


def test_api_v1_router_exists(client):
    """Test the API v1 router is mounted correctly"""
    response = client.get("/api/v1/chat/hello-chat")
    
    # Should not return 404 (router is mounted)
    assert response.status_code != 404
