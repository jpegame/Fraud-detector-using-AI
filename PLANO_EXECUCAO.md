# 📋 Plano de Execução - Fraud Detector Project

**Prazo estimado**: 2-3 semanas  
**Objetivo**: Finalizar pipeline ETL completo com arquitetura Medalhão e orquestração Airflow

---

## 🎯 Fase 1: Consolidação da Base (3-4 dias)

### ✅ 1.1 Padronizar Configurações
**Objetivo**: Centralizar todas as configurações em `.env`

**Tarefas**:
- [ ] Atualizar `docker/example.env` com todas as variáveis necessárias:
  ```env
  # MySQL
  MYSQL_ROOT_PASSWORD=root123
  MYSQL_DATABASE=creditdb
  MYSQL_TABLE=transactions
  MYSQL_CSV_FILE=/app/data/credit-card1.csv
  
  # MongoDB
  MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
  MONGO_DATABASE=frauddb
  MONGO_COLLECTION=transactions
  
  # Paths
  BRONZE_DIR=/app/bronze
  SILVER_DIR=/app/silver
  GOLD_DIR=/app/gold
  DATA_DIR=/app/data
  
  # Retry configs
  DB_RETRY_COUNT=10
  DB_RETRY_DELAY=3
  ```

- [ ] Atualizar `requirements.txt` com todas as dependências:
  ```
  python-dotenv==1.2.1
  mysql-connector-python==9.5.0
  pymongo==4.6.0
  pandas==2.1.4
  pyarrow==14.0.1
  scikit-learn==1.3.2
  apache-airflow==2.8.0
  ```

- [ ] Criar script de validação de ambiente (`scripts/validate_env.py`)

**Resultado esperado**: Ambiente configurável e reproduzível

---

### ✅ 1.2 Refatorar Scripts Existentes
**Objetivo**: Aplicar boas práticas e usar `.env` em todos os scripts

**Tarefas**:
- [ ] Refatorar `scripts/import_csv.py` para usar `.env`
- [ ] Refatorar `scripts/bronze_mysql.py` para usar `.env`
- [ ] Criar `scripts/import_mysql.py` unificado (se necessário)
- [ ] Adicionar tratamento de erros e logging em todos os scripts
- [ ] Criar funções reutilizáveis em `scripts/utils.py`:
  - `get_mysql_connection()`
  - `get_mongo_connection()`
  - `setup_logger()`
  - `validate_data()`

**Resultado esperado**: Scripts limpos, configuráveis e com logs

---

### ✅ 1.3 Criar Estrutura de Pastas Completa
**Objetivo**: Garantir que todas as pastas necessárias existam

**Tarefas**:
- [ ] Criar estrutura:
  ```
  bronze/
    mysql/
    mongo/
  silver/
    cleaned/
    normalized/
  gold/
    aggregated/
    features/
  logs/
  tests/
  airflow/
    dags/
    logs/
    plugins/
  ```

- [ ] Adicionar `.gitkeep` nas pastas vazias
- [ ] Atualizar `.gitignore` para ignorar dados sensíveis

**Resultado esperado**: Estrutura organizada e versionada

---

## 🥉 Fase 2: Camada Bronze (2-3 dias)

### 📥 2.1 Bronze - MySQL
**Objetivo**: Extrair dados do MySQL para formato JSON Lines

**Tarefas**:
- [ ] Finalizar `scripts/bronze_mysql.py`:
  - Ler configurações do `.env`
  - Conectar ao MySQL
  - Extrair todas as linhas da tabela `transactions`
  - Salvar em `bronze/mysql/credit_card1.txt` (JSON Lines)
  - Adicionar timestamp e metadata
  - Implementar checkpoint/resume (caso falhe)
  - Adicionar validação de dados extraídos

