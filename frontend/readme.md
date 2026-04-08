# Front-end — Biblioteca de Corvos

## 1. Introdução

Este módulo implementa a interface web da aplicação **Biblioteca dos Corvos**, responsável por:

- Permitir que o usuário informe um título ou autor para receber recomendações de livros similares;
- Permitir a entrada manual de atributos de um livro para que o modelo classifique sua popularidade;
- Exibir os resultados de forma visual e interativa, consumindo os endpoints da API FastAPI.

A interface foi desenvolvida como uma página HTML estática, sem dependência de frameworks ou etapas de build, e pode ser aberta diretamente no navegador.

---

## 2. Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| HTML5 | Estrutura da página |
| CSS3 | Estilização, animações e layout responsivo |
| JavaScript (ES2020) | Consumo da API via `fetch`, manipulação do DOM |
| Google Fonts | Tipografia (Cinzel, Cormorant Garamond, IM Fell English) |

Nenhuma biblioteca JavaScript externa é utilizada. Toda a lógica de interface é implementada em JavaScript puro.

---

## 3. Estrutura de Arquivos

```
frontend/
├── index.html
├── script.js
└── style.css     

```

---

## 4. Instalação e Execução

### 4.1. Pré-requisitos

- Navegador moderno (Chrome 90+, Firefox 88+, Edge 90+, Safari 14+)
- API em execução em `http://localhost:8000` (consulte o README da pasta `api/`)

### 4.2. Abertura direta no navegador

Não é necessário instalar dependências ou executar nenhum servidor. Basta abrir o arquivo diretamente:

```bash
# Linux/macOS
open frontend/index.html

# Windows (Prompt de Comando)
start frontend\index.html

# Ou simplesmente dê duplo clique no arquivo index.html
```

---

## 5. Funcionalidades

### 5.1. Consultar Grimório — Recomendação por Livro ou Autor

O usuário digita o título de um livro ou o nome de um autor no campo de busca. Ao confirmar (clicando no botão ou pressionando `Enter`), a interface envia uma requisição `POST /recomendar` à API e exibe os 10 livros mais similares, com as seguintes informações para cada resultado:

- Posição no ranking de similaridade
- Título e autor do livro
- Avaliação média
- Classe de popularidade (Alta, Média ou Baixa)
- Barra visual com o percentual de similaridade em relação ao livro de referência

### 5.2. Invocar Oráculo — Classificação de Popularidade

O usuário preenche os atributos de um livro (avaliação média, número de avaliações e número de páginas) e solicita a classificação. A interface envia uma requisição `POST /classificar` à API e exibe:

- A classe predita (Alta, Média ou Baixa) em destaque visual
- Barras de probabilidade para cada classe, com os valores percentuais retornados pelo modelo

---

## 6. Tratamento de Erros

A interface exibe mensagens de erro descritivas nas seguintes situações:

| Situação | Mensagem exibida |
|---|---|
| Campo de busca vazio | Nenhum nome foi sussurrado ao corvo. |
| Campos numéricos inválidos | Preencha ao menos a avaliação e o número de avaliações. |
| API fora do ar ou inacessível | Não foi possível contactar o servidor. Verifique se a API está ativa na porta 8000. |
| Livro não encontrado pela API | Mensagem de erro retornada diretamente pelo servidor |

Todos os textos inseridos pelo usuário são escapados antes de serem inseridos no DOM, prevenindo ataques de Cross-Site Scripting (XSS).

---

## 7. Design e Identidade Visual

A interface segue uma estética **gótico-editorial**, com referências visuais a bibliotecas antigas e grimórios medievais:

- **Tipografia**: Cinzel (títulos e rótulos), Cormorant Garamond (corpo de texto), IM Fell English (subtítulos em itálico)
- **Paleta**: fundo carvão (`#1a1208`), texto pergaminho (`#f2e8d5`), dourado (`#c8a84b`) como cor de destaque
- **Efeitos visuais**: textura de ruído, vignette radial, estrelas pulsantes, animação de flutuação no emblema de corvo
- **Cores por classe de popularidade**: verde (`Alta`), azul (`Média`), terracota (`Baixa`)

---

## 8. Segurança

As seguintes práticas foram adotadas na camada de front-end:

- **Escape de HTML**: todas as strings provenientes da API são tratadas com a função `esc()` antes de serem inseridas no DOM, prevenindo XSS
- **Validação no cliente**: os campos numéricos são verificados localmente antes de qualquer requisição à API, reduzindo tráfego desnecessário
- **Sem armazenamento local**: nenhum dado digitado pelo usuário é armazenado em `localStorage`, `sessionStorage` ou cookies
- **Sem dependências externas de scripts**: toda a lógica é implementada em JavaScript nativo, eliminando riscos de Supply Chain Attack via CDN de terceiros
