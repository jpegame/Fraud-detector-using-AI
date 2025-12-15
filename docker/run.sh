#!/bin/sh
set -e

IMPORT_MYSQL=true
IMPORT_MONGO=true
RUN_PIPELINE=true

# Leitura de argumentos
for arg in "$@"; do
  case $arg in
    --no-mysql)
      IMPORT_MYSQL=false
      ;;
    --no-mongo)
      IMPORT_MONGO=false
      ;;
    --no-pipeline)
      RUN_PIPELINE=false
      ;;
    *)
      echo "❌ Opção desconhecida: $arg"
      exit 1
      ;;
  esac
done

echo "▶ Iniciando execução..."

if [ "$IMPORT_MYSQL" = true ]; then
  echo "▶ Importando dados no MySQL..."
  docker compose run --rm runner scripts/import_csv.py
else
  echo "⏭ Pulando import do MySQL"
fi

if [ "$IMPORT_MONGO" = true ]; then
  echo "▶ Importando dados no MongoDB..."
  docker compose run --rm runner scripts/import_csv_mongo.py
else
  echo "⏭ Pulando import do MongoDB"
fi

if [ "$RUN_PIPELINE" = true ]; then
  echo "▶ Executando pipeline..."
  docker compose run --rm runner scripts/run_pipeline.py
else
  echo "⏭ Pulando execução do pipeline"
fi

echo "✅ Execução finalizada com sucesso!"