**Código base**:
```python
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
from utils import get_mysql_connection, setup_logger

def extract_mysql_to_bronze():
    """Extrai dados do MySQL para camada Bronze"""
    logger = setup_logger('bronze_mysql')
    
    # Conectar ao MySQL
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Extrair dados
    table = os.getenv('MYSQL_TABLE', 'transactions')
    cursor.execute(f"SELECT * FROM {table}")
    
    # Salvar em Bronze
    bronze_path = f"{os.getenv('BRONZE_DIR')}/mysql/credit_card1.txt"
    os.makedirs(os.path.dirname(bronze_path), exist_ok=True)
    
    count = 0
    with open(bronze_path, 'w', encoding='utf-8') as f:
        for row in cursor:
            # Adicionar metadata
            row['_extracted_at'] = datetime.utcnow().isoformat()
            row['_source'] = 'mysql'
            f.write(json.dumps(row, default=str) + '\n')
            count += 1
    
    logger.info(f"Extracted {count} rows to {bronze_path}")
    cursor.close()
    conn.close()
```

**Resultado esperado**: Arquivo `bronze/mysql/credit_card1.txt` com dados brutos

---

### 📥 2.2 Bronze - MongoDB
**Objetivo**: Extrair dados do MongoDB para formato JSON Lines

**Tarefas**:
- [ ] Criar `scripts/bronze_mongo.py`:
  - Ler configurações do `.env`
  - Conectar ao MongoDB Atlas (ou local)
  - Extrair todos os documentos da collection
  - Salvar em `bronze/mongo/credit_card2.txt` (JSON Lines)
  - Adicionar timestamp e metadata
  - Implementar paginação (batches de 1000)
  - Adicionar validação de dados extraídos

**Código base**:
```python
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from utils import get_mongo_connection, setup_logger

def extract_mongo_to_bronze():
    """Extrai dados do MongoDB para camada Bronze"""
    logger = setup_logger('bronze_mongo')
    
    # Conectar ao MongoDB
    client = get_mongo_connection()
    db = client[os.getenv('MONGO_DATABASE')]
    collection = db[os.getenv('MONGO_COLLECTION')]
    
    # Extrair dados
    bronze_path = f"{os.getenv('BRONZE_DIR')}/mongo/credit_card2.txt"
    os.makedirs(os.path.dirname(bronze_path), exist_ok=True)
    
    count = 0
    batch_size = 1000
    
    with open(bronze_path, 'w', encoding='utf-8') as f:
        cursor = collection.find({}).batch_size(batch_size)
        for doc in cursor:
            # Converter ObjectId para string
            doc['_id'] = str(doc['_id'])
            doc['_extracted_at'] = datetime.utcnow().isoformat()
            doc['_source'] = 'mongodb'
            f.write(json.dumps(doc, default=str) + '\n')
            count += 1
    
    logger.info(f"Extracted {count} documents to {bronze_path}")
    client.close()
```

**Resultado esperado**: Arquivo `bronze/mongo/credit_card2.txt` com dados brutos

---

### ✅ 2.3 Validação da Camada Bronze
**Tarefas**:
- [ ] Criar `scripts/validate_bronze.py`:
  - Contar linhas em cada arquivo Bronze
  - Validar estrutura JSON
  - Verificar campos obrigatórios
  - Comparar contagens com fontes originais
  - Gerar relatório de validação

**Resultado esperado**: Relatório confirmando integridade dos dados Bronze

---

## 🥈 Fase 3: Camada Silver (3-4 dias)

### 🧹 3.1 Silver - Limpeza e Normalização
**Objetivo**: Transformar dados brutos em dados limpos e padronizados

**Tarefas**:
- [ ] Criar `scripts/silver_clean.py`:
  - Ler arquivos Bronze (MySQL + MongoDB)
  - Unificar schemas (padronizar nomes de colunas)
  - Tratar valores nulos/missing
  - Converter tipos de dados corretamente
  - Remover duplicatas
  - Normalizar valores (ex: `Amount` para float)
  - Validar consistência dos dados
  - Salvar como Parquet em `silver/cleaned/`

