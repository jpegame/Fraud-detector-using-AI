# Contexto do Projeto - Fraud Detector Using AI

## Visão Geral
Plataforma de engenharia de dados para detecção de fraude em cartão de crédito, implementando arquitetura Medalhão (Bronze/Silver/Gold) com orquestração via Apache Airflow.

## Ambiente de Desenvolvimento

### Infraestrutura Principal
- **VM Ubuntu Server** (fornecida pelo professor)
  - Docker instalado
  - Python com venv
  - Apache Airflow
  
### Banco de Dados
- **MySQL 8** (Docker container)
  - Database: `creditdb`
  - Porta: 3306
  - Dados: `credit-card1.csv`
  
- **MongoDB Atlas** (nuvem)
  - Conexão via PC local (restrições de rede na VM)
  - Dados: `credit-card2.json`

## Estrutura do Projeto

```
Fraud-detector-using-AI/
├── data/                    # Dados de origem
│   ├── credit-card1.csv    # → MySQL
│   └── credit-card2.csv    # → MongoDB
│
├── scripts/                 # Scripts Python de ETL
│   ├── import_csv.py       # Importa CSV para MySQL
│   ├── csv_to_json.py      # Converte CSV2 → JSON
│   ├── import_json.py      # Importa JSON para MongoDB
│   ├── bronze_mysql.py     # Camada Bronze
│   ├── check_one.py        # Validação
│   ├── count_docs.py       # Contagem de documentos
│   └── teste_mongo_connection.py
│
├── bronze/                  # Camada Bronze (dados brutos)
│   └── *.txt               # JSON por linha
│
├── silver/                  # Camada Silver (dados tratados)
│   └── *.parquet           # DataFrames com pandas
│
├── gold/                    # Camada Gold (dados agregados)
│   └── *.db                # Tabelas SQLite
│
├── docker/                  # Configurações Docker
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── example.env
│
├── requirements.txt         # Dependências Python
└── readme.md
```

## Fonte de Dados

### Dataset Original
- **Origem**: Kaggle - Credit Card Fraud Detection
- **Arquivo**: `credit-card.csv`
- **Particionamento**:
  - `credit-card1.csv` → MySQL (Docker na VM)
  - `credit-card2.csv` → MongoDB Atlas (via PC local)

### Campos do Dataset
- `Time`, `V1-V28` (features PCA), `Amount`, `Class` (0=normal, 1=fraude)

## Arquitetura Medalhão

### Camada Bronze 🥉
- **Objetivo**: Armazenar dados brutos sem transformação
- **Formato**: JSON Lines (.txt, um JSON por linha)
- **Fonte**: MySQL + MongoDB
- **Status**: Estrutura criada, implementação em andamento

### Camada Silver 🥈
- **Objetivo**: Dados limpos e padronizados
- **Formato**: Parquet/DataFrames pandas
- **Transformações**:
  - Normalização de valores
  - Tratamento de missing values
  - Tipagem correta de dados
- **Status**: Estrutura criada, aguardando implementação

### Camada Gold 🥇
- **Objetivo**: Dados agregados e prontos para análise
- **Formato**: Tabelas SQLite
- **Agregações**:
  - Estatísticas de fraude
  - Análises temporais
  - Features para ML
- **Status**: Estrutura criada, aguardando implementação

## Scripts Implementados

### 1. `import_csv.py` / `import_mysql.py`
- Lê `credit-card1.csv`
- Conecta ao MySQL via `.env`
- Cria tabela com `CREATE TABLE IF NOT EXISTS`
- Insere dados linha a linha
- **Status**: ✅ Funcionando

### 2. `csv_to_json.py`
- Lê `credit-card2.csv` com `csv.DictReader`
- Converte para lista de objetos JSON
- Salva como `credit-card2.json`
- **Status**: ✅ Testado no PC local

### 3. `import_json.py`
- Conecta ao MongoDB Atlas
- Faz `insert_many` dos documentos
- Valida com `find_one` e `count_documents`
- **Status**: ✅ Funcionando no PC local

### 4. `bronze_mysql.py`
- Extrai dados do MySQL
- Gera arquivos Bronze (.txt JSON Lines)
- **Status**: 🔄 Em desenvolvimento

