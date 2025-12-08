"""
Camada Silver - Limpeza e normalização de dados
Unifica dados do MySQL e MongoDB, remove duplicatas e trata valores
"""

import json
import os
import sys
import pandas as pd
from datetime import datetime

# Adicionar diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, ensure_dir, validate_file_exists, format_size

# Configurar logger
logger = setup_logger('silver_clean')


def load_bronze_to_dataframe(filepath):
    """
    Carrega arquivo Bronze (JSON Lines) para DataFrame
    
    Args:
        filepath: Caminho do arquivo Bronze
        
    Returns:
        DataFrame com os dados
    """
    logger.info(f"Carregando arquivo Bronze: {filepath}")
    
    validate_file_exists(filepath)
    
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    df = pd.DataFrame(data)
    logger.info(f"  Carregadas {len(df):,} linhas com {len(df.columns)} colunas")
    
    return df


def clean_transactions(df, source_name):
    """
    Limpa e padroniza dados de transações
    
    Args:
        df: DataFrame com dados brutos
        source_name: Nome da fonte (para logging)
        
    Returns:
        DataFrame limpo
    """
    logger.info(f"Limpando dados de {source_name}...")
    
    initial_count = len(df)
    
    # Remover colunas de metadata
    metadata_cols = [c for c in df.columns if c.startswith('_')]
    if metadata_cols:
        df = df.drop(columns=metadata_cols)
        logger.info(f"  Removidas {len(metadata_cols)} colunas de metadata")
    
    # Converter tipos de dados
    logger.info("  Convertendo tipos de dados...")
    
    # Time e Amount são campos essenciais
    if 'Time' in df.columns:
        df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    
    if 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Class (0=normal, 1=fraude)
    if 'Class' in df.columns:
        df['Class'] = pd.to_numeric(df['Class'], errors='coerce').astype('Int64')
    
    # Features V1-V28 (resultado de PCA)
    v_cols = [f'V{i}' for i in range(1, 29) if f'V{i}' in df.columns]
    for col in v_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Tratar valores nulos
    logger.info("  Tratando valores nulos...")
    
    # Class não pode ser nulo - remover linhas sem Class
    if 'Class' in df.columns:
        null_class = df['Class'].isna().sum()
        if null_class > 0:
            logger.warning(f"  Removendo {null_class} linhas com Class nulo")
            df = df.dropna(subset=['Class'])
    
    # Amount nulo = 0
    if 'Amount' in df.columns:
        null_amount = df['Amount'].isna().sum()
        if null_amount > 0:
            logger.info(f"  Preenchendo {null_amount} valores nulos em Amount com 0")
            df['Amount'] = df['Amount'].fillna(0)
    
    # Remover duplicatas
    logger.info("  Removendo duplicatas...")
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        logger.warning(f"  Encontradas {duplicates} linhas duplicadas")
        df = df.drop_duplicates()
    
    final_count = len(df)
    removed = initial_count - final_count
    
    logger.info(f"  Limpeza concluída:")
    logger.info(f"    Linhas iniciais: {initial_count:,}")
    logger.info(f"    Linhas finais: {final_count:,}")
    logger.info(f"    Linhas removidas: {removed:,}")
    
    return df


def process_silver_clean():
    """
    Processa a camada Silver - limpeza de dados
    
    Returns:
        dict: Estatísticas do processamento
    """
    logger.info("=" * 80)
    logger.info("PROCESSAMENTO SILVER - Limpeza de Dados")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Obter configurações
        bronze_dir = os.getenv('BRONZE_DIR', './bronze')
        silver_dir = os.getenv('SILVER_DIR', './silver')
        
        mysql_file = os.path.join(bronze_dir, 'mysql', 'credit_card1.txt')
        mongo_file = os.path.join(bronze_dir, 'mongo', 'credit_card2.txt')
        output_file = os.path.join(silver_dir, 'cleaned', 'transactions.parquet')
        
        ensure_dir(os.path.dirname(output_file))
        
        # Carregar dados do MySQL
        df_mysql = load_bronze_to_dataframe(mysql_file)
        df_mysql_clean = clean_transactions(df_mysql, 'MySQL')
        
        # Carregar dados do MongoDB
        df_mongo = load_bronze_to_dataframe(mongo_file)
        df_mongo_clean = clean_transactions(df_mongo, 'MongoDB')
        
        # Combinar datasets
        logger.info("Combinando datasets MySQL + MongoDB...")
        df_combined = pd.concat([df_mysql_clean, df_mongo_clean], ignore_index=True)
        
        # Remover duplicatas entre as fontes
        logger.info("Removendo duplicatas entre fontes...")
        duplicates_inter = df_combined.duplicated().sum()
        if duplicates_inter > 0:
            logger.warning(f"  Encontradas {duplicates_inter} duplicatas entre MySQL e MongoDB")
            df_combined = df_combined.drop_duplicates()
        
        # Resetar índice
        df_combined = df_combined.reset_index(drop=True)
        
        # Salvar em Parquet
        logger.info(f"Salvando dados limpos em: {output_file}")
        df_combined.to_parquet(output_file, index=False, compression='snappy')
        
        # Estatísticas finais
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        file_size = os.path.getsize(output_file)
        
        # Estatísticas de qualidade
        total_rows = len(df_combined)
        fraud_count = df_combined['Class'].sum() if 'Class' in df_combined.columns else 0
        fraud_rate = (fraud_count / total_rows * 100) if total_rows > 0 else 0
        
        stats = {
            'mysql_rows': len(df_mysql_clean),
            'mongo_rows': len(df_mongo_clean),
            'combined_rows': total_rows,
            'fraud_transactions': int(fraud_count),
            'fraud_rate_pct': round(fraud_rate, 4),
            'columns': len(df_combined.columns),
            'output_file': output_file,
            'file_size': format_size(file_size),
            'duration_seconds': round(duration, 2)
        }
        
        logger.info("=" * 80)
        logger.info("LIMPEZA CONCLUÍDA COM SUCESSO!")
        logger.info(f"MySQL: {stats['mysql_rows']:,} linhas")
        logger.info(f"MongoDB: {stats['mongo_rows']:,} linhas")
        logger.info(f"Total combinado: {stats['combined_rows']:,} linhas")
        logger.info(f"Colunas: {stats['columns']}")
        logger.info(f"Transações fraudulentas: {stats['fraud_transactions']:,} ({stats['fraud_rate_pct']}%)")
        logger.info(f"Arquivo: {output_file}")
        logger.info(f"Tamanho: {stats['file_size']}")
        logger.info(f"Tempo: {duration:.2f}s")
        logger.info("=" * 80)
        
        return stats
        
    except Exception as e:
        logger.error(f"ERRO no processamento Silver Clean: {e}")
        raise


if __name__ == "__main__":
    try:
        stats = process_silver_clean()
        print(f"\n✅ Sucesso! {stats['combined_rows']:,} linhas processadas")
        print(f"   Fraudes: {stats['fraud_transactions']:,} ({stats['fraud_rate_pct']}%)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
