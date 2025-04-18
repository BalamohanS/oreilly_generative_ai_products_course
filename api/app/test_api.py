from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API. Refer to the documentation for available endpoints."}

def test_knowledge_base_search():
    response = client.post("/query/knowledge_base_search/", json={"message": "desserts, roasts, casseroles and similar"})
    assert response.status_code == 200
    assert "Instant Pot Duo 7-in-1" in response.json()["response"][0]["page_content"]

def test_knowledge_base_search_with_ai():
    response = client.post("/query/knowledge_base_search_with_ai/", json={"message": "did people complain about Apple TV+?, what were the issues?"})
    assert response.status_code == 200
    assert "Yes" in response.json()["response"]["answer"]

def test_general_advice():
    response = client.post("/query/general_advice/", json={"message": "What is the best product to buy?"})
    assert response.status_code == 200
    assert "Great that you ask about products!" in response.json()["response"]

def test_sql():
    response = client.post("/query/sql/", json={"message": "average stock"})
    assert response.status_code == 200
    assert "27.5" in response.json()["response"]

def test_recommend_image():
    response = client.post("/query/recommend_image/", json={"message": "a person who likes rainforests"})
    assert response.status_code == 200
    assert "rainforest.png" in response.json()["response"]

def test_recommend_tour_from_knowledgebase():
    response = client.post("/query/recommend_tour/", json={"message": "the client is very interested in exploring africa"})
    assert response.status_code == 200
    assert "Botswana" in response.json()["response"]["context"][0]["page_content"]

def test_recommend_tour_from_knowledgebase_message():
    response = client.post("/query/recommend_tour/", json={"message": "I am interested in booking a tour in Botswana. I want to do a safari for sure; which tour should I book?"})
    assert response.status_code == 200
    assert "safari" in response.json()["response"]["answer"]
