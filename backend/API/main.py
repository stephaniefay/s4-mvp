from __future__ import annotations

import json
import logging
import requests
from pathlib import Path
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO, format="%(levelname)s │ %(message)s")
log = logging.getLogger("corvos-api")

# ──────────────────────────────────────────────────────────────────────
# Caminhos dos artefatos
# ──────────────────────────────────────────────────────────────────────

BASE_API_DIR = Path(__file__).resolve().parent
BASE_DIR = BASE_API_DIR.parent / "machine_learning" / "model"

ARTEFATOS = {
    "modelo": {
        "url": "https://github.com/stephaniefay/s4-mvp/releases/download/pkl/modelo_popularidade.pkl",
        "path": BASE_DIR / "modelo_popularidade.pkl"
    },
    "tfidf": {
        "url": "https://github.com/stephaniefay/s4-mvp/releases/download/pkl/tfidf_vetorizador.pkl",
        "path": BASE_DIR / "tfidf_vetorizador.pkl"
    },
    "matrix": {
        "url": "https://github.com/stephaniefay/s4-mvp/releases/download/pkl/feature_matrix.pkl",
        "path": BASE_DIR / "feature_matrix.pkl"
    },
    "data": {
        "url": "https://github.com/stephaniefay/s4-mvp/releases/download/pkl/goodreads_rec.csv",
        "path": BASE_DIR / "goodreads_rec.csv"
    },
    "metadata": {
        "url": "https://github.com/stephaniefay/s4-mvp/releases/download/pkl/model_metadata.json",
        "path": BASE_DIR / "model_metadata.json"
    }
}

# ──────────────────────────────────────────────────────────────────────
# Carga dos artefatos (acontece uma única vez na inicialização)
# ──────────────────────────────────────────────────────────────────────
def download_file(url: str, path: Path):
    """Baixa um arquivo apenas se ele não existir localmente."""
    if path.exists():
        print(f"  [OK] Arquivo já existe: {path.name}")
        return

    print(f"  [baixando] {path.name}...")
    try:
        # Garante que a pasta pai exista
        path.parent.mkdir(parents=True, exist_ok=True)
        
        response = requests.get(url, stream=True)
        response.raise_for_status() # Lança erro se o download falhar (ex: 404)
        
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  [sucesso] {path.name} salvo em {path.parent}")
    except Exception as e:
        print(f"  [erro] Falha ao baixar {url}: {e}")


def _carregar_artefatos():
    """Itera sobre todos os artefatos definidos e garante sua presença local."""
    print("Verificando artefatos do modelo...")
    for chave, info in ARTEFATOS.items():
        download_file(info["url"], info["path"])
    print("Carga de artefatos finalizada.")

    log.info("Carregando artefatos do modelo...")
    modelo         = joblib.load(ARTEFATOS["modelo"]["path"])
    tfidf          = joblib.load(ARTEFATOS["tfidf"]["path"])
    feature_matrix = joblib.load(ARTEFATOS["matrix"]["path"])
    df_rec         = pd.read_csv(ARTEFATOS["data"]["path"])
    metadata_json  = ARTEFATOS["metadata"]["path"].read_text(encoding='utf-8')
    metadata       = json.loads(metadata_json)

    col_titulo = metadata["col_titulo"]
    col_autor  = metadata["col_autor"]
    col_rating = metadata["col_rating"]
    col_link   = metadata.get("col_link") 

    log.info(
        "Modelo '%s' carregado · %d livros indexados",
        metadata["melhor_modelo"],
        len(df_rec),
        "sim" if col_link else "não",
    )
    return modelo, tfidf, feature_matrix, df_rec, metadata, col_titulo, col_autor, col_rating, col_link


modelo, tfidf, feature_matrix, df_rec, metadata, COL_TITULO, COL_AUTOR, COL_RATING, COL_LINK = (
    _carregar_artefatos()
)

# ──────────────────────────────────────────────────────────────────────
# Aplicação FastAPI
# ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="📚 Biblioteca dos Corvos — ML API",
    description=(
        "API de classificação de popularidade e recomendação de livros "
        "baseada no dataset Goodreads 100k."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # restrinja em produção
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────
# Schemas (Pydantic)
# ──────────────────────────────────────────────────────────────────────
class ClassificarRequest(BaseModel):
    rating: float = Field(..., ge=0.0, le=5.0, description="Avaliação média (0–5)")
    num_avaliacoes: int = Field(..., ge=1, description="Número de avaliações")
    num_paginas: Optional[int] = Field(300, ge=1, le=10_000, description="Número de páginas")

    @field_validator("rating")
    @classmethod
    def validar_rating(cls, v: float) -> float:
        return round(v, 4)


class ClassificarResponse(BaseModel):
    popularidade: str
    probabilidades: dict[str, float]
    features_usadas: dict[str, float]


class RecomendarRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, description="Título ou autor")
    top_n: int = Field(10, ge=1, le=20, description="Número de recomendações")

    @field_validator("query")
    @classmethod
    def sanitizar_query(cls, v: str) -> str:
        return v.strip().lower()


