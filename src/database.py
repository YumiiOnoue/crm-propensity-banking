"""Módulo de conexão e gerenciamento do banco de dados MySQL.

Carrega as credenciais a partir do arquivo .env e fornece a engine de conexão
do SQLAlchemy configurada (com pool_pre_ping) para consumo padronizado por
outros módulos do projeto.
"""

# Bibliotecas
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine

# Ancorado na pasta raiz assumindo que este arquivo está em src/
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"

# Criação da Engine de Conexão MySQL via SQLAlchemy
def get_engine():
    load_dotenv(ENV_PATH, override=True)

    usuario = os.getenv("MYSQL_USER")
    senha = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST", "localhost")
    porta = int(os.getenv("MYSQL_PORT", "3306"))
    banco = os.getenv("MYSQL_DATABASE", "crm_propensity_banking")

    if not usuario or not senha:
        raise ValueError("Configure MYSQL_USER e MYSQL_PASSWORD no arquivo .env.")

    url_conexao = URL.create(
        drivername="mysql+pymysql",
        username=usuario,
        password=senha,
        host=host,
        port=porta,
        database=banco,
    )
    return create_engine(url_conexao, pool_pre_ping=True)