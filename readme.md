# 🔍 Fraud Detector - Pipeline ETL com Arquitetura Medalhão

Sistema de detecção de fraudes em cartões de crédito utilizando **Arquitetura Medalhão** (Bronze/Silver/Gold) com pipeline ETL completo.

## 📋 Sobre o Projeto

Este projeto implementa um pipeline de engenharia de dados para processar transações de cartão de crédito e identificar padrões de fraude, utilizando:

- **Arquitetura Medalhão**: Bronze → Silver → Gold
- **Fontes de dados múltiplas**: MySQL + MongoDB
- **Feature Engineering**: Criação de features derivadas para análise
- **Machine Learning**: Dataset preparado para treinamento de modelos
- **Analytics**: Agregações e métricas em SQLite

### 🎯 Dataset

- **Origem**: Kaggle - Credit Card Fraud Detection
- **Registros**: ~284.807 transações
- **Features**: 30 (Time, V1-V28 PCA, Amount, Class)
- **Particionamento**: 
  - `credit-card1.csv` → MySQL
  - `credit-card2.csv` → MongoDB

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FONTES DE DADOS                          │
├─────────────────────────────────────────────────────────────────┤
│  MySQL (Docker)              MongoDB Atlas                      │
│  credit-card1.csv            credit-card2.csv                   │
└──────────────┬────────────────────────┬─────────────────────────┘
               │                        │
               ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      🥉 CAMADA BRONZE                            │
│                    (Dados Brutos - JSON Lines)                  │
├─────────────────────────────────────────────────────────────────┤
│  bronze/mysql/credit_card1.txt                                  │
│  bronze/mongo/credit_card2.txt                                  │
│  + Metadata (_extracted_at, _source)                            │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      🥈 CAMADA SILVER                            │
│              (Dados Limpos e com Features)                      │
├─────────────────────────────────────────────────────────────────┤
│  silver/cleaned/transactions.parquet                            │
│  silver/features/transactions_features.parquet                  │
│  + Limpeza, normalização, deduplicação                          │
│  + Features derivadas (temporais, estatísticas, categorias)     │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      🥇 CAMADA GOLD                              │
│           (Dados Analíticos e Prontos para ML)                  │
├─────────────────────────────────────────────────────────────────┤
│  gold/analytics/fraud_analytics.db (SQLite)                     │
│    - fraud_statistics                                           │
│    - hourly_analysis                                            │
│    - amount_category_analysis                                   │
│    - time_period_analysis                                       │
│    - daily_summary                                              │
│                                                                 │
│  gold/ml/ (Dataset ML - Train/Test Split)                       │
│    - X_train.parquet, X_test.parquet                            │
│    - y_train.parquet, y_test.parquet                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1️⃣ Pré-requisitos

- Python 3.8+
- MySQL (Docker ou local)
- MongoDB Atlas (ou MongoDB local)

### 2️⃣ Instalação

```bash
# Clonar repositório
git clone https://github.com/jpegame/Fraud-detector-using-AI.git
cd Fraud-detector-using-AI

# Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 3️⃣ Configuração

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
# (MySQL host, senha, MongoDB URI, etc.)
```

**Exemplo de `.env`:**
```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=creditdb
MYSQL_TABLE=transactions

# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DATABASE=frauddb
MONGO_COLLECTION=transactions

# Paths
DATA_DIR=./data
BRONZE_DIR=./bronze
SILVER_DIR=./silver
GOLD_DIR=./gold
LOGS_DIR=./logs
```

### 4️⃣ Preparar Dados

Certifique-se de ter os arquivos CSV em `data/`:
- `data/credit-card1.csv`
- `data/credit-card2.csv`

### 5️⃣ Executar Pipeline

```bash
# Pipeline completo (Bronze → Silver → Gold)
python scripts/run_pipeline.py

# Executar etapas individuais
python scripts/bronze_mysql.py
python scripts/bronze_mongo.py
python scripts/silver_clean.py
python scripts/silver_features.py
python scripts/gold_aggregations.py
python scripts/gold_ml_prep.py
```

---

## 📂 Estrutura do Projeto

```
Fraud-detector-using-AI/
├── data/                          # Dados de entrada
│   ├── credit-card1.csv          # → MySQL
│   └── credit-card2.csv          # → MongoDB
│
├── scripts/                       # Scripts Python do pipeline
│   ├── utils.py                  # Funções utilitárias
│   ├── bronze_mysql.py           # Extração MySQL → Bronze
│   ├── bronze_mongo.py           # Extração MongoDB → Bronze
│   ├── validate_bronze.py        # Validação Bronze
│   ├── silver_clean.py           # Limpeza e unificação
│   ├── silver_features.py        # Feature engineering
│   ├── gold_aggregations.py      # Agregações SQLite
│   ├── gold_ml_prep.py           # Preparação ML
│   └── run_pipeline.py           # Pipeline completo
│
├── bronze/                        # 🥉 Camada Bronze
│   ├── mysql/credit_card1.txt
│   └── mongo/credit_card2.txt
│
├── silver/                        # 🥈 Camada Silver
│   ├── cleaned/transactions.parquet
│   └── features/transactions_features.parquet
│
├── gold/                          # 🥇 Camada Gold
│   ├── analytics/fraud_analytics.db
│   └── ml/X_train.parquet, X_test.parquet, y_train.parquet, y_test.parquet
│
├── logs/                          # Logs de execução
├── docker/                        # Configurações Docker
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── example.env
│
├── requirements.txt               # Dependências Python
├── .env.example                   # Exemplo de configuração
├── CONTEXTO.md                    # Documentação do contexto
├── PLANO_EXECUCAO.md             # Plano de implementação
└── README.md                      # Este arquivo
```

