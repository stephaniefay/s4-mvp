
# Classificação de Gênero de Livros com Machine Learning

## 1. Introdução


Este trabalho tem como objetivo desenvolver um modelo de Machine Learning para classificar automaticamente o gênero de livros com base em seus títulos e sinopses. A classificação de textos é uma tarefa importante em diversas aplicações, como sistemas de recomendação e organização de conteúdo digital.

## 2. Base de Dados

A [base de dados](https://www.kaggle.com/datasets/athu1105/tagmybook/data) contém informações sobre livros, incluindo:

* Título (`title`)
* Sinopse (`synopsis`)
* Gênero (`genre`)

A variável **gênero** foi utilizada como variável alvo (target), enquanto os campos textuais foram utilizados como entrada.


## 3. Pré-processamento dos Dados

Foi criada uma nova variável textual combinando o título e a sinopse:

```python
dataset['text'] = dataset['title'] + " " + dataset['synopsis']
```

Registros com valores ausentes foram removidos. Para converter os dados textuais em formato numérico, foi utilizada a técnica de **TF-IDF (Term Frequency–Inverse Document Frequency)**, essa técnica também atua como uma forma de normalização, eliminando a necessidade de métodos adicionais como padronização com StandardScaler.


## 4. Separação dos Dados

Os dados foram divididos em:

* 80% para treinamento
* 20% para teste

Foi utilizada **estratificação**, garantindo a proporção das classes em ambos os conjuntos.


## 5. Modelagem

Foram utilizados os seguintes algoritmos:

* K-Nearest Neighbors (KNN)
* Árvore de Decisão (CART)
* Naive Bayes (MultinomialNB)
* Support Vector Machine (SVM)

Foi utilizada a técnica de **Pipeline**, integrando o TF-IDF com os modelos, evitando vazamento de dados.


## 6. Validação Cruzada

A avaliação foi realizada utilizando **validação cruzada estratificada com 10 partições (10-fold)**, a abordagem fornece uma estimativa mais confiável do desempenho dos modelos.


## 7. Avaliação dos Modelos

Os modelos foram avaliados com base na métrica de **acurácia** e um gráfico boxplot foi utilizado para comparar o desempenho entre os algoritmos. Modelos baseados em texto, como Naive Bayes e SVM, apresentaram melhor desempenho.


## 8. Otimização de Hiperparâmetros

Foi utilizada a técnica de **Grid Search (GridSearchCV)** para otimizar o modelo SVM e os parâmetros ajustados incluíram:

* `C` (regularização)
* `kernel`
* número máximo de features do TF-IDF


## 9. Avaliação Final

O melhor modelo foi avaliado no conjunto de teste, utilizando:

* Acurácia
* Precision
* Recall
* F1-score

Os resultados indicaram bom desempenho na tarefa de classificação.


## 10. Treinamento Final e Exportação

Após a seleção do melhor modelo, ele foi treinado com **todo o conjunto de dados**:

```python
best_model.fit(X, y)
```

O modelo foi então salvo utilizando a biblioteca `joblib`:

```python
joblib.dump(best_model, "./model/modelo_genero_livros.pkl")
```


## 11. Conclusão

Os resultados demonstram que algoritmos clássicos de Machine Learning, combinados com técnicas de processamento de linguagem natural como TF-IDF, são eficazes para classificação de textos e o uso de pipelines, validação cruzada e otimização de hiperparâmetros contribuiu para a robustez do modelo.

Como trabalhos futuros, pode-se explorar modelos mais avançados baseados em redes neurais e embeddings semânticos.