class LivroRecomendado(BaseModel):
    titulo: str
    autor: str
    rating: float
    popularidade: str
    similaridade: float
    link: Optional[str] = Field(None, description="URL da página do livro no Goodreads")


class ReferenciaLivro(BaseModel):
    titulo: str
    link: Optional[str] = Field(None, description="URL da página do livro no Goodreads")


class RecomendarResponse(BaseModel):
    referencia: ReferenciaLivro
    total: int
    recomendacoes: List[LivroRecomendado]


class HealthResponse(BaseModel):
    status: str
    modelo: str
    livros_indexados: int
    f1_macro_treino: float
    acuracia_treino: float

# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────
def _extrair_link(row: pd.Series) -> Optional[str]:
    """Retorna o link do Goodreads de uma linha do DataFrame, ou None se ausente."""
    if COL_LINK is None:
        return None
    val = row.get(COL_LINK)
    if pd.isna(val) or str(val).strip() == "":
        return None
    return str(val).strip()


def _montar_features(rating: float, num_avaliacoes: int, num_paginas: int) -> np.ndarray:
    features = metadata["features"]
    pages_clip = min(num_paginas, 2000)

    valores = {
        metadata["col_rating"]: rating,
        "pages_clip":            pages_clip,
    }
    return np.array([[valores[f] for f in features]]), valores


def _buscar_indice(query: str) -> int:
    mask = df_rec["texto"].str.contains(query, regex=False, na=False)
    if mask.sum() > 0:
        return int(df_rec[mask].index[0])

    # Fallback: TF-IDF da query
    query_vec  = tfidf.transform([query])
    n_tfidf    = query_vec.shape[1]
    tfidf_only = feature_matrix[:, :n_tfidf]
    sim        = cosine_similarity(query_vec, tfidf_only).flatten()
    return int(sim.argmax())


# ──────────────────────────────────────────────────────────────────────
# Rotas
# ──────────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
def health():
    """Verifica se a API e o modelo estão operacionais."""
    return HealthResponse(
        status="ok",
        modelo=metadata["melhor_modelo"],
        livros_indexados=len(df_rec),
        f1_macro_treino=metadata["f1_macro_teste"],
        acuracia_treino=metadata["accuracy_teste"],
    )


@app.post("/classificar", response_model=ClassificarResponse, tags=["Classificação"])
def classificar(req: ClassificarRequest):
    """
    Classifica a popularidade de um livro com base em seus atributos.

    Retorna **Alta**, **Média** ou **Baixa** junto com as probabilidades
    estimadas pelo modelo.
    """
    X, valores = _montar_features(req.rating, req.num_avaliacoes, req.num_paginas or 300)

    predicao = modelo.predict(X)[0]

    if hasattr(modelo, "predict_proba"):
        proba_arr = modelo.predict_proba(X)[0]
        classes   = modelo.classes_
        probas    = {cls: round(float(p), 4) for cls, p in zip(classes, proba_arr)}
    else:
        probas = {predicao: 1.0}

    log.info("Classificação → %s (rating=%.2f, n=%d)", predicao, req.rating, req.num_avaliacoes)

    return ClassificarResponse(
        popularidade=predicao,
        probabilidades=probas,
        features_usadas={k: round(v, 4) for k, v in valores.items()},
    )


@app.post("/recomendar", response_model=RecomendarResponse, tags=["Recomendação"])
def recomendar(req: RecomendarRequest):
    """
    Recomenda livros similares com base em um título ou autor.

    Utiliza similaridade de cosseno sobre features TF-IDF (título + autor)
    combinadas com a avaliação média normalizada.
    """
    try:
        idx_base = _buscar_indice(req.query)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Nenhum livro encontrado para '{req.query}'") from exc

    vec_base  = feature_matrix[idx_base]
    sim_scores = cosine_similarity(vec_base, feature_matrix).flatten()
    top_idx   = sim_scores.argsort()[::-1][1 : req.top_n + 1]

    row_ref    = df_rec.iloc[idx_base]
    referencia = ReferenciaLivro(
        titulo=str(row_ref[COL_TITULO]),
        link=_extrair_link(row_ref),
    )

    recomendacoes = []
    for i in top_idx:
        row = df_rec.iloc[i]
        recomendacoes.append(
            LivroRecomendado(
                titulo=str(row[COL_TITULO]),
                autor=str(row[COL_AUTOR]),
                rating=round(float(row[COL_RATING]), 2),
                popularidade=str(row.get("popularidade", "N/A")),
                similaridade=round(float(sim_scores[i]), 4),
                link=_extrair_link(row),
            )
        )

    log.info("Recomendação para '%s' → %d livros", referencia.titulo, len(recomendacoes))

    return RecomendarResponse(
        referencia=referencia,
        total=len(recomendacoes),
        recomendacoes=recomendacoes,
    )

