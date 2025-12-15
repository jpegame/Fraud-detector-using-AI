# Como Executar o Projeto

Guia passo a passo para rodar o pipeline completo e visualizar os resultados do Machine Learning.

---

## Pré-requisitos

- VM Ubuntu Server 25 com Docker instalado
- Python 3 com ambiente virtual (.venv)
- Conexão com MongoDB Atlas configurada
- Arquivo `.env` configurado na pasta `docker/`

---

## Passo 1: Iniciar o MySQL

```sh
cd docker
docker compose up -d
```

Aguarde o container iniciar (cerca de 30 segundos).

---

## Passo 2: Importar os dados

### Importar para MySQL
```sh
cd scripts
python import_csv.py
```

### Importar para MongoDB
```sh
python import_csv_mongo.py
```

---

## Passo 3: Executar o Pipeline Completo

```sh
airflow standalone
```

Copie o usuario e senha do arquivo: simple_auth_manager_passwords.json.generated.
Acesse a aba DAGS que aparecerá a tarefa que pode ser executada por lá

Isso executa automaticamente:
1. **Bronze** → Extrai dados do MySQL e MongoDB, salva em `.txt`
2. **Silver** → Processa e salva DataFrame em `.pkl`
3. **Gold** → Persiste em SQLite
4. **ML** → Treina o modelo RandomForest

---

## Passo 4: Ver Resultados do Machine Learning

```sh
python test_ml.py
```

### O que vai aparecer na tela:

```
==================================================
RESULTADO DO MODELO DE DETECCAO DE FRAUDES
==================================================

Total de transacoes analisadas: 284807
Transacoes normais (predicao): 284315
Fraudes detectadas (predicao): 492

Fraudes reais no dataset: 492
Acuracia: 99.85%

==================================================
EXEMPLOS DE PREDICOES
==================================================

--- 5 Transacoes NORMAIS detectadas ---
Transacao 0: Predicao=Normal, Real=Normal
Transacao 1: Predicao=Normal, Real=Normal

--- 5 Transacoes FRAUDE detectadas ---
Transacao 492: Predicao=FRAUDE, Real=FRAUDE
Transacao 493: Predicao=FRAUDE, Real=FRAUDE

==================================================
IMPORTANCIA DAS FEATURES (Top 10)
==================================================
V14: 0.1523
V17: 0.1245
V12: 0.1087
```

---

## Alternativa: Executar via Airflow

### 1. Copie a DAG
```sh
cp dags/fraud_detection_dag.py ~/airflow/dags/
```

### 2. Inicie o Airflow
```sh
airflow standalone
```

### 3. Acesse a interface
Abra o navegador em `http://localhost:8080`

### 4. Ative a DAG
Procure por `fraud_detection_pipeline` e clique no toggle para ativar.

---

## Onde ficam os arquivos gerados

| Camada | Arquivo | Localização |
|--------|---------|-------------|
| Bronze | Dados brutos | `data/bronze/*.txt` |
| Silver | DataFrame processado | `data/silver/silver_data.pkl` |
| Gold | Banco SQLite | `data/gold/gold.db` |
| ML | Modelo treinado | `models/fraud_model.pkl` |

---

## Consultar dados no SQLite (Gold)

```sh
sqlite3 data/gold/gold.db
```

Dentro do SQLite:
```sql
SELECT COUNT(*) FROM credit_card_gold;
SELECT * FROM credit_card_gold WHERE Class = 1 LIMIT 10;
.exit
```

---

## Resumo dos comandos

```sh
# 1. Subir banco
cd docker && docker compose up -d

# 2. Importar dados
cd scripts
python import_csv.py
python import_csv_mongo.py

# 3. Rodar pipeline
python run_pipeline.py

# 4. Ver resultados ML
python test_ml.py
```
