# 📚 Book Genre Classifier

This project is a Machine Learning application that predicts the genre of a book based on its title.

It consists of:

* 🧠 A trained ML model (Scikit-Learn)
* ⚙️ A backend API built with FastAPI
* 🎨 A simple frontend for interaction

---

## 🚀 Features

* Predicts book genre from title
* REST API with FastAPI
* Simple frontend interface
* Model loaded dynamically from URL (avoids large files in repo)

---

## 📁 Project Structure

```
backend/
├── Machine Learning/
│   ├── dataset/
│   ├── model/
│   └── notebook/
├── routes/
│   ├── main.py
│   └── test_main.py

frontend/
├── index.html
├── index.js
└── index.css
```

---

## ⚙️ Requirements

* Python 3.10+
* pip

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/stephaniefay/s4-mvp.git
cd s4-mvp/backend/routes
```

---

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**

```bash
.\venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Backend

```bash
python -m uvicorn main:app --reload
```

---

## 🧪 Running Tests

```bash
pip install -r requirements-test.txt
```

To run automated tests:

```bash
pytest
```

---

## 🌐 API Access

Once running, open:

* API root:
  http://127.0.0.1:8000

* Interactive docs (Swagger):
  http://127.0.0.1:8000/docs

---

## 🔮 Making Predictions

Using browser (GET request):

```
http://127.0.0.1:8000/predict?title=The%20Art%20of%20War
```

---

## 🎨 Running the Frontend

Open the file:

```
frontend/index.html
```

Then:

1. Enter a book title
2. Click "Predict"
3. View the predicted genre

---

## 🧠 Model Notes

* Built using TF-IDF + SVM
* Trained on Goodreads dataset
* Uses only book titles as input

---

## ⚠️ Limitations

* Titles alone may not provide enough context
* Some predictions may be inaccurate
* Model does not understand semantics, only patterns

---

## 🚀 Future Improvements

* Add synopsis support
* Use larger and richer datasets
* Apply advanced NLP models (BERT, embeddings)

---

## 👩‍💻 Author

Stephanie Fay