## Configuração com .env

Centralização de configurações em arquivo `.env`:

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DATABASE=creditdb

# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DATABASE=frauddb
MONGO_COLLECTION=transactions

# Paths
DATA_DIR=/caminho/para/data
BRONZE_DIR=/caminho/para/bronze
SILVER_DIR=/caminho/para/silver
GOLD_DIR=/caminho/para/gold
```

## Aprendizados e Desafios

### ✅ Sucessos
1. **Ambiente Python**: venv configurado com todas as dependências
2. **MySQL Docker**: Container rodando corretamente com volumes persistentes
3. **Scripts ETL**: Lógica de importação CSV→MySQL e CSV→JSON→MongoDB funcionando
4. **Estrutura Medalhão**: Pastas e conceitos bem definidos

### ⚠️ Desafios Encontrados

#### 1. MySQL sem configuração inicial
**Problema**: Container criado sem `MYSQL_ROOT_PASSWORD` e `MYSQL_DATABASE`  
**Solução**: Remover container e recriar com variáveis de ambiente corretas:
```bash
docker run -d \
  --name mysql-fraud \
  -e MYSQL_ROOT_PASSWORD=senha123 \
  -e MYSQL_DATABASE=creditdb \
  -p 3306:3306 \
  mysql:8
```

#### 2. MongoDB Atlas bloqueado na VM
**Problema**: Conexão com `*.mongodb.net` falha com erros TLS/connection closed  
**Causa**: Restrições de firewall/rede da infraestrutura da VM  
**Solução**: Executar a parte MongoDB no PC local onde a conexão funciona  
**Aprendizado**: O código está correto, o problema é infraestrutura, não lógica

#### 3. Organização de código
**Solução adotada**: Separar scripts por responsabilidade única
- `import_mysql.py` → apenas importação MySQL
- `csv_to_json.py` → apenas conversão
- `import_json.py` → apenas importação MongoDB
- `bronze_mysql.py` → apenas geração Bronze

## Tecnologias Utilizadas

### Python
- `pandas` - manipulação de dados
- `pymongo` - conexão MongoDB
- `mysql-connector-python` - conexão MySQL
- `python-dotenv` - gerenciamento de variáveis de ambiente
- `csv` - leitura de CSV
- `json` - manipulação de JSON

### Infraestrutura
- **Docker** - containerização (MySQL)
- **Apache Airflow** - orquestração de pipelines
- **MySQL 8** - banco relacional
- **MongoDB Atlas** - banco NoSQL
- **SQLite** - camada Gold

## Próximos Passos

### Curto Prazo
1. [ ] Finalizar script `bronze_mysql.py`
2. [ ] Criar script `bronze_mongo.py`
3. [ ] Implementar camada Silver com pandas
4. [ ] Implementar camada Gold com SQLite
5. [ ] Criar validações de qualidade de dados

### Médio Prazo
1. [ ] Criar DAGs do Airflow
2. [ ] Implementar testes automatizados
3. [ ] Configurar logging estruturado
4. [ ] Documentar APIs dos scripts

### Longo Prazo
1. [ ] Implementar modelo de ML para detecção de fraude
2. [ ] Criar dashboard de visualização
3. [ ] Automatizar deploy com CI/CD
4. [ ] Implementar monitoramento e alertas

## Comandos Úteis

### Ativar ambiente virtual
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Rodar scripts
```bash
python scripts/import_mysql.py
python scripts/csv_to_json.py
python scripts/import_json.py
```

### Docker MySQL
```bash
# Iniciar container
docker start mysql-fraud

# Parar container
docker stop mysql-fraud

# Acessar MySQL
docker exec -it mysql-fraud mysql -uroot -p
```

### Verificar MongoDB
```bash
python scripts/count_docs.py
python scripts/check_one.py
```

## Contatos e Referências

- **Professor**: [Nome do professor]
- **Equipe**: Leonardo de Oliveira, [outros membros]
- **Dataset**: [Kaggle Credit Card Fraud](https://www.kaggle.com/mlg-ulb/creditcardfraud)
- **Repositório**: jpegame/Fraud-detector-using-AI
- **Branch atual**: feature/etl-pipeline

---

**Última atualização**: 8 de dezembro de 2025
