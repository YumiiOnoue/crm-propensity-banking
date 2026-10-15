"""
Script de Treinamento e Comparação de Modelos de Propensão (CRM Banking).

Compara Regressão Logística, Random Forest e XGBoost, calibra o limiar ótimo
via validação cruzada no treino, avalia no teste (PR-AUC / Lift@10%) e persiste os artefatos.
"""

# Bibliotecas
import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

# Configurar caminhos do projeto
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.database import get_engine

# Hiperparâmetros e configurações globais
RANDOM_STATE = 42
TEST_SIZE = 0.20
CV_FOLDS = 5
COLUNAS_EXCLUIR = ["target", "duration", "campaign", "record_id"]


def carregar_dados() -> pd.DataFrame:
    """Carrega os dados tratados da camada de staging no MySQL."""
    print("Conectando ao banco de dados MySQL...")
    engine = get_engine()
    query = "SELECT * FROM stg_bank_marketing"
    df = pd.read_sql(query, con=engine)
    engine.dispose()
    print(f"Dados carregados com sucesso: {df.shape[0]:,} linhas e {df.shape[1]} colunas.")
    return df


def preparar_features(df: pd.DataFrame):
    """Separa variáveis preditoras e a variável alvo, catalogando os tipos."""
    colunas_excluir_presentes = [c for c in COLUNAS_EXCLUIR if c in df.columns]
    X = df.drop(columns=colunas_excluir_presentes).copy()
    y = df["target"].astype(int).copy()

    colunas_categoricas = X.select_dtypes(include=["object", "category", "bool", "string", "str"]).columns.tolist()
    colunas_numericas = X.select_dtypes(include=[np.number]).columns.tolist()

    # Suporte defensivo a diferentes nomenclaturas de pdays
    col_pdays = "pdays"
    colunas_numericas_gerais = [c for c in colunas_numericas if c != col_pdays]

    return X, y, colunas_numericas_gerais, colunas_categoricas, col_pdays


def criar_preprocessadores(colunas_numericas_gerais, colunas_categoricas, col_pdays):
    """Cria os pré-processadores adequados para modelos lineares e de árvore."""
    transformers_linear = [
        (
            "num",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]),
            colunas_numericas_gerais,
        ),
        (
            "cat",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", drop="first", sparse_output=False)),
            ]),
            colunas_categoricas,
        ),
    ]

    transformers_arvore = [
        ("num", SimpleImputer(strategy="median"), colunas_numericas_gerais),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), colunas_categoricas),
    ]

    # Adiciona tratamento específico de pdays se a coluna existir
    if col_pdays:
        transformers_linear.append((
            "pdays",
            Pipeline([
                ("imputer", SimpleImputer(strategy="constant", fill_value=-1)),
                ("scaler", StandardScaler()),
            ]),
            [col_pdays],
        ))
        transformers_arvore.append((
            "pdays",
            SimpleImputer(strategy="constant", fill_value=-1),
            [col_pdays],
        ))

    preproc_linear = ColumnTransformer(transformers=transformers_linear, remainder="drop")
    preproc_arvore = ColumnTransformer(transformers=transformers_arvore, remainder="drop")

    return preproc_linear, preproc_arvore


