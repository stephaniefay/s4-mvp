# Classificação de Popularidade de Livros com Machine Learning

## 1. Introdução

Este módulo tem como objetivo desenvolver um sistema de Machine Learning capaz de:

- Classificar livros em categorias de popularidade (**Alta**, **Média** ou **Baixa**) com base em seus atributos quantitativos;
- Recomendar livros similares a partir de um título ou autor informado pelo usuário.

A solução combina técnicas de aprendizado supervisionado com métodos de processamento de linguagem natural (NLP), permitindo tanto a classificação quanto a recomendação de conteúdo literário.

---

## 2. Base de Dados

A base de dados utilizada foi o [**Goodreads Books 100k**](https://www.kaggle.com/datasets/mdhamani/goodreads-books-100k?select=GoodReads_100k_books.csv), disponível publicamente no Kaggle, contendo metadados de mais de 100.000 livros:

- Título (`title`)
- Autor (`author`)
- Avaliação média (`average_rating`)
- Quantidade de avaliações (`ratings_count`)
- Número de páginas (`num_pages`)

Os nomes das colunas foram padronizados automaticamente durante o pré-processamento via função auxiliar de detecção por palavras-chave, tornando o pipeline resistente a variações no cabeçalho do CSV.

---

## 3. Pré-processamento dos Dados

Foram realizadas as seguintes etapas, todas antes da separação treino/teste:

- Padronização dos nomes das colunas (`str.lower().str.replace(' ', '_')`)
- Identificação automática das colunas relevantes por palavras-chave
- Conversão de tipos numéricos
- Remoção de valores nulos nas colunas obrigatórias (`average_rating`, `ratings_count`)
- Filtragem de registros com `ratings_count <= 0`
- Validação com `assert` para garantir que as colunas obrigatórias foram encontradas
- Preenchimento da mediana nos valores ausentes de páginas

Além disso, foi criada uma variável textual combinando título e autor para uso no sistema de recomendação:

```python
df['texto'] = df['title'] + " " + df['author']
```

---

## 4. Criação da Variável Alvo

A variável alvo é derivada de `ratings_count` usando percentis calculados **somente no treino**:

| Classe | Critério |
|---|---|
| **Alta** | `ratings_count` ≥ p75 do treino |
| **Média** | p25 ≤ `ratings_count` < p75 do treino |
| **Baixa** | `ratings_count` < p25 do treino |

Os mesmos limiares são aplicados ao conjunto de teste sem recalculá-los, replicando o comportamento de produção.

---

## 5. Separação dos Dados

Os dados foram divididos em:

- **80%** para treinamento
- **20%** para teste

O split é realizado **antes** de qualquer derivação de target ou feature — etapa crítica para prevenir *data leakage*. Como o target ainda não existe neste ponto, a estratificação é feita por quartis de `average_rating`, garantindo distribuição equilibrada em ambas as partições.

---

## 6. Engenharia de Features

As features de classificação são **exclusivamente atributos independentes do target**:

| Feature | Descrição |
|---|---|
| `average_rating` | Avaliação média do livro (0–5) |
| `pages_clip` | Número de páginas com nulos imputados pela mediana do treino e outliers limitados a 2.000 |

### Por que `ratings_count` e suas derivadas não são features?

O target `popularidade` é uma transformação direta e determinística de `ratings_count` via percentis. Incluir `ratings_count` — ou qualquer função monotônica dela como `log(ratings_count)` ou `rating × log(ratings_count)` — como feature equivale a revelar o target ao modelo.

A Árvore de Decisão, por exemplo, consegue reconstruir a classificação perfeita com apenas um nó (`log_count >= limiar`), resultando em **F1 = 1.0** — indicador inequívoco de leakage por feature derivada do target. Para uma tarefa de classificação honesta, as features devem ser atributos que descrevem o livro independentemente de quão popular ele é.

---

## 7. Modelagem

Foram avaliados os seguintes algoritmos de classificação, conforme exigido pela disciplina:

- K-Nearest Neighbors (KNN)
- Árvore de Classificação (`DecisionTreeClassifier`)
- Naive Bayes (`GaussianNB`)
- Regressão Logística (`LogisticRegression`)

> O SVM foi substituído pela **Regressão Logística** pelo seu alto custo computacional com o volume de dados do dataset. A Regressão Logística apresenta desempenho competitivo, tempo de execução significativamente menor e maior interpretabilidade.

Para cada algoritmo foi construído um **Pipeline** do Scikit-Learn:

```python
Pipeline([
    ('scaler', StandardScaler()),
    ('clf',    LogisticRegression(random_state=42, max_iter=1000))
])
```

| Algoritmo | Scaler | Justificativa |
|---|---|---|
| KNN | StandardScaler | Muito sensível à escala das features |
| Árvore de Classificação | StandardScaler | Invariante à escala, mantido por consistência |
| Naive Bayes | MinMaxScaler | GaussianNB exige valores ≥ 0 |
| Regressão Logística | StandardScaler | Converge mais rápido com dados padronizados |

---

## 8. Otimização de Hiperparâmetros

A otimização foi realizada com **GridSearchCV** combinado com **Stratified K-Fold** (5 folds), utilizando **F1-macro** como métrica de otimização — mais adequada para problemas multiclasse com possível desbalanceamento.

Exemplos de parâmetros otimizados:

- `n_neighbors` e `metric` (KNN)
- `max_depth` e `min_samples_leaf` (Árvore de Classificação)
- `var_smoothing` (Naive Bayes)
- `C` e `solver` (Regressão Logística)

---

## 9. Avaliação dos Modelos

Os modelos foram avaliados no conjunto de teste utilizando:

- Acurácia
- F1-score macro
- Precision e Recall por classe
- Matriz de Confusão

Um gráfico comparativo de F1-macro (CV vs. Teste) é gerado para todos os modelos — uma diferença pequena entre os dois valores indica ausência de overfitting.

---

## 10. Modelo Selecionado

O modelo com maior **F1-macro no conjunto de teste** é selecionado automaticamente:

```python
melhor_nome = max(resultados_teste, key=lambda n: resultados_teste[n]['f1_macro'])
```

O modelo é exportado como Pipeline completo (scaler + classificador), garantindo que o pré-processamento seja parte integrante do artefato.

---

## 11. Sistema de Recomendação

Além da classificação supervisionada, foi implementado um sistema de recomendação baseado em similaridade.

### Técnica utilizada

- **TF-IDF** sobre o campo textual `título + autor` (bigramas, `max_features=5000`, `sublinear_tf=True`)
- **Similaridade de Cosseno** entre os vetores de features
- Rating médio normalizado combinado à matriz TF-IDF via `hstack`

O TF-IDF é ajustado sobre o dataset completo — válido pois o sistema de recomendação é **não supervisionado** e não possui variável alvo.

---

## 12. Exportação dos Artefatos

```python
joblib.dump(melhor_modelo,  "modelo_popularidade.pkl")
joblib.dump(tfidf,          "tfidf_vetorizador.pkl")
joblib.dump(feature_matrix, "feature_matrix.pkl")
df_rec.to_csv(              "goodreads_rec.csv", index=False)
json.dump(metadata,          open("model_metadata.json", "w"))
```

O `model_metadata.json` armazena os parâmetros aprendidos no treino (`p25`, `p75`, `mediana_paginas`, `features`) para garantir que a API e os testes automatizados reproduzam exatamente o mesmo pipeline.

---

## 13. Testes Automatizados

Critérios mínimos de desempenho definidos para validação antes da implantação:

- **Acurácia ≥ 0.50**
- **F1-macro ≥ 0.40**

Os testes (arquivo `tests/test_modelo.py`) reconstroem o conjunto de teste com os mesmos parâmetros do notebook e cobrem: carregamento do modelo, desempenho mínimo, ausência de overfitting suspeito (F1 < 0.99), formato das predições e consistência com as métricas registradas no notebook (tolerância ±5 p.p.).

---

## 14. Segurança

- **Minimização de dados**: apenas colunas necessárias ao modelo foram retidas
- **Validação de entrada**: ranges numéricos validados via Pydantic na API
- **Separação modelo/dados**: o `.pkl` contém apenas o pipeline treinado, sem dados embutidos
- **Anonimização**: dataset exclusivamente público; com dados de usuários, aplicar pseudonimização e k-anonimato antes do treino

---

## 15. Conclusão

A principal revisão desta versão foi a **correção completa do data leakage**, que ocorria em duas camadas:

1. **Leakage estatístico** — percentis e medianas calculadas sobre o dataset completo antes do split. Corrigido realizando o holdout antes de qualquer cálculo.

2. **Leakage por feature derivada do target** — `log_count` e `rating_x_log` são transformações monotônicas de `ratings_count`, que é a coluna que gerou o target. Incluí-las como features tornava o problema trivialmente separável. Corrigido removendo-as das features de classificação, mantendo apenas `average_rating` e `pages_clip`.

---

## 16. Trabalhos Futuros

- Uso de embeddings semânticos (Word2Vec, Sentence-BERT) no sistema de recomendação
- Incorporação de gênero literário para classificação mais granular
- Sistemas de recomendação híbridos (colaborativo + baseado em conteúdo)
- Retreinamento incremental com novos dados do Goodreads
