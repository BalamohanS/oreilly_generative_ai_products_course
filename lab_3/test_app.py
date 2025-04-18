import pytest
from fastapi.testclient import TestClient
from main_advanced import app  # replace with actual module name

client = TestClient(app)

def test_ask_endpoint():
    # Sample request body
    request_data = {
        "prompt": "Hello, who are you?",
        "session_id": "test-session"
    }

    # Send POST request to /ask
    response = client.post("/ask", json=request_data)

    # Basic assertions
    assert response.status_code == 200
    json_data = response.json()
    assert "response" in json_data
    assert isinstance(json_data["response"], str)
    assert len(json_data["response"]) > 0