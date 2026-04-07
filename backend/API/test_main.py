import os

from fastapi.testclient import TestClient
import joblib
import pickle

import requests
from main import app
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score

MODEL_URL = "https://github.com/stephaniefay/s4-mvp/releases/download/pklv2/modelo_genero_livros.pkl"
MODEL_PATH = "modelo.pkl"

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

def load_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model...")
        response = requests.get(MODEL_URL)
    
    output_path = Path(MODEL_PATH)
    return pickle.loads(output_path.read_bytes())

def test_model_consistency():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model...")
        response = requests.get(MODEL_URL)

    model = joblib.load(MODEL_PATH)

    title = ["The Art of War"]

    pred1 = model.predict(title)
    pred2 = model.predict(title)

    assert pred1[0] == pred2[0]

def test_response_format():
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    response = client.get("/predict?title=Dracula")

    data = response.json()

    assert "predicted_genre" in data
    assert isinstance(data["predicted_genre"], str)