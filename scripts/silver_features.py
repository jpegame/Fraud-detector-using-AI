"""
Camada Silver - Feature Engineering
Cria features derivadas para análise e machine learning
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Adicionar diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, ensure_dir, validate_file_exists, format_size

# Configurar logger
logger = setup_logger('silver_features')


def create_temporal_features(df):
    """
    Cria features temporais baseadas em Time
    
    Args:
        df: DataFrame com coluna Time
        
    Returns:
        DataFrame com features temporais
    """
    logger.info("Criando features temporais...")
    
    if 'Time' not in df.columns:
        logger.warning("  Coluna 'Time' não encontrada, pulando features temporais")
        return df
    
    # Time está em segundos desde a primeira transação
    # Converter para horas, dias
    df['hour'] = (df['Time'] / 3600) % 24
    df['day'] = (df['Time'] / 86400).astype(int)
    
    # Categorias de hora (madrugada, manhã, tarde, noite)
    df['time_period'] = pd.cut(
        df['hour'],
        bins=[0, 6, 12, 18, 24],
        labels=['madrugada', 'manha', 'tarde', 'noite'],
        include_lowest=True
    )
    
    logger.info("  Criadas: hour, day, time_period")
    
    return df


def create_amount_features(df):
    """
    Cria features baseadas em Amount
    
    Args:
        df: DataFrame com coluna Amount
        
    Returns:
        DataFrame com features de Amount
    """
    logger.info("Criando features de Amount...")
    
    if 'Amount' not in df.columns:
        logger.warning("  Coluna 'Amount' não encontrada, pulando features de Amount")
        return df
    
    # Estatísticas de Amount
    amount_mean = df['Amount'].mean()
    amount_std = df['Amount'].std()
    
    # Amount normalizado (z-score)
    df['amount_normalized'] = (df['Amount'] - amount_mean) / amount_std
    
    # Log de Amount (para lidar com valores muito altos)
    df['amount_log'] = np.log1p(df['Amount'])  # log1p = log(1 + x)
    
    # Categorias de valor
    df['amount_category'] = pd.cut(
        df['Amount'],
        bins=[0, 10, 50, 100, 500, float('inf')],
        labels=['very_low', 'low', 'medium', 'high', 'very_high']
    )
    
    # Flags
    df['is_high_value'] = (df['Amount'] > 500).astype(int)
    df['is_very_low_value'] = (df['Amount'] < 1).astype(int)
    
    logger.info("  Criadas: amount_normalized, amount_log, amount_category, is_high_value, is_very_low_value")
    
    return df


def create_fraud_features(df):
    """
    Cria features relacionadas a fraude
    
    Args:
        df: DataFrame com coluna Class
        
    Returns:
        DataFrame com features de fraude
    """
    logger.info("Criando features de fraude...")
    
    if 'Class' not in df.columns:
        logger.warning("  Coluna 'Class' não encontrada, pulando features de fraude")
        return df
    
    # Flag booleana de fraude
    df['is_fraud'] = (df['Class'] == 1).astype(int)
    
    logger.info("  Criadas: is_fraud")
    
    return df


def create_statistical_features(df):
    """
    Cria features estatísticas derivadas dos componentes V1-V28
    
    Args:
        df: DataFrame com colunas V1-V28
        
    Returns:
        DataFrame com features estatísticas
    """
    logger.info("Criando features estatísticas...")
    
    # Identificar colunas V1-V28
    v_cols = [f'V{i}' for i in range(1, 29) if f'V{i}' in df.columns]
    
    if not v_cols:
        logger.warning("  Colunas V1-V28 não encontradas, pulando features estatísticas")
        return df
    
    # Estatísticas agregadas das features PCA
    df['v_mean'] = df[v_cols].mean(axis=1)
    df['v_std'] = df[v_cols].std(axis=1)
    df['v_min'] = df[v_cols].min(axis=1)
    df['v_max'] = df[v_cols].max(axis=1)
    df['v_range'] = df['v_max'] - df['v_min']
    
    logger.info("  Criadas: v_mean, v_std, v_min, v_max, v_range")
    
    return df


def process_silver_features():
    """
    Processa a camada Silver - feature engineering
    
    Returns:
        dict: Estatísticas do processamento
    """
    logger.info("=" * 80)
    logger.info("PROCESSAMENTO SILVER - Feature Engineering")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Obter configurações
        silver_dir = os.getenv('SILVER_DIR', './silver')
        
        input_file = os.path.join(silver_dir, 'cleaned', 'transactions.parquet')
        output_file = os.path.join(silver_dir, 'features', 'transactions_features.parquet')
        
        ensure_dir(os.path.dirname(output_file))
        
        # Carregar dados limpos
        logger.info(f"Carregando dados de: {input_file}")
        validate_file_exists(input_file)
        df = pd.read_parquet(input_file)
        
        initial_cols = len(df.columns)
        logger.info(f"  Carregadas {len(df):,} linhas com {initial_cols} colunas")
        
        # Criar features
        df = create_temporal_features(df)
        df = create_amount_features(df)
        df = create_fraud_features(df)
        df = create_statistical_features(df)
        
        final_cols = len(df.columns)
        new_features = final_cols - initial_cols
        
        # Salvar resultado
        logger.info(f"Salvando features em: {output_file}")
        df.to_parquet(output_file, index=False, compression='snappy')
        
        # Estatísticas finais
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        file_size = os.path.getsize(output_file)
        
        stats = {
            'rows': len(df),
            'initial_columns': initial_cols,
            'final_columns': final_cols,
            'new_features': new_features,
            'output_file': output_file,
            'file_size': format_size(file_size),
            'duration_seconds': round(duration, 2)
        }
        
        logger.info("=" * 80)
        logger.info("FEATURE ENGINEERING CONCLUÍDO!")
        logger.info(f"Linhas: {stats['rows']:,}")
        logger.info(f"Colunas iniciais: {stats['initial_columns']}")
        logger.info(f"Colunas finais: {stats['final_columns']}")
        logger.info(f"Novas features: {stats['new_features']}")
        logger.info(f"Arquivo: {output_file}")
        logger.info(f"Tamanho: {stats['file_size']}")
        logger.info(f"Tempo: {duration:.2f}s")
        logger.info("=" * 80)
        
        return stats
        
    except Exception as e:
        logger.error(f"ERRO no processamento Silver Features: {e}")
        raise


if __name__ == "__main__":
    try:
        stats = process_silver_features()
        print(f"\n✅ Sucesso! {stats['new_features']} novas features criadas")
        print(f"   Total de colunas: {stats['final_columns']}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
