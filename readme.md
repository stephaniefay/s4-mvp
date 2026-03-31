# Book Genre Classifier

Esse projeto contém uma aplicação que possui machine learning utilizada para predizer o gênero de um livro baseado em seu título (apenas títulos em inglês, por hora).

Ele consiste de:

* Um modelo ML treinado via Scikit-Learn
* Uma API backend construída com FastAPI
* Um frontend simples que demonstra a predição da ML

## Features

* Preve o gênero de um livro baseado em seu título
* Modelo carregado dinamicamente via [releases](https://github.com/stephaniefay/s4-mvp/releases/tag/pkl) para evitar files grandes no repositório

## Estrutura do projeto

```
backend/
├── Machine Learning/
│   ├── dataset/
│   │   ├── data.csv
│   │   └── old_data.csv (não utilizado, mantido apenas para referência)
│   ├── model/
│   │   ├── modelo_genero_livros.pkl
│   │   └── old_modelo_genero_livros.pkl (não utilizado, mantido apenas para referência)
│   └── notebook/
│   │   ├── machine_learning.ipynb
│   │   └── old_machine_learning.ipynb (não utilizado, mantido apenas para referência)
├── API/
│   ├── main.py
│   └── test_main.py

frontend/
├── index.html
├── script.js
└── style.css
```

## Requirements

* Python 3.10+
* pip

## Instalação

### 1. Clone do repositório

```bash
git clone https://github.com/stephaniefay/s4-mvp.git
cd s4-mvp/backend/routes
```

---

### 2. Crie um ambiente virtual e ative-o

```bash
python -m venv venv
```

Ativação:

**Windows:**

```bash
.\venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

---

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## Rodando a API

```bash
python -m uvicorn main:app --reload
```

## Rodando os Testes 

```bash
pip install -r requirements-test.txt
```

Para rodar os testes:

```bash
pytest
```

## Acesso a API

uma vez que esteja rodando, você poderá acessar esses endpoints:

* API root:
  http://127.0.0.1:8000

* Interactive docs (Swagger):
  http://127.0.0.1:8000/docs

## Fazendo uma requisição de predição

Você pode utilizar o browser (GET) para testar o modelo:

```
http://127.0.0.1:8000/predict?title=The%20Art%20of%20War
```

## Executando o frontend

Abre o arquivo em seu navegador de preferência (foi testado apenas em chrome):

```
frontend/index.html
```

Fluxo básico de execução:

1. Insira um título de livro
2. Clique em "Predict"
3. Visualize o gênero que foi predito (e aprecie os corvos! 🐦‍⬛)

## Notas

* Construído usando TF-IDF + SVM
* Treinado usando o [dataset](https://www.kaggle.com/datasets/middlelight/goodreadsbookswithgenres/data) do site Goodreads, conhecido por uma extensa database de livros
* Usa, hoje, apenas o título como input de predição

## Limitações

* O uso apenas de títulos pode não ser contexto o suficiente para possuir uma confiabilidade grande
* Dataset era em inglês, portanto ainda não há suporte para predições em outras línguas
* Algumas predições podem não estar corretas
* Modelo ainda não entende semântica, apenas padrões

## Melhorias futuras (previstas)

* Adicionar suporte a sinopses para aumentar a confiabilidade
* Adicionar outras línguas
* Usar datasets maiores e ricos (exemplos: [10,000 Books and Their Genres *standardized*](https://www.kaggle.com/datasets/michaelrussell4/10000-books-and-their-genres-standardized), [Goodreads Best Books Ever dataset](https://github.com/scostap/goodreads_bbe_dataset/tree/main) ou [Goodreads Book Descriptions](https://huggingface.co/datasets/booksouls/goodreads-book-descriptions))
* Aplicar modelos NLP avançados (BERT, embeddings)

## Autora

Stephanie Fay