**Transformações necessárias**:
```python
import pandas as pd
import json

def load_bronze_to_df(bronze_path):
    """Carrega JSON Lines para DataFrame"""
    data = []
    with open(bronze_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return pd.DataFrame(data)

def clean_transactions(df):
    """Limpa e padroniza dados de transações"""
    # Remover duplicatas
    df = df.drop_duplicates()
    
    # Converter tipos
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Class'] = df['Class'].astype(int)
    
    # Tratar nulos
    df = df.dropna(subset=['Class'])  # Class não pode ser nulo
    df['Amount'] = df['Amount'].fillna(0)
    
    # Remover colunas de metadata
    metadata_cols = [c for c in df.columns if c.startswith('_')]
    df = df.drop(columns=metadata_cols)
    
    return df

def process_silver():
    """Processa camada Silver"""
    # Carregar Bronze
    df_mysql = load_bronze_to_df('bronze/mysql/credit_card1.txt')
    df_mongo = load_bronze_to_df('bronze/mongo/credit_card2.txt')
    
    # Limpar
    df_mysql_clean = clean_transactions(df_mysql)
    df_mongo_clean = clean_transactions(df_mongo)
    
    # Combinar
    df_combined = pd.concat([df_mysql_clean, df_mongo_clean], ignore_index=True)
    
    # Salvar
    df_combined.to_parquet('silver/cleaned/transactions.parquet', index=False)
    
    return df_combined
```

**Resultado esperado**: Arquivo `silver/cleaned/transactions.parquet` com dados limpos

---

### 📊 3.2 Silver - Feature Engineering
**Objetivo**: Criar features derivadas para análise e ML

**Tarefas**:
- [ ] Criar `scripts/silver_features.py`:
  - Calcular estatísticas por transação
  - Criar features temporais (hora do dia, dia da semana)
  - Normalizar valores (StandardScaler para V1-V28)
  - Criar bins para Amount (faixas de valor)
  - Adicionar flags (is_fraud, is_high_value, etc.)
  - Salvar em `silver/normalized/transactions_features.parquet`

**Features a criar**:
```python
def create_features(df):
    """Cria features derivadas"""
    # Features temporais
    df['hour'] = (df['Time'] / 3600) % 24
    df['day'] = (df['Time'] / 86400).astype(int)
    
    # Categorias de valor
    df['amount_category'] = pd.cut(
        df['Amount'], 
        bins=[0, 10, 50, 100, 500, float('inf')],
        labels=['very_low', 'low', 'medium', 'high', 'very_high']
    )
    
    # Normalização de Amount
    df['amount_normalized'] = (df['Amount'] - df['Amount'].mean()) / df['Amount'].std()
    
    # Flags
    df['is_fraud'] = df['Class'] == 1
    df['is_high_value'] = df['Amount'] > 500
    
    return df
```

**Resultado esperado**: Arquivo com features prontas para análise

---

### ✅ 3.3 Validação da Camada Silver
**Tarefas**:
- [ ] Criar `scripts/validate_silver.py`:
  - Verificar qualidade dos dados (% nulos, duplicatas)
  - Validar distribuições estatísticas
  - Verificar correlações entre features
  - Gerar relatório de qualidade
  - Criar visualizações básicas (opcional)

**Resultado esperado**: Relatório de qualidade dos dados Silver

---

## 🥇 Fase 4: Camada Gold (2-3 dias)

### 📈 4.1 Gold - Agregações e Métricas
**Objetivo**: Criar tabelas analíticas prontas para consumo

**Tarefas**:
- [ ] Criar `scripts/gold_aggregations.py`:
  - Conectar ao SQLite (`gold/analytics.db`)
  - Criar tabelas agregadas:
    - `fraud_stats`: estatísticas de fraude (total, taxa, valor médio)
    - `hourly_transactions`: transações por hora
    - `amount_distribution`: distribuição de valores
    - `fraud_by_category`: fraudes por categoria de valor
  - Criar índices para performance
  - Adicionar timestamps de processamento

**Tabelas a criar**:
```python
import sqlite3
import pandas as pd

def create_gold_tables(df):
    """Cria tabelas Gold no SQLite"""
    conn = sqlite3.connect('gold/analytics.db')
    
    # 1. Estatísticas gerais de fraude
    fraud_stats = df.groupby('Class').agg({
        'Amount': ['count', 'sum', 'mean', 'median'],
        'Time': ['min', 'max']
    }).reset_index()
    fraud_stats.to_sql('fraud_stats', conn, if_exists='replace', index=False)
    
    # 2. Transações por hora
    hourly = df.groupby('hour').agg({
        'Class': ['count', 'sum'],
        'Amount': ['sum', 'mean']
    }).reset_index()
    hourly.to_sql('hourly_transactions', conn, if_exists='replace', index=False)
    
    # 3. Distribuição de valores
    amount_dist = df.groupby('amount_category').agg({
        'Class': ['count', 'sum'],
        'Amount': 'sum'
    }).reset_index()
    amount_dist.to_sql('amount_distribution', conn, if_exists='replace', index=False)
    
    # 4. Features para ML
    ml_features = df[['Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 
                      'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16',
                      'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23', 'V24',
                      'V25', 'V26', 'V27', 'V28', 'Amount', 'Class']]
    ml_features.to_sql('ml_dataset', conn, if_exists='replace', index=False)
    
    conn.close()
```

