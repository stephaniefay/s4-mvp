from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import joblib
import requests

MODEL_URL = "https://github.com/stephaniefay/s4-mvp/releases/download/pkl/modelo_genero_livros_imp.pkl"
MODEL_PATH = "modelo.pkl"

# Download only if not exists
if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    response = requests.get(MODEL_URL)
    
    with open(MODEL_PATH, "wb") as f:
        f.write(response.content)

# Load model
model = joblib.load(MODEL_PATH)

print("Model loaded successfully 🚀")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookRequest(BaseModel):
    title: str

@app.get("/")
def home():
    return {"message": "Book Genre Classifier API is running ✨"}

@app.get("/predict")
def predict(title: str):
    if not title.strip():
        return {"error": "Title cannot be empty"}
    
    prediction = model.predict([title])[0]
   
    return {
        "title": title,
        "predicted_genre": prediction
    }