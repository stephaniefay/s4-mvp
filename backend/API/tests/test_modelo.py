from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# ──────────────────────────────────────────────────────────────────────
# Caminhos
# ──────────────────────────────────────────────────────────────────────
REPO_ROOT  = Path(__file__).resolve().parent.parent.parent
API_DIR    = REPO_ROOT / "machine_learning" / "model"

MODEL_PATH    = API_DIR / "modelo_popularidade.pkl"
DATA_PATH     = API_DIR / "goodreads_rec.csv"
METADATA_PATH = API_DIR / "model_metadata.json"

THRESHOLD_ACCURACY = 0.50
THRESHOLD_F1_MACRO = 0.40
OVERFITTING_CEILING = 0.99 

# ──────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def metadata() -> dict:
    if not METADATA_PATH.exists():
        pytest.skip(f"Arquivo não encontrado: {METADATA_PATH}")
    return json.loads(METADATA_PATH.read_text())


@pytest.fixture(scope="module")
def modelo(metadata):
    if not MODEL_PATH.exists():
        pytest.skip(f"Arquivo não encontrado: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


@pytest.fixture(scope="module")
def dados_teste(metadata):
    if not DATA_PATH.exists():
        pytest.skip(f"Arquivo não encontrado: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    col_rating  = metadata["col_rating"]
    col_count   = metadata["col_count"]
    col_paginas = metadata.get("col_paginas")
    features    = metadata["features"]
    p25         = metadata["p25"]
    p75         = metadata["p75"]

    # 1. Geração do Target
    def classificar(n: float) -> str:
        if n >= p75:   return "Alta"
        elif n >= p25: return "Média"
        else:          return "Baixa"

    df["popularidade"] = df[col_count].apply(classificar)

    # 2. Engenharia de Features (Rebatendo o que o modelo espera)
    df["log_count"]    = np.log1p(df[col_count])
    df["rating_x_log"] = df[col_rating] * df["log_count"]

    # CORREÇÃO: Garantindo a existência da pages_clip (mesmo que com zeros)
    if col_paginas and col_paginas in df.columns:
        df["pages_clip"] = df[col_paginas].clip(0, 2000)
    else:
        df["pages_clip"] = 0 

    # Validação de segurança: Todas as features esperadas existem no DF?
    missing_cols = set(features) - set(df.columns)
    if missing_cols:
        pytest.fail(f"As seguintes features esperadas não foram encontradas: {missing_cols}")

    X = df[features].values
    y = df["popularidade"].values

    # Separando treino/teste com a mesma semente do notebook
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    return X_test, y_test


# ──────────────────────────────────────────────────────────────────────
# Testes
# ──────────────────────────────────────────────────────────────────────

class TestCargaDoModelo:
    def test_modelo_nao_e_none(self, modelo):
        assert modelo is not None

    def test_modelo_tem_metodo_predict(self, modelo):
        assert hasattr(modelo, "predict")

    def test_modelo_tem_metodo_predict_proba(self, modelo):
        assert hasattr(modelo, "predict_proba")


class TestDesempenhoNoTeste:
    def test_acuracia_minima(self, modelo, dados_teste):
        X_test, y_test = dados_teste
        y_pred = modelo.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        assert acc >= THRESHOLD_ACCURACY

    def test_f1_macro_minimo(self, modelo, dados_teste):
        X_test, y_test = dados_teste
        y_pred = modelo.predict(X_test)
        f1 = f1_score(y_test, y_pred, average="macro")
        assert f1 >= THRESHOLD_F1_MACRO

    def test_sem_overfitting_suspeito(self, modelo, dados_teste):
        """
        Se este teste falhar mesmo com o código novo, significa que as 
        features 'log_count' ou 'rating_x_log' precisam ser removidas do seu 
        PROCESSO DE TREINAMENTO no notebook, pois elas revelam o target.
        """
        X_test, y_test = dados_teste
        y_pred = modelo.predict(X_test)
        f1 = f1_score(y_test, y_pred, average="macro")
        assert f1 < OVERFITTING_CEILING, f"Data Leakage detectado! F1: {f1:.4f}"


class TestFormatoDaPredicao:
    CLASSES_ESPERADAS = {"Alta", "Média", "Baixa"}

    def test_predicao_retorna_array(self, modelo, dados_teste):
        X_test, _ = dados_teste
        y_pred = modelo.predict(X_test[:5])
        assert len(y_pred) == 5

    def test_classes_validas(self, modelo, dados_teste):
        X_test, _ = dados_teste
        y_pred = modelo.predict(X_test[:50])
        assert set(y_pred).issubset(self.CLASSES_ESPERADAS)


class TestConsistenciaComMetadata:
    TOLERANCIA = 0.05 

    def test_acuracia_consistente_com_notebook(self, modelo, dados_teste, metadata):
        X_test, y_test = dados_teste
        y_pred = modelo.predict(X_test)
        acc_atual = accuracy_score(y_test, y_pred)
        acc_registrada = metadata["accuracy_teste"]
        assert abs(acc_atual - acc_registrada) <= self.TOLERANCIA