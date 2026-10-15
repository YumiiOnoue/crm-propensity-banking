# Dicionário de Dados: Bank Marketing Dataset

- **Fonte:** [UCI Machine Learning Repository - Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)
- **Origem:** Instituição bancária portuguesa (campanhas de marketing direto por telefone).
- **Objetivo:** Prever se o cliente vai aderir um depósito a prazo (variável binária `y`).
- **Dimensões do arquivo `bank-full.csv`:** 45.211 linhas e 17 atributos.

---

## Atributos do Cliente (Dados Bancários)

| Coluna | Tipo | Descrição | Valores Possíveis / Exemplo |
| :--- | :--- | :--- | :--- |
| `age` | Numérico (`int`) | Idade do cliente | Ex: 18 a 95 |
| `job` | Categórico (`string`) | Tipo de emprego/profissão | `admin.`, `unknown`, `unemployed`, `management`, `housemaid`, `entrepreneur`, `student`, `blue-collar`, `self-employed`, `retired`, `technician`, `services` |
| `marital` | Categórico (`string`) | Estado civil | `married`, `divorced`, `single` (nota: `divorced` inclui viúvos) |
| `education` | Categórico (`string`) | Nível de escolaridade | `unknown`, `secondary`, `primary`, `tertiary` |
| `default` | Binário (`string`) | Possui crédito em incumprimento? | `yes`, `no` |
| `balance` | Numérico (`int`) | Saldo médio bancário anual em euros | Ex: -8019 a 102127 |
| `housing` | Binário (`string`) | Possui crédito à habitação? | `yes`, `no` |
| `loan` | Binário (`string`) | Possui empréstimo pessoal? | `yes`, `no` |

---

## Atributos Relacionados com o Último Contato da Campanha Atual

| Coluna | Tipo | Descrição | Valores Possíveis / Exemplo |
| :--- | :--- | :--- | :--- |
| `contact` | Categórico (`string`) | Tipo de comunicação de contato | `unknown`, `telephone`, `cellular` |
| `month` | Categórico (`string`) | Último mês em que foi contatado | `jan`, `feb`, `mar`, ..., `nov`, `dec` |
| `day` | Numérico (`int`) | Último dia do mês em que foi contatado | 1 a 31 |
| `duration` | Numérico (`int`) | Duração da última chamada em segundos | Ex: 0 a 4918 |

---

## Outros Atributos da Campanha

| Coluna | Tipo | Descrição | Valores Possíveis / Exemplo |
| :--- | :--- | :--- | :--- |
| `campaign` | Numérico (`int`) | Número de contatos realizados durante esta campanha para este cliente | Inclui o último contato (1 a 63) |
| `pdays` | Numérico (`int`) | Dias decorridos após o último contato de campanha anterior | `-1` indica que o cliente não foi contatado anteriormente |
| `previous` | Numérico (`int`) | Número de contatos realizados antes desta campanha para este cliente | 0 a 275 |
| `poutcome` | Categórico (`string`) | Resultado da campanha de marketing anterior | `unknown`, `other`, `failure`, `success` |

---

## Variável Alvo (Target)

| Coluna | Tipo | Descrição | Valores Possíveis |
| :--- | :--- | :--- | :--- |
| `y` | Binário (`string`) | O cliente subscreveu o depósito a prazo? | `yes`, `no` |

---

## Referência

> S. Moro, P. Cortez and P. Rita. *A Data-Driven Approach to Predict the Success of Bank Telemarketing.* Decision Support Systems, Elsevier, 62:22-31, June 2014.