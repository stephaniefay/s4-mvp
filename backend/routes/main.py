from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(
    BASE_DIR,
    "..",
    "Machine Learning",
    "model",
    "modelo_genero_livros_imp.pkl"
)

model = joblib.load(model_path)

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
    prediction = model.predict([title])[0]
   
    return {
        "title": title,
        "predicted_genre": prediction
    }