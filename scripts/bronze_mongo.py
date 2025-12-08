"""
Extrai dados do MongoDB para a camada Bronze
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
    get_mongo_connection,
    ensure_dir,
    get_timestamp,
    format_size
)

# Configurar logger
logger = setup_logger('bronze_mongo')


def extract_mongo_to_bronze():
    """
    Extrai todos os dados do MongoDB e salva na camada Bronze
    
    Returns:
        dict: Estatísticas da extração
    """
    logger.info("=" * 80)
    logger.info("INICIANDO EXTRAÇÃO - MongoDB → Bronze")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Obter configurações
        database_name = os.getenv('MONGO_DATABASE', 'frauddb')
        collection_name = os.getenv('MONGO_COLLECTION', 'transactions')
        bronze_dir = os.getenv('BRONZE_DIR', './bronze')
        output_path = os.path.join(bronze_dir, 'mongo', 'credit_card2.txt')
        
        # Garantir que o diretório existe
        ensure_dir(os.path.dirname(output_path))
        
        # Conectar ao MongoDB
        logger.info(f"Conectando ao MongoDB...")
        client = get_mongo_connection()
        db = client[database_name]
        collection = db[collection_name]
        
        # Contar documentos
        total_docs = collection.count_documents({})
        logger.info(f"Total de documentos na collection '{collection_name}': {total_docs:,}")
        
        # Extrair e salvar dados
        logger.info(f"Salvando dados em: {output_path}")
        count = 0
        batch_size = 1000
        
        with open(output_path, 'w', encoding='utf-8') as f:
            cursor = collection.find({}).batch_size(batch_size)
            
            for doc in cursor:
                # Converter ObjectId para string
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                
                # Adicionar metadata
                doc['_extracted_at'] = get_timestamp()
                doc['_source'] = 'mongodb'
                doc['_collection'] = collection_name
                
                # Escrever linha
                f.write(json.dumps(doc, default=str) + '\n')
                count += 1
                
                # Log de progresso a cada 10000 documentos
                if count % 10000 == 0:
                    logger.info(f"Processados {count:,} documentos...")
        
        # Fechar conexão
        client.close()
        
        # Estatísticas finais
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        file_size = os.path.getsize(output_path)
        
        stats = {
            'documents_extracted': count,
            'output_file': output_path,
            'file_size': format_size(file_size),
            'duration_seconds': round(duration, 2),
            'docs_per_second': round(count / duration, 2) if duration > 0 else 0
        }
        
        logger.info("=" * 80)
        logger.info("EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info(f"Total de documentos: {count:,}")
        logger.info(f"Arquivo gerado: {output_path}")
        logger.info(f"Tamanho: {stats['file_size']}")
        logger.info(f"Tempo: {duration:.2f}s ({stats['docs_per_second']:.2f} docs/s)")
        logger.info("=" * 80)
        
        return stats
        
    except Exception as e:
        logger.error(f"ERRO na extração MongoDB → Bronze: {e}")
        raise


if __name__ == "__main__":
    try:
        stats = extract_mongo_to_bronze()
        print(f"\n✅ Sucesso! {stats['documents_extracted']:,} documentos extraídos")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
