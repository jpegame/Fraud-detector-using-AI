"""
Camada Gold - Agregações e Métricas Analíticas
Cria tabelas SQLite com agregações prontas para análise
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

# Adicionar diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, ensure_dir, validate_file_exists, format_size

# Configurar logger
logger = setup_logger('gold_aggregations')


def create_fraud_statistics(df, conn):
    """
    Cria tabela com estatísticas gerais de fraude
    
    Args:
        df: DataFrame com dados
        conn: Conexão SQLite
    """
    logger.info("Criando tabela: fraud_statistics")
    
    stats = df.groupby('Class').agg({
        'Amount': ['count', 'sum', 'mean', 'median', 'min', 'max', 'std'],
        'Time': ['min', 'max']
    }).reset_index()
    
    # Achatar multi-index columns
    stats.columns = ['_'.join(col).strip('_') for col in stats.columns.values]
    
    # Renomear para ficar mais legível
    stats = stats.rename(columns={
        'Class': 'class',
        'Amount_count': 'transaction_count',
        'Amount_sum': 'total_amount',
        'Amount_mean': 'avg_amount',
        'Amount_median': 'median_amount',
        'Amount_min': 'min_amount',
        'Amount_max': 'max_amount',
        'Amount_std': 'std_amount',
        'Time_min': 'first_transaction_time',
        'Time_max': 'last_transaction_time'
    })
    
    # Calcular taxa de fraude
    total_transactions = stats['transaction_count'].sum()
    stats['fraud_rate_pct'] = (stats['transaction_count'] / total_transactions * 100).round(4)
    
    stats.to_sql('fraud_statistics', conn, if_exists='replace', index=False)
    logger.info(f"  ✓ {len(stats)} linhas inseridas")


def create_hourly_analysis(df, conn):
    """
    Cria tabela com análise por hora do dia
    
    Args:
        df: DataFrame com dados
        conn: Conexão SQLite
    """
    logger.info("Criando tabela: hourly_analysis")
    
    if 'hour' not in df.columns:
        logger.warning("  Coluna 'hour' não encontrada, pulando hourly_analysis")
        return
    
    hourly = df.groupby('hour').agg({
        'Class': ['count', 'sum'],
        'Amount': ['sum', 'mean']
    }).reset_index()
    
    hourly.columns = ['_'.join(col).strip('_') for col in hourly.columns.values]
    hourly = hourly.rename(columns={
        'hour': 'hour',
        'Class_count': 'total_transactions',
        'Class_sum': 'fraud_transactions',
        'Amount_sum': 'total_amount',
        'Amount_mean': 'avg_amount'
    })
    
    hourly['fraud_rate_pct'] = (hourly['fraud_transactions'] / hourly['total_transactions'] * 100).round(4)
    
    hourly.to_sql('hourly_analysis', conn, if_exists='replace', index=False)
    logger.info(f"  ✓ {len(hourly)} linhas inseridas")


def create_amount_category_analysis(df, conn):
    """
    Cria tabela com análise por categoria de valor
    
    Args:
        df: DataFrame com dados
        conn: Conexão SQLite
    """
    logger.info("Criando tabela: amount_category_analysis")
    
    if 'amount_category' not in df.columns:
        logger.warning("  Coluna 'amount_category' não encontrada, pulando amount_category_analysis")
        return
    
    category_stats = df.groupby('amount_category').agg({
        'Class': ['count', 'sum'],
        'Amount': ['sum', 'mean', 'min', 'max']
    }).reset_index()
    
    category_stats.columns = ['_'.join(col).strip('_') for col in category_stats.columns.values]
    category_stats = category_stats.rename(columns={
        'amount_category': 'category',
        'Class_count': 'total_transactions',
        'Class_sum': 'fraud_transactions',
        'Amount_sum': 'total_amount',
        'Amount_mean': 'avg_amount',
        'Amount_min': 'min_amount',
        'Amount_max': 'max_amount'
    })
    
    category_stats['fraud_rate_pct'] = (
        category_stats['fraud_transactions'] / category_stats['total_transactions'] * 100
    ).round(4)
    
    category_stats.to_sql('amount_category_analysis', conn, if_exists='replace', index=False)
    logger.info(f"  ✓ {len(category_stats)} linhas inseridas")


def create_time_period_analysis(df, conn):
    """
    Cria tabela com análise por período do dia
    
    Args:
        df: DataFrame com dados
        conn: Conexão SQLite
    """
    logger.info("Criando tabela: time_period_analysis")
    
    if 'time_period' not in df.columns:
        logger.warning("  Coluna 'time_period' não encontrada, pulando time_period_analysis")
        return
    
    period_stats = df.groupby('time_period').agg({
        'Class': ['count', 'sum'],
        'Amount': ['sum', 'mean']
    }).reset_index()
    
    period_stats.columns = ['_'.join(col).strip('_') for col in period_stats.columns.values]
    period_stats = period_stats.rename(columns={
        'time_period': 'period',
        'Class_count': 'total_transactions',
        'Class_sum': 'fraud_transactions',
        'Amount_sum': 'total_amount',
        'Amount_mean': 'avg_amount'
    })
    
    period_stats['fraud_rate_pct'] = (
        period_stats['fraud_transactions'] / period_stats['total_transactions'] * 100
    ).round(4)
    
    period_stats.to_sql('time_period_analysis', conn, if_exists='replace', index=False)
    logger.info(f"  ✓ {len(period_stats)} linhas inseridas")


def create_daily_summary(df, conn):
    """
    Cria tabela com resumo diário de transações
    
    Args:
        df: DataFrame com dados
        conn: Conexão SQLite
    """
    logger.info("Criando tabela: daily_summary")
    
    if 'day' not in df.columns:
        logger.warning("  Coluna 'day' não encontrada, pulando daily_summary")
        return
    
    daily = df.groupby('day').agg({
        'Class': ['count', 'sum'],
        'Amount': ['sum', 'mean'],
        'is_high_value': 'sum'
    }).reset_index()
    
    daily.columns = ['_'.join(col).strip('_') for col in daily.columns.values]
    daily = daily.rename(columns={
        'day': 'day',
        'Class_count': 'total_transactions',
        'Class_sum': 'fraud_transactions',
        'Amount_sum': 'total_amount',
        'Amount_mean': 'avg_amount',
        'is_high_value_sum': 'high_value_transactions'
    })
    
    daily['fraud_rate_pct'] = (daily['fraud_transactions'] / daily['total_transactions'] * 100).round(4)
    
    daily.to_sql('daily_summary', conn, if_exists='replace', index=False)
    logger.info(f"  ✓ {len(daily)} linhas inseridas")


def process_gold_aggregations():
    """
    Processa a camada Gold - agregações analíticas
    
    Returns:
        dict: Estatísticas do processamento
    """
    logger.info("=" * 80)
    logger.info("PROCESSAMENTO GOLD - Agregações Analíticas")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Obter configurações
        silver_dir = os.getenv('SILVER_DIR', './silver')
        gold_dir = os.getenv('GOLD_DIR', './gold')
        
        input_file = os.path.join(silver_dir, 'features', 'transactions_features.parquet')
        db_file = os.path.join(gold_dir, 'analytics', 'fraud_analytics.db')
        
        ensure_dir(os.path.dirname(db_file))
        
        # Carregar dados com features
        logger.info(f"Carregando dados de: {input_file}")
        validate_file_exists(input_file)
        df = pd.read_parquet(input_file)
        
        logger.info(f"  Carregadas {len(df):,} linhas com {len(df.columns)} colunas")
        
        # Conectar ao SQLite
        logger.info(f"Conectando ao banco SQLite: {db_file}")
        conn = sqlite3.connect(db_file)
        
        # Criar tabelas agregadas
        create_fraud_statistics(df, conn)
        create_hourly_analysis(df, conn)
        create_amount_category_analysis(df, conn)
        create_time_period_analysis(df, conn)
        create_daily_summary(df, conn)
        
        # Criar índices para performance
        logger.info("Criando índices...")
        cursor = conn.cursor()
        
        # Commit e fechar
        conn.commit()
        
        # Listar todas as tabelas criadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        conn.close()
        
        # Estatísticas finais
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        file_size = os.path.getsize(db_file)
        
        stats = {
            'input_rows': len(df),
            'tables_created': len(table_names),
            'table_names': table_names,
            'database_file': db_file,
            'file_size': format_size(file_size),
            'duration_seconds': round(duration, 2)
        }
        
        logger.info("=" * 80)
        logger.info("AGREGAÇÕES CONCLUÍDAS COM SUCESSO!")
        logger.info(f"Linhas processadas: {stats['input_rows']:,}")
        logger.info(f"Tabelas criadas: {stats['tables_created']}")
        for table in table_names:
            logger.info(f"  - {table}")
        logger.info(f"Database: {db_file}")
        logger.info(f"Tamanho: {stats['file_size']}")
        logger.info(f"Tempo: {duration:.2f}s")
        logger.info("=" * 80)
        
        return stats
        
    except Exception as e:
        logger.error(f"ERRO no processamento Gold Aggregations: {e}")
        raise


if __name__ == "__main__":
    try:
        stats = process_gold_aggregations()
        print(f"\n✅ Sucesso! {stats['tables_created']} tabelas criadas")
        print(f"   Database: {stats['database_file']}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