---

## 🔧 Scripts Disponíveis

### Pipeline Completo
```bash
# Executar todo o pipeline
python scripts/run_pipeline.py

# Pular Bronze (se já executado)
python scripts/run_pipeline.py --skip-bronze

# Pular Silver
python scripts/run_pipeline.py --skip-silver

# Pular Gold
python scripts/run_pipeline.py --skip-gold
```

### Scripts Individuais

**Camada Bronze:**
```bash
python scripts/bronze_mysql.py      # Extrai MySQL → Bronze
python scripts/bronze_mongo.py      # Extrai MongoDB → Bronze
python scripts/validate_bronze.py   # Valida dados Bronze
```

**Camada Silver:**
```bash
python scripts/silver_clean.py      # Limpa e unifica dados
python scripts/silver_features.py   # Cria features derivadas
```

**Camada Gold:**
```bash
python scripts/gold_aggregations.py # Cria tabelas analíticas
python scripts/gold_ml_prep.py      # Prepara dataset ML
```

---

## 📊 Features Criadas

### Temporais
- `hour` - Hora do dia (0-23)
- `day` - Dia desde primeira transação
- `time_period` - Período (madrugada/manhã/tarde/noite)

### Amount
- `amount_normalized` - Amount normalizado (z-score)
- `amount_log` - Log de Amount
- `amount_category` - Categoria (very_low/low/medium/high/very_high)
- `is_high_value` - Flag para valores > 500
- `is_very_low_value` - Flag para valores < 1

### Estatísticas (V1-V28)
- `v_mean` - Média das features PCA
- `v_std` - Desvio padrão
- `v_min` - Valor mínimo
- `v_max` - Valor máximo
- `v_range` - Range (max - min)

### Fraude
- `is_fraud` - Flag booleana (Class == 1)

---

## 🗄️ Tabelas Gold (SQLite)

### `fraud_statistics`
Estatísticas gerais de fraude por classe (0=normal, 1=fraude)

### `hourly_analysis`
Análise de transações e fraudes por hora do dia

### `amount_category_analysis`
Análise por faixa de valor (very_low até very_high)

### `time_period_analysis`
Análise por período (madrugada, manhã, tarde, noite)

### `daily_summary`
Resumo diário de transações, fraudes e valores

**Consultar tabelas:**
```bash
sqlite3 gold/analytics/fraud_analytics.db

# No SQLite
.tables
SELECT * FROM fraud_statistics;
SELECT * FROM hourly_analysis WHERE fraud_rate_pct > 1;
```

---

## 🐳 Docker (Opcional)

### Subir MySQL com Docker

```bash
cd docker
docker compose up -d mysql
```

### Verificar MySQL

```bash
docker exec -it mysql-container mysql -u root -p
```

### Parar containers

```bash
docker compose down
```

---

## 📈 Logs e Monitoramento

Todos os scripts geram logs em `logs/`:
- `logs/bronze_mysql_YYYYMMDD.log`
- `logs/bronze_mongo_YYYYMMDD.log`
- `logs/silver_clean_YYYYMMDD.log`
- etc.

**Visualizar logs:**
```bash
tail -f logs/run_pipeline_$(date +%Y%m%d).log
```

---

## ✅ Validação

O pipeline inclui validações automáticas:
- ✓ Verificação de arquivos de entrada
- ✓ Validação de JSON Lines (Bronze)
- ✓ Contagem de registros por camada
- ✓ Verificação de valores nulos
- ✓ Validação de tipos de dados
- ✓ Estatísticas de qualidade

---

## 🎓 Uso Acadêmico

Este projeto foi desenvolvido para a disciplina de **Big Data** como parte da implementação de um pipeline ETL completo seguindo boas práticas de engenharia de dados.

**Principais conceitos aplicados:**
- Arquitetura Medalhão (Bronze/Silver/Gold)
- ETL com múltiplas fontes de dados
- Feature Engineering
- Data Quality
- Preparação de dados para ML
- Logging e monitoramento

---

## 🤝 Contribuidores

- Leonardo de Oliveira
- [Adicionar outros membros da equipe]

---

## 📝 Licença

Este projeto é para uso acadêmico.

---

## 📞 Suporte

Em caso de dúvidas ou problemas:
1. Verificar logs em `logs/`
2. Revisar configuração do `.env`
3. Consultar `CONTEXTO.md` para detalhes do projeto
4. Consultar `PLANO_EXECUCAO.md` para roadmap completo
