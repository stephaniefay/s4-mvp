from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_prediction():
    response = client.get("/predict?title=The Art of War")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "predicted_genre" in data
    assert isinstance(data["predicted_genre"], str)

def test_prediction_different_title():
    response = client.get("/predict?title=Love and Relationships")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "predicted_genre" in data

def test_empty_title():
    response = client.get("/predict?title=")
    
    assert response.status_code in [200, 422]