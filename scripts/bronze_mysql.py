"""
Extrai dados do MySQL para a camada Bronze
Salva em formato JSON Lines (um JSON por linha)
"""

import json
import os
import sys
from datetime import datetime

# Adicionar diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    setup_logger,
    get_mysql_connection,
    ensure_dir,
    get_timestamp,
    format_size
)

# Configurar logger
logger = setup_logger('bronze_mysql')


def extract_mysql_to_bronze():
    """
    Extrai todos os dados do MySQL e salva na camada Bronze
    
    Returns:
        dict: Estatísticas da extração
    """
    logger.info("=" * 80)
    logger.info("INICIANDO EXTRAÇÃO - MySQL → Bronze")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Obter configurações
        table = os.getenv('MYSQL_TABLE', 'transactions')
        bronze_dir = os.getenv('BRONZE_DIR', './bronze')
        output_path = os.path.join(bronze_dir, 'mysql', 'credit_card1.txt')
        
        # Garantir que o diretório existe
        ensure_dir(os.path.dirname(output_path))
        
        # Conectar ao MySQL
        logger.info(f"Conectando ao MySQL...")
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Executar query
        logger.info(f"Executando query: SELECT * FROM {table}")
        cursor.execute(f"SELECT * FROM {table}")
        
        # Extrair e salvar dados
        logger.info(f"Salvando dados em: {output_path}")
        count = 0
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for row in cursor:
                # Adicionar metadata
                row['_extracted_at'] = get_timestamp()
                row['_source'] = 'mysql'
                row['_table'] = table
                
                # Escrever linha
                f.write(json.dumps(row, default=str) + '\n')
                count += 1
                
                # Log de progresso a cada 10000 linhas
                if count % 10000 == 0:
                    logger.info(f"Processadas {count:,} linhas...")
        
        # Fechar conexões
        cursor.close()
        conn.close()
        
        # Estatísticas finais
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        file_size = os.path.getsize(output_path)
        
        stats = {
            'rows_extracted': count,
            'output_file': output_path,
            'file_size': format_size(file_size),
            'duration_seconds': round(duration, 2),
            'rows_per_second': round(count / duration, 2) if duration > 0 else 0
        }
        
        logger.info("=" * 80)
        logger.info("EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info(f"Total de linhas: {count:,}")
        logger.info(f"Arquivo gerado: {output_path}")
        logger.info(f"Tamanho: {stats['file_size']}")
        logger.info(f"Tempo: {duration:.2f}s ({stats['rows_per_second']:.2f} linhas/s)")
        logger.info("=" * 80)
        
        return stats
        
    except Exception as e:
        logger.error(f"ERRO na extração MySQL → Bronze: {e}")
        raise


if __name__ == "__main__":
    try:
        stats = extract_mysql_to_bronze()
        print(f"\n✅ Sucesso! {stats['rows_extracted']:,} linhas extraídas")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
