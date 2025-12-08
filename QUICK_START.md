# 🚀 Guia Rápido de Execução

## Para executar na VM

### 1. Configurar ambiente
```bash
# Criar .env a partir do exemplo
cp .env.example .env

# Editar .env com suas credenciais
nano .env
```

### 2. Ativar venv e instalar dependências
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Executar pipeline completo
```bash
python scripts/run_pipeline.py
```

## Execução passo a passo

```bash
# 1. Bronze (Extração)
python scripts/bronze_mysql.py
python scripts/bronze_mongo.py
python scripts/validate_bronze.py

# 2. Silver (Transformação)
python scripts/silver_clean.py
python scripts/silver_features.py

# 3. Gold (Agregação)
python scripts/gold_aggregations.py
python scripts/gold_ml_prep.py
```

## Verificar resultados

```bash
# Ver logs
ls -lh logs/

# Ver arquivos gerados
ls -lh bronze/mysql/
ls -lh silver/cleaned/
ls -lh gold/analytics/

# Consultar SQLite
sqlite3 gold/analytics/fraud_analytics.db "SELECT * FROM fraud_statistics;"
```

## Docker (MySQL)

```bash
# Subir MySQL
cd docker
docker compose up -d mysql

# Verificar
docker ps
docker logs mysql-container
```

## Troubleshooting

**Erro de conexão MySQL:**
- Verificar se container está rodando: `docker ps`
- Verificar .env: `cat .env | grep MYSQL`

**Erro de conexão MongoDB:**
- Executar no PC local se VM tiver restrições de rede
- Usar MongoDB local se necessário

**Erro de dependências:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