**Resultado esperado**: Database SQLite com tabelas analíticas

---

### 🤖 4.2 Gold - Dataset para Machine Learning
**Objetivo**: Preparar dados para treinamento de modelo

**Tarefas**:
- [ ] Criar `scripts/gold_ml_prep.py`:
  - Separar features (X) e target (y)
  - Fazer split treino/teste (80/20)
  - Balancear classes (SMOTE ou undersampling)
  - Salvar datasets separados:
    - `gold/ml/X_train.parquet`
    - `gold/ml/X_test.parquet`
    - `gold/ml/y_train.parquet`
    - `gold/ml/y_test.parquet`

**Código base**:
```python
from sklearn.model_selection import train_test_split

def prepare_ml_dataset(df):
    """Prepara dataset para ML"""
    # Separar features e target
    feature_cols = [c for c in df.columns if c not in ['Class', 'is_fraud']]
    X = df[feature_cols]
    y = df['Class']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Salvar
    X_train.to_parquet('gold/ml/X_train.parquet', index=False)
    X_test.to_parquet('gold/ml/X_test.parquet', index=False)
    y_train.to_frame().to_parquet('gold/ml/y_train.parquet', index=False)
    y_test.to_frame().to_parquet('gold/ml/y_test.parquet', index=False)
```

**Resultado esperado**: Datasets prontos para treinar modelos

---

### ✅ 4.3 Validação da Camada Gold
**Tarefas**:
- [ ] Criar `scripts/validate_gold.py`:
  - Verificar criação de todas as tabelas SQLite
  - Validar contagens e somas
  - Verificar integridade referencial
  - Gerar relatório final do pipeline

**Resultado esperado**: Confirmação de pipeline completo

---

## 🔄 Fase 5: Orquestração com Airflow (3-4 dias)

### ⚙️ 5.1 Configurar Airflow
**Tarefas**:
- [ ] Atualizar `docker-compose.yml` para incluir Airflow:
  ```yaml
  airflow:
    image: apache/airflow:2.8.0
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./scripts:/opt/airflow/scripts
      - ./data:/opt/airflow/data
    depends_on:
      - postgres
  
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
  ```

- [ ] Inicializar Airflow:
  ```bash
  docker exec -it airflow-container airflow db init
  docker exec -it airflow-container airflow users create \
      --username admin \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com \
      --password admin
  ```

**Resultado esperado**: Airflow rodando e acessível em `http://localhost:8080`

---

### 📅 5.2 Criar DAGs
**Objetivo**: Orquestrar todo o pipeline ETL

**Tarefas**:
- [ ] Criar `airflow/dags/fraud_detection_pipeline.py`:
  - Task 1: Validar ambiente
  - Task 2: Extrair MySQL → Bronze
  - Task 3: Extrair MongoDB → Bronze
  - Task 4: Validar Bronze
  - Task 5: Processar Silver (limpeza)
  - Task 6: Processar Silver (features)
  - Task 7: Validar Silver
  - Task 8: Processar Gold (agregações)
  - Task 9: Processar Gold (ML prep)
  - Task 10: Validar Gold
  - Task 11: Notificação de sucesso/falha

**Código da DAG**:
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'fraud-detection-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 8),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'fraud_detection_etl',
    default_args=default_args,
    description='Pipeline ETL completo para detecção de fraude',
    schedule_interval='@daily',
    catchup=False,
)

# Task: Validar ambiente
validate_env = BashOperator(
    task_id='validate_environment',
    bash_command='python /opt/airflow/scripts/validate_env.py',
    dag=dag,
)

