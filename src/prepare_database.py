"""Script de ingestão e preparação do banco de dados MySQL.

Valida as variáveis de ambiente (.env) e a integridade estrutural do ficheiro
CSV bruto (bank-full.csv). Cria/substitui a tabela de destino no banco de dados,
insere os registos em lotes (chunks) e executa a validação de contagem para
garantir a consistência da carga de dados.
"""

# Bibliotecas
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from sqlalchemy.types import Integer, VARCHAR

# Importa a conexão padronizada
from database import get_engine, ROOT_DIR

CSV_PATH = ROOT_DIR / "data" / "raw" / "bank-full.csv"
NOME_TABELA = "bank_full"

if not CSV_PATH.exists():
    raise FileNotFoundError(f"Arquivo CSV não encontrado em: {CSV_PATH}")

# Leitura e validação
df = pd.read_csv(CSV_PATH, sep=";")

colunas_esperadas = {
    "age", "job", "marital", "education", "default", "balance",
    "housing", "loan", "contact", "day", "month", "duration",
    "campaign", "pdays", "previous", "poutcome", "y",
}

colunas_ausentes = colunas_esperadas - set(df.columns)
if colunas_ausentes:
    raise ValueError(f"Colunas ausentes no CSV: {sorted(colunas_ausentes)}")

if df.empty:
    raise ValueError("O CSV está vazio.")

if df["y"].isna().any():
    raise ValueError("A coluna alvo 'y' possui valores nulos.")

# Mapeamento de tipos explícitos para o MySQL (evita criação de TEXT desnecessário)
dtypes = {
    "age": Integer(),
    "job": VARCHAR(50),
    "marital": VARCHAR(20),
    "education": VARCHAR(30),
    "default": VARCHAR(10),
    "balance": Integer(),
    "housing": VARCHAR(10),
    "loan": VARCHAR(10),
    "contact": VARCHAR(20),
    "day": Integer(),
    "month": VARCHAR(10),
    "duration": Integer(),
    "campaign": Integer(),
    "pdays": Integer(),
    "previous": Integer(),
    "poutcome": VARCHAR(30),
    "y": VARCHAR(10),
}

engine = get_engine()

try:
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))
    print("Conexão estabelecida com sucesso.")

    df.to_sql(
        name=NOME_TABELA,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=1000,
        dtype=dtypes,
    )

    with engine.connect() as conexao:
        total_importado = conexao.execute(
            text(f"SELECT COUNT(*) FROM `{NOME_TABELA}`")
        ).scalar_one()

    if total_importado != len(df):
        raise RuntimeError(
            f"Divergência na carga: CSV={len(df)}, Banco={total_importado}"
        )

    print(f"Carga concluída com sucesso: {total_importado:,} registros inseridos.")

finally:
    engine.dispose()