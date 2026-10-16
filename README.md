# 🏦 CRM Banking: Modelo Preditivo de Propensão a Depósitos a Prazo

## 📌 Contexto

Este projeto demonstra uma solução analítica para apoiar a priorização de campanhas de CRM em uma instituição financeira.

O objetivo é estimar a propensão de contratação de uma oferta bancária a partir de dados históricos de campanhas, utilizando SQL para preparação e validação dos dados e Python para análise exploratória e modelagem preditiva.

## 💼 Problema de negócio

Como priorizar clientes para uma oferta bancária considerando a probabilidade estimada de aceitação, com o objetivo de apoiar o planejamento de campanhas de CRM?

## 📊 Dados

Os dados foram extraídos do [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/222/bank+marketing).
Para ver a descrição detalhada de cada atributo e tipos de dados, consulte o nosso [Dicionário de Dados](data/data_dictionary.md).

O dataset contém informações de campanhas de marketing direto de uma instituição financeira portuguesa. A variável-alvo indica se o cliente contratou um depósito a prazo.

* Público analisado: pessoa física.
* Variável-alvo: y, codificada como 0 ou 1.
* Unidade de análise: registro de campanha, não cliente individual identificado.
* Limitação: os dados não são provenientes do Bradesco.

## 💻 Tecnologias

* SQL e MySQL
* Python
* pandas e NumPy
* scikit-learn
* Matplotlib e Seaborn
* Git e GitHub

## 📋 Metodologia

* Importação e validação dos dados.
* Criação de tabelas brutas e tratadas no MySQL.
* Análise exploratória e investigação da taxa de aceitação.
* Preparação das variáveis e divisão estratificada entre treino e teste.
* Treinamento de modelos com pipeline de pré-processamento.
* Avaliação do modelo com PR-AUC, ROC-AUC, precisão e recall.
* Construção de um ranking de propensão e avaliação de lift@10%.
* Elaboração de recomendações para CRM.

## 📊 Resultados
Para evitar vazamento de dados (data leakage), atributos posteriores ao contato (como duration) e identificadores operacionais foram estritamente removidos.

A base foi dividida de forma estratificada em 80% treino (36.168 linhas) e 20% teste (9.043 linhas). Foram avaliados três algoritmos com tratamento específico de desbalanceamento de classes:

| Modelo | ROC-AUC | PR-AUC | Limiar Ótimo | F1​-Score | Precisão | Recall | Conversão Top 10% | Lift @10% | 
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| XGBoost | |  |  | |  |  |  |  |
| Regressão Logística |  |  |  | | |  |  |  |
| Random Forest |  |  |  |  |  |  | |  |



## 🎯 Recomendações Estratégicas para o CRM & Negócio



## 🚧 Limitações

* Dados históricos de uma instituição financeira portuguesa.
* Ausência de identificador individual real de cliente.
* Propensão não equivale a efeito causal da campanha.

## 🏗️ Arquitetura da Solução

O pipeline de dados e modelagem foi concebido de forma modular e auditável:

```text
crm-propensity-banking/
├── data/
│   └── raw/
│       └── bank-full.csv           # Base bruta de campanhas (45.211 registos)
│   └── README.md                   # Dicionário dos dados
├── sql/
│   ├── 01_create_staging.sql       # DDL/DML: limpeza, sentinelas e binarização do target
│   └── 02_quality_checks.sql       # Auditoria de volumetria, nulos e distribuição
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb # Análise exploratória e bivariada de propensão
│   └── 02_propensity_model.ipynb     # Comparativo de modelos, limiar ótimo e Lift
├── src/
│   ├── database.py                 # Conexão centralizada via SQLAlchemy / .env
│   ├── prepare_database.py         # Carga bruta automatizada do CSV para MySQL
│   └── train_model.py              # Script autônomo de treino e exportação de artefatos
├── reports/
│   ├── model_metrics.json          # Métricas de validação e benchmark dos modelos
│   └── test_propensity_scores.csv  # Base classificada e ranqueada por probabilidade
├── models/
│   └── best_model.joblib           # Pipeline do modelo campeão serializado
├── requirements.txt                # Dependências do ambiente Python
├── .gitignore
└── README.md
```

## 🚀 Como reproduzir o projeto

1. Clonar o repositório e configurar o ambiente

```Bash
git clone [https://github.com/YumiiOnoue/crm-propensity-banking.git](https://github.com/YumiiOnoue/crm-propensity-banking.git)
cd crm-propensity-banking

# Criar e ativar ambiente virtual (Conda)
conda create -n crm_env python=3.11 -y
conda activate crm_env

# Instalar dependências
pip install -r requirements.txt
```

2. Configurar variáveis de ambiente

Crie um ficheiro .env na raiz do projeto com as credenciais do seu banco de dados:

```Snippet de código
MYSQL_USER=seu_usuario
MYSQL_PASSWORD=sua_senha
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=crm_propensity_banking
```

3. Carga do banco de dados e execução do pipeline

```Bash
# Carga dos dados brutos no MySQL
python src/prepare_database.py

# Executar scripts SQL no banco (via MySQL Workbench, DBeaver ou terminal)
# - sql/01_create_staging.sql
# - sql/02_quality_checks.sql

# Treinar modelos, avaliar métricas e salvar artefatos
python src/train_model.py
```

Os artefatos gerados serão salvos automaticamente em:

* `reports/model_metrics.json`
* `reports/test_propensity_scores.csv`
* `models/best_model.joblib`

# 🛣️ Próximos passos

* Validar o modelo em campanhas futuras.
* Testar diferentes tamanhos de público prioritário.
* Realizar experimento controlado para medir o efeito incremental da campanha.
* Avaliar a integração com um ambiente de dados corporativo, como um lakehouse.