# Task: Bronze MySQL
bronze_mysql = BashOperator(
    task_id='extract_mysql_to_bronze',
    bash_command='python /opt/airflow/scripts/bronze_mysql.py',
    dag=dag,
)

# Task: Bronze MongoDB
bronze_mongo = BashOperator(
    task_id='extract_mongo_to_bronze',
    bash_command='python /opt/airflow/scripts/bronze_mongo.py',
    dag=dag,
)

# Task: Validar Bronze
validate_bronze = BashOperator(
    task_id='validate_bronze',
    bash_command='python /opt/airflow/scripts/validate_bronze.py',
    dag=dag,
)

# Task: Silver Clean
silver_clean = BashOperator(
    task_id='process_silver_clean',
    bash_command='python /opt/airflow/scripts/silver_clean.py',
    dag=dag,
)

# Task: Silver Features
silver_features = BashOperator(
    task_id='process_silver_features',
    bash_command='python /opt/airflow/scripts/silver_features.py',
    dag=dag,
)

# Task: Validar Silver
validate_silver = BashOperator(
    task_id='validate_silver',
    bash_command='python /opt/airflow/scripts/validate_silver.py',
    dag=dag,
)

# Task: Gold Aggregations
gold_agg = BashOperator(
    task_id='process_gold_aggregations',
    bash_command='python /opt/airflow/scripts/gold_aggregations.py',
    dag=dag,
)

# Task: Gold ML Prep
gold_ml = BashOperator(
    task_id='process_gold_ml_prep',
    bash_command='python /opt/airflow/scripts/gold_ml_prep.py',
    dag=dag,
)

# Task: Validar Gold
validate_gold = BashOperator(
    task_id='validate_gold',
    bash_command='python /opt/airflow/scripts/validate_gold.py',
    dag=dag,
)

