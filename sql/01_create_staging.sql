-- =============================================================================
-- Script: 01_create_staging.sql
-- Descrição: Criação da tabela de staging (`stg_bank_marketing`) a partir de `bank_full`.
-- Principais transformações:
--   - Limpeza de espaços em branco e conversão de strings vazias para NULL.
--   - Renomeação de atributos para maior clareza (`default_credit`, `pdays_since_contact`).
--   - Tratamento de sentinela: conversão de pdays = -1 para NULL.
--   - Engenharia de atributos inicial: criação da flag binária `previous_contact`.
--   - Binarização da variável alvo (`target`: 1 para 'yes', 0 para 'no').
-- =============================================================================

-- Verifica se a tabela de staging já existe e, se sim, remove-a para evitar conflitos na criação da nova tabela.
DROP TABLE IF EXISTS stg_bank_marketing;

-- Cria a tabela de staging com os dados do banco de marketing, aplicando transformações para limpeza e padronização dos dados.
CREATE TABLE stg_bank_marketing AS
SELECT
    age,
    NULLIF(TRIM(job), '') AS job,
    NULLIF(TRIM(marital), '') AS marital,
    NULLIF(TRIM(education), '') AS education,
    NULLIF(TRIM(`default`), '') AS default_credit,
    balance,
    NULLIF(TRIM(housing), '') AS housing,
    NULLIF(TRIM(loan), '') AS loan,
    NULLIF(TRIM(contact), '') AS contact,
    day,
    NULLIF(TRIM(month), '') AS month,
    campaign,
    NULLIF(pdays, -1) AS pdays,
    CASE
        WHEN pdays = -1 THEN 0
        ELSE 1
    END AS previous_contact,
    previous,
    NULLIF(TRIM(poutcome), '') AS poutcome,
    CASE
        WHEN LOWER(TRIM(y)) = 'yes' THEN 1
        WHEN LOWER(TRIM(y)) = 'no' THEN 0
        ELSE NULL
    END AS target
FROM bank_full;