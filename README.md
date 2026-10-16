# 🏦 CRM Banking: Modelo Preditivo de Propensão a Depósitos a Prazo

## 📌 Contexto

Este projeto demonstra uma solução analítica para apoiar a priorização de campanhas de CRM em uma instituição financeira.

O objetivo é estimar a propensão de contratação de uma oferta bancária a partir de dados históricos de campanhas, utilizando SQL para preparação e validação dos dados e Python para análise exploratória e modelagem preditiva.

## 💼 Problema de negócio

Como priorizar clientes para uma oferta bancária considerando a probabilidade estimada de aceitação, com o objetivo de apoiar o planejamento de campanhas de CRM?

## 📊 Dados

Os dados foram extraídos do [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/222/bank+marketing).
Para ver a descrição detalhada de cada atributo e tipos de dados, consulte o nosso [Dicionário de Dados](data/README.md).

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

| Modelo | ROC-AUC | PR-AUC | Limiar Ótimo | F1-Score | Precisão | Recall | Conversão Top 10% | Lift @10% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| XGBoost 🏆 | 0.8018 | 0.4640 | 0.6491 | 0.4988 | 0.4922 | 0.5057 | 52.71% | 4.51x |
| Regressão Logística | 0.7686 | 0.4051 | 0.6352 | 0.4476 | 0.4511 | 0.4442 | 47.85% | 4.09x |
| Random Forest | 0.7950 | 0.4380 | 0.6133 | 0.4752 | 0.4583 | 0.4934 | 50.17% | 4.29x |



## 🎯 Recomendações Estratégicas para o CRM & Negócio

Com base nos padrões identificados na análise exploratória e nas probabilidades geradas pelo modelo preditivo, estruturaram-se recomendações táticas e estratégicas para otimizar as campanhas de telemarketing e a alocação de recursos operacionais:

**1. Estratégia de Priorização por Decis (Eficiência do Call Center)**
* **Foco no Top 10% mais propenso:** Ao priorizar o primeiro decil de clientes classificados pelo modelo (`test_propensity_scores.csv`), a taxa de conversão sobe de **11,70% (média da base)** para **52,71%**, representando um **Lift de 4,51x**.
* **Segmentação da Régua de Contacto:**
  * **Alta Propensão (probabilidade maior ou igual a 0,64):** Encaminhar para contacto telefónico ativo com operadores seniores ou consultores dedicados a investimentos.
  * **Média Propensão (probabilidade entre 0,35 e 0,64):** Ativação por canais digitais de baixo custo (notificações *push* na app, e-mail marketing ou banners personalizados no *internet banking*).
  * **Baixa Propensão (probabilidade menor que 0,35):** Excluir de campanhas ativas de curto prazo para evitar fadiga de contacto e desperdício de orçamento.

**2. Gestão do Histórico do Cliente (*Relationship Banking*)**
* **Régua Prioritária para Sucesso Prévio (`poutcome = 'success'`):** Clientes que aderiram a produtos em campanhas anteriores apresentaram uma propensão multiplicada por mais de **10 vezes** (Odds Ratio aproximadamente 10,56). Este grupo deve ter atendimento preferencial no lançamento de novos produtos financeiros.
* **Política de Recontacto (`pdays` e `campaign`):** Clientes contatados repetidamente na mesma campanha sem conversão tendem a apresentar taxa de rejeição progressiva. Recomenda-se estipular uma política de tolerância máxima (ex.: fixar quantidade de tentativas por período) para mitigar insatisfação e proteger a reputação da marca.

**3. Ajuste de Calendário e Sazonalidade**
* **Alocação de Esforço Comercial:** Concentrar campanhas nos meses com maiores probabilidades históricas de adesão:
  * **Março (Odds Ratio aproximadamente 3,06):** Período de planeamento fiscal e rebalanceamento de carteiras.
  * **Outubro e Dezembro (Odds Ratio maior ou igual a 2,15):** Meses com injeção de liquidez adicional (subsídios de férias e fim de ano).
* **Desaceleração em Meses de Baixa Resposta:** Em meses como janeiro (Odds Ratio aproximadamente 0,34) e agosto (Odds Ratio aproximadamente 0,40), reduzir o volume de chamadas ativas para depósitos a prazo, redirecionando o esforço para outros produtos.

**4. Segmentação por Ocupação e Situação Financeira**
* **Aposta em Perfis Conservadores:** Clientes aposentados (taxa de adesão média de **22,79%**) e estudantes (**28,68%**) têm respostas acima do dobro da média global:
  * *Aposentados:* Têm preferência por aplicações previsíveis e com baixo risco de capital, alinhando-se com depósitos a prazo fixo.
  * *Estudantes:* Apresentam apetite por produtos com baixos montantes mínimos de entrada e objetivos de poupança definidos.
* **Atenção ao Crédito à Habitação (`housing = 'yes'`):** Clientes com prestações imobiliárias ativas têm taxas de adesão significativamente menores a depósitos a prazo devido ao comprometimento da renda mensal. Para este perfil, produtos com liquidez diária ou planos de amortização são mais recomendados.

**5. Higienização Cadastral e Governança de Canais**
* **Qualificação de Contactos:** Clientes com canal de contacto desconhecido (`contact = 'unknown'`) apresentaram redução de **70%** na probabilidade de adesão (Odds Ratio aproximadamente 0,30). 
* **Ação Corretiva:** Implementar gatilhos de atualização de número de contato e e-mail no login da aplicação bancária antes da execução de novas campanhas.

**6. Métricas de Acompanhamento e Governança (MLOps)**
* **Testes A/B em Produção:** Manter um grupo de controle de 10% da base abordado de forma aleatória para mensurar continuamente o ganho financeiro incremental (*uplift*) do modelo.
* **Monitorização de Desvio (*Data Drift*):** Auditar trimestralmente a estabilidade das distribuições demográficas e macroeconômicas para identificar eventuais quedas de desempenho no limiar de corte (0,64).


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

## 🛣️ Próximos passos

* Validar o modelo em campanhas futuras.
* Testar diferentes tamanhos de público prioritário.
* Realizar experimento controlado para medir o efeito incremental da campanha.
* Avaliar a integração com um ambiente de dados corporativo, como um lakehouse.