def calcular_threshold_otimo(y_true, probas) -> float:
    """Encontra o threshold que maximiza o F1-Score."""
    precisions, recalls, thresholds = precision_recall_curve(y_true, probas)
    f1_scores = (2 * precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    return float(thresholds[min(best_idx, len(thresholds) - 1)])


def main():
    # 1. Carga e Validação
    df = carregar_dados()
    X, y, col_num, col_cat, col_pdays = preparar_features(df)

    # 2. Divisão Estratificada (Treino / Teste)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    taxa_base_teste = float(y_test.mean())
    print(f"\nTreino: {X_train.shape[0]:,} | Teste: {X_test.shape[0]:,} (Taxa de aceite teste: {taxa_base_teste:.2%})")

    # 3. Pré-processadores
    preproc_linear, preproc_arvore = criar_preprocessadores(col_num, col_cat, col_pdays)

    # 4. Configuração dos Modelos
    scale_pos_weight = float((y_train == 0).sum() / (y_train == 1).sum())

    candidatos = {
        "LogisticRegression": Pipeline([
            ("preprocessamento", preproc_linear),
            ("classificador", LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=RANDOM_STATE
            )),
        ]),
        "RandomForest": Pipeline([
            ("preprocessamento", preproc_arvore),
            ("classificador", RandomForestClassifier(
                n_estimators=300,
                max_depth=10,
                min_samples_split=20,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1
            )),
        ]),
        "XGBoost": Pipeline([
            ("preprocessamento", preproc_arvore),
            ("classificador", XGBClassifier(
                n_estimators=250,
                learning_rate=0.05,
                max_depth=5,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=scale_pos_weight,
                random_state=RANDOM_STATE,
                eval_metric="logloss",
                n_jobs=-1
            )),
        ]),
    }

    # 5. Treinamento, Calibração de Threshold e Avaliação
    resultados = []
    modelos_treinados = {}
    probas_dict = {}
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    print("\nIniciando calibração, treinamento e avaliação...")
    for nome, pipe in candidatos.items():
        print(f"\n-> Processando {nome}...")
        
        # A. Calibração do limiar ótimo no treino usando Validação Cruzada (sem leakage)
        probas_cv_train = cross_val_predict(
            pipe, X_train, y_train, cv=cv, method="predict_proba", n_jobs=-1
        )[:, 1]
        best_threshold = calcular_threshold_otimo(y_train, probas_cv_train)
        print(f"   Threshold ótimo calibrado (CV Treino): {best_threshold:.4f}")

        # B. Ajuste do modelo no conjunto de treino completo
        pipe.fit(X_train, y_train)
        probas_test = pipe.predict_proba(X_test)[:, 1]
        preds_test = (probas_test >= best_threshold).astype(int)

        # C. Cálculo do Lift@10%
        df_lift = pd.DataFrame({
            "y_real": y_test.to_numpy(),
            "proba": probas_test
        }).sort_values(by="proba", ascending=False).reset_index(drop=True)

        n_top = int(np.ceil(len(df_lift) * 0.10))
        taxa_top10 = float(df_lift.head(n_top)["y_real"].mean())
        lift_10 = float(taxa_top10 / taxa_base_teste) if taxa_base_teste > 0 else 0.0

        resumo = {
            "modelo": nome,
            "roc_auc": float(roc_auc_score(y_test, probas_test)),
            "average_precision": float(average_precision_score(y_test, probas_test)),
            "threshold_otimo": best_threshold,
            "f1": float(f1_score(y_test, preds_test, zero_division=0)),
            "precision": float(precision_score(y_test, preds_test, zero_division=0)),
            "recall": float(recall_score(y_test, preds_test, zero_division=0)),
            "taxa_top_10_percent": taxa_top10,
            "lift_at_10_percent": lift_10,
        }

        resultados.append(resumo)
        modelos_treinados[nome] = pipe
        probas_dict[nome] = probas_test

    # 6. Seleção do Modelo Campeão
    df_resumos = pd.DataFrame(resultados).sort_values(by="average_precision", ascending=False).reset_index(drop=True)
    campeao_resumo = df_resumos.iloc[0].to_dict()
    campeao_nome = campeao_resumo["modelo"]
    campeao_pipe = modelos_treinados[campeao_nome]
    campeao_probas = probas_dict[campeao_nome]

    print("\n" + "=" * 65)
    print("RESUMO DO BENCHMARK DE MODELOS (CONJUNTO DE TESTE)")
    print("=" * 65)
    for res in resultados:
        print(f"Modelo: {res['modelo']:<18} | PR-AUC: {res['average_precision']:.4f} | ROC-AUC: {res['roc_auc']:.4f} | F1: {res['f1']:.4f} | Lift@10%: {res['lift_at_10_percent']:.2f}x")
    print(f"\n=> MODELO CAMPEÃO SELECIONADO: {campeao_nome}")

    # 7. Persistência dos Artefatos
    reports_dir = ROOT_DIR / "reports"
    models_dir = ROOT_DIR / "models"
    reports_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    # A. Salvar Modelo Treinado (.joblib)
    caminho_modelo = models_dir / "best_model.joblib"
    joblib.dump(campeao_pipe, caminho_modelo)
    print(f"\n[OK] Modelo campeão salvo")

    # B. Salvar Métricas e Esquema das Features (.json)
    caminho_metricas = reports_dir / "model_metrics.json"
    metricas_finais = {
        "modelo": campeao_nome,
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "cv_folds": CV_FOLDS,
        "feature_names": X.columns.tolist(),
        "threshold": campeao_resumo["threshold_otimo"],
        "roc_auc": campeao_resumo["roc_auc"],
        "average_precision": campeao_resumo["average_precision"],
        "precision": campeao_resumo["precision"],
        "recall": campeao_resumo["recall"],
        "f1": campeao_resumo["f1"],
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "positive_rate_test": taxa_base_teste,
        "baseline_acceptance_rate_test": taxa_base_teste,
        "top_10_percent_acceptance_rate": campeao_resumo["taxa_top_10_percent"],
        "lift_at_10_percent": campeao_resumo["lift_at_10_percent"],
        "top_10_percent_n": int(np.ceil(len(X_test) * 0.10)),
        "benchmark_comparativo": resultados,
    }

    with caminho_metricas.open("w", encoding="utf-8") as f:
        json.dump(metricas_finais, f, ensure_ascii=False, indent=4)
    print(f"[OK] Métricas salvas")

    # C. Salvar Scores de Teste Ordenados (.csv)
    df_scores = (
        pd.DataFrame({
            "y_real": y_test.to_numpy(),
            "probabilidade": campeao_probas,
        })
        .sort_values(by="probabilidade", ascending=False)
        .reset_index(drop=True)
    )
    df_scores.insert(0, "test_row_rank", np.arange(1, len(df_scores) + 1))

    caminho_scores = reports_dir / "test_propensity_scores.csv"
    df_scores.to_csv(caminho_scores, index=False)
    print(f"[OK] Scores de propensão salvos")


if __name__ == "__main__":
    main()