# Definir dependências
validate_env >> [bronze_mysql, bronze_mongo]
[bronze_mysql, bronze_mongo] >> validate_bronze
validate_bronze >> silver_clean
silver_clean >> silver_features
silver_features >> validate_silver
validate_silver >> [gold_agg, gold_ml]
[gold_agg, gold_ml] >> validate_gold
```

**Resultado esperado**: DAG funcional e testada

---

### 📊 5.3 Monitoramento e Alertas
**Tarefas**:
- [ ] Configurar logs estruturados
- [ ] Criar alertas de falha (email ou Slack)
- [ ] Adicionar métricas de performance
- [ ] Criar dashboard de monitoramento (opcional)

**Resultado esperado**: Pipeline monitorado e com alertas

---

## 🧪 Fase 6: Testes e Qualidade (2 dias)

### ✅ 6.1 Testes Automatizados
**Tarefas**:
- [ ] Criar `tests/test_bronze.py`:
  - Testar extração MySQL
  - Testar extração MongoDB
  - Validar formato JSON Lines

- [ ] Criar `tests/test_silver.py`:
  - Testar limpeza de dados
  - Testar criação de features
  - Validar tipos de dados

- [ ] Criar `tests/test_gold.py`:
  - Testar criação de tabelas SQLite
  - Validar agregações
  - Testar dataset ML

- [ ] Criar `tests/test_utils.py`:
  - Testar conexões
  - Testar funções auxiliares

**Executar testes**:
```bash
pytest tests/ -v --cov=scripts
```

**Resultado esperado**: Cobertura de testes > 80%

---

### 📝 6.2 Documentação
**Tarefas**:
- [ ] Atualizar `README.md` com:
  - Instruções de instalação completas
  - Como executar o pipeline
  - Arquitetura do sistema
  - Exemplos de uso

- [ ] Criar `docs/ARCHITECTURE.md`:
  - Diagrama da arquitetura Medalhão
  - Fluxo de dados
  - Tecnologias utilizadas

- [ ] Criar `docs/API.md`:
  - Documentação de cada script
  - Parâmetros e retornos
  - Exemplos de uso

- [ ] Adicionar docstrings em todos os scripts

**Resultado esperado**: Documentação completa e clara

---

## 🚀 Fase 7: Deploy e Entrega (1-2 dias)

### 📦 7.1 Preparar para Produção
**Tarefas**:
- [ ] Criar script de deploy (`deploy.sh`):
  ```bash
  #!/bin/bash
  echo "Deploying Fraud Detection Pipeline..."
  docker-compose down
  docker-compose build
  docker-compose up -d
  docker exec airflow-container airflow dags trigger fraud_detection_etl
  ```

- [ ] Configurar variáveis de ambiente para produção
- [ ] Testar pipeline completo end-to-end
- [ ] Criar backup dos dados importantes

**Resultado esperado**: Pipeline pronto para produção

---

### 📊 7.2 Apresentação Final
**Tarefas**:
- [ ] Criar apresentação (slides) com:
  - Contexto do projeto
  - Arquitetura implementada
  - Desafios enfrentados e soluções
  - Resultados obtidos
  - Próximos passos

- [ ] Preparar demo ao vivo:
  - Executar pipeline completo
  - Mostrar dados em cada camada
  - Exibir Airflow UI
  - Consultar tabelas Gold no SQLite

- [ ] Criar vídeo de demonstração (5-10 min)

**Resultado esperado**: Apresentação profissional

---

## 📅 Cronograma Resumido

| Fase | Duração | Tarefas principais |
|------|---------|-------------------|
| **Fase 1** | 3-4 dias | Padronizar configs, refatorar scripts, estrutura de pastas |
| **Fase 2** | 2-3 dias | Implementar Bronze (MySQL + MongoDB) + validação |
| **Fase 3** | 3-4 dias | Implementar Silver (limpeza + features) + validação |
| **Fase 4** | 2-3 dias | Implementar Gold (agregações + ML prep) + validação |
| **Fase 5** | 3-4 dias | Configurar Airflow + criar DAGs + monitoramento |
| **Fase 6** | 2 dias | Testes automatizados + documentação |
| **Fase 7** | 1-2 dias | Deploy + apresentação |
| **TOTAL** | **16-23 dias** | **~3 semanas** |

---

## 🎯 Critérios de Sucesso

### Técnicos
- ✅ Pipeline ETL completo funcionando
- ✅ Arquitetura Medalhão implementada (Bronze/Silver/Gold)
- ✅ Dados validados em cada camada
- ✅ Orquestração com Airflow funcional
- ✅ Testes automatizados (cobertura > 80%)
- ✅ Documentação completa

### Funcionais
- ✅ Dados de fraude prontos para análise
- ✅ Dataset preparado para Machine Learning
- ✅ Agregações e métricas acessíveis
- ✅ Pipeline reproduzível e escalável

### Apresentação
- ✅ Demo funcionando ao vivo
- ✅ Apresentação clara e objetiva
- ✅ Documentação profissional

---

## 🚨 Riscos e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Problemas de rede com MongoDB Atlas na VM | Alto | Alta | Usar MongoDB local ou executar no PC |
| Dados muito grandes para processar | Médio | Baixa | Implementar processamento em batches |
| Incompatibilidade de versões de bibliotecas | Médio | Média | Fixar versões no requirements.txt |
| Airflow não subir corretamente | Alto | Média | Testar em ambiente isolado primeiro |
| Falta de tempo | Alto | Média | Priorizar MVP (fases 1-4), Airflow é opcional |

---

## 📌 Priorização

### Essencial (MVP)
1. Fase 1: Consolidação da Base
2. Fase 2: Camada Bronze
3. Fase 3: Camada Silver
4. Fase 4: Camada Gold
5. Documentação básica

### Desejável
1. Fase 5: Airflow completo
2. Fase 6: Testes automatizados
3. Dashboard de visualização

### Opcional
1. Machine Learning avançado
2. API REST para consumo
3. CI/CD pipeline

---

## 📞 Próximos Passos Imediatos

1. **Hoje**: Atualizar `.env` e `requirements.txt`
2. **Amanhã**: Refatorar scripts existentes com `.env`
3. **Esta semana**: Finalizar camada Bronze
4. **Próxima semana**: Implementar Silver e Gold
5. **Semana seguinte**: Airflow e apresentação

---

**Última atualização**: 8 de dezembro de 2025  
**Responsável**: Leonardo de Oliveira  
**Status**: 🟡 Em Progresso
