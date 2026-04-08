# API de Classificação e Recomendação de Livros

## 1. Introdução

Este módulo implementa o back-end da aplicação **Biblioteca dos Corvos**, responsável por:

- Servir o modelo de Machine Learning de forma embarcada, sem dependência de serviços externos;
- Expor endpoints para classificação de popularidade de livros e recomendação por similaridade;
- Validar e sanitizar todas as entradas do usuário antes de qualquer processamento.

A API foi desenvolvida com **FastAPI** e segue os princípios REST, oferecendo documentação interativa automática.

---

## 2. Tecnologias Utilizadas

| Tecnologia | Versão mínima | Finalidade |
|---|---|---|
| Python | 3.10 | Linguagem base |
| FastAPI | 0.111.0 | Framework da API |
| Uvicorn | 0.29.0 | Servidor ASGI |
| Pydantic | 2.6.0 | Validação de schemas |
| Scikit-Learn | 1.6.1 | Carregamento e execução do modelo (versão estática por conta da geração dos PKL via Google Colab) |
| Joblib | 1.3.0 | Desserialização dos artefatos `.pkl` |
| NumPy | 1.26.0 | Manipulação de arrays numéricos |
| Pandas | 2.1.0 | Leitura do dataset de recomendação |
| SciPy | 1.12.0 | Operações com matrizes esparsas |

---

## 3. Estrutura de Arquivos

```
api/
├── main.py                     # Código da API
├── requirements.txt            # Dependências Python
```

> Os artefatos são gerados automaticamente ao executar todas as células do notebook `machine_learning/notebook/goodreads_classificacao.ipynb`. Por conta do tamanho dos arquivos eles foram disponibilizados dentro da aba **Releases** do repositório e são baixados, automaticamente, uma vez que a API é executada.

---

## 4. Instalação

### 4.1. Pré-requisitos

- Python 3.11 
- `pip` atualizado

### 4.2. Criação do ambiente virtual (recomendado)

```bash
# Criar o ambiente
py -3.11 -m venv .venv

# Ativar — Linux/macOS
source .venv/bin/activate

# Ativar — Windows
.venv\Scripts\activate
```

### 4.3. Instalação das dependências

```bash
cd api
pip install -r requirements.txt
```

---

## 5. Execução

### 5.1. Iniciar o servidor

```bash
# Modo desenvolvimento (com hot reload)
uvicorn main:app --reload --port 8000

# Modo produção
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

A API estará disponível em: `http://localhost:8000`

---

## 6. Documentação Interativa

O FastAPI gera automaticamente duas interfaces de documentação:

| Interface | URL | Descrição |
|---|---|---|
| Swagger UI | `http://localhost:8000/docs` | Documentação interativa com formulários para teste |
| ReDoc | `http://localhost:8000/redoc` | Documentação em formato de referência |

---

## 7. Endpoints

### `GET /health`

Verifica se a API está operacional e retorna informações sobre o modelo carregado.

**Resposta:**

```json
{
  "status": "ok",
  "modelo": "SVM",
  "livros_indexados": 98432,
  "f1_macro_treino": 0.8134,
  "acuracia_treino": 0.8291
}
```

---

### `POST /classificar`

Classifica a popularidade de um livro com base em seus atributos numéricos.

**Corpo da requisição:**

| Campo | Tipo | Obrigatório | Validação | Descrição |
|---|---|---|---|---|
| `rating` | float | ✅ | 0.0 – 5.0 | Avaliação média do livro |
| `num_avaliacoes` | int | ✅ | ≥ 1 | Número total de avaliações |
| `num_paginas` | int | ❌ | 1 – 10.000 | Número de páginas (padrão: 300) |

**Exemplo de requisição:**

```bash
curl -X POST http://localhost:8000/classificar \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4.2,
    "num_avaliacoes": 18500,
    "num_paginas": 342
  }'
```

**Resposta:**

```json
{
  "popularidade": "Alta",
  "probabilidades": {
    "Alta":  0.8812,
    "Média": 0.0971,
    "Baixa": 0.0217
  },
  "features_usadas": {
    "average_rating": 4.2,
    "log_count": 9.8271,
    "rating_x_log": 41.2738,
    "pages_clip": 342.0
  }
}
```

