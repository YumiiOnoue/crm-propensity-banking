
-- 1. Comparação entre base bruta e base tratada
SELECT
    (SELECT COUNT(*) FROM bank_full)
        AS raw_rows,
    (SELECT COUNT(*) FROM stg_bank_marketing)
        AS staging_rows;

-- 2. Distribuição da variável-alvo
SELECT
    target,
    COUNT(*) AS total,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM stg_bank_marketing),
        2
    ) AS percentage
FROM stg_bank_marketing
GROUP BY target
ORDER BY target;

-- 3. Valores ausentes nas variáveis categóricas
SELECT
    SUM(CASE WHEN job IS NULL THEN 1 ELSE 0 END)
        AS missing_job,
    SUM(CASE WHEN education IS NULL THEN 1 ELSE 0 END)
        AS missing_education,
    SUM(CASE WHEN poutcome IS NULL THEN 1 ELSE 0 END)
        AS missing_poutcome
FROM stg_bank_marketing;

-- 4. Validação de idades
SELECT
    MIN(age) AS min_age,
    MAX(age) AS max_age,
    SUM(CASE WHEN age <= 0 THEN 1 ELSE 0 END)
        AS invalid_ages
FROM stg_bank_marketing;

-- 5. Registros sem alvo válido
SELECT COUNT(*) AS invalid_targets
FROM stg_bank_marketing
WHERE target IS NULL;

-- 6. Taxa de aceitação por ocupação
SELECT
    job,
    COUNT(*) AS customers,
    ROUND(AVG(target) * 100, 2) AS acceptance_rate_pct
FROM stg_bank_marketing
WHERE target IS NOT NULL
GROUP BY job
ORDER BY acceptance_rate_pct DESC;
