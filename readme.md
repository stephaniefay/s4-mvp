# 📚 Biblioteca dos Corvos — MVP

Sistema de classificação de popularidade e recomendação de livros
baseado no dataset [**Goodreads Books 100k**](https://www.kaggle.com/datasets/mdhamani/goodreads-books-100k?select=GoodReads_100k_books.csv).

---

## Estrutura do Projeto

```
backend/
├── api/
│   ├── tests/
│   │   ├── test_modelo.py                  # Testes automatizados PyTest
│   ├── main.py
│   ├── requirements.txt
│   └── readme.md                           # ReadME da API
└── machine_learning/
    ├── readme.md                           # ReadME das técnicas aplicadas no notebook de ML
    ├── dataset/
    │   └── books.csv                       # Dataset importado do Kaggle
    ├── model/                              # Artefatos gerados pelo notebook
    │   ├── modelo_popularidade.pkl
    │   ├── tfidf_vetorizador.pkl
    │   ├── feature_matrix.pkl
    │   ├── goodreads_rec.csv
    │   └──  model_metadata.json
    └── notebook/
        └── goodreads_classificacao.ipynb   # Pipeline ML completo (Google Colab)

frontend/
├── index.html                              # Interface "Biblioteca dos Corvos"
├── script.js
├── style.css
└── readme.md                               # ReadME explicando os detalhes da interface
```

> [!IMPORTANT]
> Esse repositório conta com dois releases, um que contém o [dataset](https://github.com/stephaniefay/s4-mvp/releases/tag/csv) e outro que contem os [artefatos](https://github.com/stephaniefay/s4-mvp/releases/tag/pkl).
> Infelizmente essa abordagem teve que ser usada graças ao tamanho dos arquivos.

> [!IMPORTANT]
> Os artefatos serão baixados **automaticamente** da release para o diretório machine_learning/model caso não sejam reconhecidos pela API diante da sua execução

---

## 1. Notebook (Google Colab)

Abra `notebook/goodreads_classificacao.ipynb` no Google Colab.

Ao final, caso deseje, você pode fazer o download dos arquivos gerados para verificação. Eles já se encontram disponíveis na aba releases.

---

## 2. API (FastAPI)

```bash
cd api
pip install -r requirements.txt

# Coloque os artefatos do notebook aqui antes de rodar
uvicorn main:app --reload --port 8000
```

Documentação interativa disponível em: http://localhost:8000/docs

### Endpoints

| Método | Rota          | Descrição                              |
|--------|---------------|----------------------------------------|
| GET    | `/health`     | Status da API e métricas do modelo     |
| POST   | `/classificar`| Classifica popularidade de um livro    |
| POST   | `/recomendar` | Recomenda livros similares             |

### Exemplos de uso

```bash
# Classificar
curl -X POST http://localhost:8000/classificar \
  -H "Content-Type: application/json" \
  -d '{"rating": 4.2, "num_avaliacoes": 15000, "num_paginas": 320}'

# Recomendar
curl -X POST http://localhost:8000/recomendar \
  -H "Content-Type: application/json" \
  -d '{"query": "Harry Potter", "top_n": 10}'
```

---

## 3. Frontend

Abra `frontend/index.html` diretamente no navegador (duplo clique).

Certifique-se de que a API está rodando em `http://localhost:8000`.

---

## 4. Testes

```bash
# Da raiz do projeto:
pip install pytest
pytest tests/test_modelo.py -v
```

Os testes validam:
- Carregamento correto do modelo
- Acurácia ≥ 0.70 no conjunto de teste
- F1-macro ≥ 0.68 no conjunto de teste
- Formato correto das predições (classes válidas, probabilidades somando 1)
- Consistência com os resultados registrados no notebook

---

## Segurança

- Inputs sanitizados via Pydantic (validação de tipos e ranges)
- CORS configurado (restrinja `allow_origins` em produção)
- Modelo embarcado no back-end (nunca exposto diretamente)
- Nenhum dado pessoal é coletado ou armazenado