---

### `POST /recomendar`

Recomenda livros similares a partir de um título ou autor informado.

**Corpo da requisição:**

| Campo | Tipo | Obrigatório | Validação | Descrição |
|---|---|---|---|---|
| `query` | string | ✅ | 2 – 200 caracteres | Título ou nome do autor |
| `top_n` | int | ❌ | 1 – 20 | Número de recomendações (padrão: 10) |

**Exemplo de requisição:**

```bash
curl -X POST http://localhost:8000/recomendar \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Harry Potter",
    "top_n": 5
  }'
```

**Resposta:**

```json
{
  "referencia": "Harry Potter and the Sorcerer's Stone",
  "total": 5,
  "recomendacoes": [
    {
      "titulo": "Harry Potter and the Chamber of Secrets",
      "autor": "J.K. Rowling",
      "rating": 4.42,
      "popularidade": "Alta",
      "similaridade": 0.9134
    }
  ]
}
```

---

## 8. Testes Automatizados

Os testes validam o modelo de Machine Learning antes de qualquer implantação. Eles estão localizados em `tests/test_modelo.py` e são executados de forma independente da API.

### 8.1. Instalação do PyTest

```bash
pip install pytest
```

### 8.2. Executar todos os testes

```bash
# Da raiz do projeto
pytest tests/test_modelo.py -v
```

A flag `-v` (verbose) exibe o resultado individual de cada teste.

### 8.3. Executar uma classe de testes específica

```bash
# Apenas os testes de desempenho
pytest tests/test_modelo.py::TestDesempenhoNoTeste -v

# Apenas os testes de formato das predições
pytest tests/test_modelo.py::TestFormatoDaPredicao -v
```

### 8.4. Testes disponíveis

| Classe | Teste | Critério de aprovação |
|---|---|---|
| `TestCargaDoModelo` | `test_modelo_nao_e_none` | Modelo carregado com sucesso |
| `TestCargaDoModelo` | `test_modelo_tem_metodo_predict` | Possui o método `predict()` |
| `TestCargaDoModelo` | `test_modelo_tem_metodo_predict_proba` | Possui o método `predict_proba()` |
| `TestDesempenhoNoTeste` | `test_acuracia_minima` | Acurácia ≥ 0.70 |
| `TestDesempenhoNoTeste` | `test_f1_macro_minimo` | F1-macro ≥ 0.68 |
| `TestDesempenhoNoTeste` | `test_sem_overfitting_suspeito` | F1-macro < 0.99 |
| `TestFormatoDaPredicao` | `test_predicao_retorna_array` | 5 predições retornadas para 5 entradas |
| `TestFormatoDaPredicao` | `test_classes_validas` | Classes apenas entre Alta, Média, Baixa |
| `TestFormatoDaPredicao` | `test_predict_proba_soma_um` | Probabilidades somam 1.0 (±1e-6) |
| `TestFormatoDaPredicao` | `test_features_corretas` | Aceita o número correto de features |
| `TestConsistenciaComMetadata` | `test_acuracia_consistente_com_notebook` | Diferença ≤ 5 p.p. em relação ao notebook |

### 8.5. Interpretando os resultados

```
PASSED  — teste aprovado, critério atendido
FAILED  — teste reprovado, não implantar o modelo
SKIPPED — artefato necessário não encontrado em api/
```

---

## 9. Segurança

As seguintes práticas foram adotadas:

- **Validação de tipos e ranges** via Pydantic: `rating` aceita apenas valores entre 0.0 e 5.0; `num_avaliacoes` deve ser ≥ 1; `query` é limitada a 200 caracteres
- **Sanitização de texto**: a query é convertida para minúsculas e removida de espaços antes de qualquer processamento
- **Modelo embarcado**: o arquivo `.pkl` é carregado uma única vez na inicialização da API e nunca exposto diretamente ao cliente
- **CORS configurado**: em produção, substitua `allow_origins=["*"]` pelos domínios autorizados do front-end
- **Sem armazenamento de dados**: nenhuma requisição ou dado do usuário é persistido
