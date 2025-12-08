"""
Camada Gold - Preparação de Dataset para Machine Learning
Separa features e target, cria splits treino/teste
"""

import os
import sys
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split

# Adicionar diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, ensure_dir, validate_file_exists, format_size

# Configurar logger
logger = setup_logger('gold_ml_prep')


def prepare_ml_features(df):
    """
    Prepara features para Machine Learning
    
    Args:
        df: DataFrame com todas as features
        
    Returns:
        tuple: (X, y) - features e target
    """
    logger.info("Preparando features para ML...")
    
    # Colunas a excluir (não são features úteis para ML)
    exclude_cols = [
        'Class',           # Target
        'is_fraud',        # Derivado do target
        'time_period',     # Categórica (já temos hour)
        'amount_category'  # Categórica (já temos amount_normalized)
    ]
    
    # Selecionar apenas colunas numéricas
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Remover colunas excluídas
    feature_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    logger.info(f"  Features selecionadas: {len(feature_cols)}")
    logger.info(f"  Primeiras features: {feature_cols[:5]}...")
    
    # Separar features (X) e target (y)
    X = df[feature_cols].copy()
    y = df['Class'].copy()
    
    # Verificar valores nulos
    null_count = X.isnull().sum().sum()
    if null_count > 0:
        logger.warning(f"  Encontrados {null_count} valores nulos - preenchendo com 0")
        X = X.fillna(0)
    
    logger.info(f"  X shape: {X.shape}")
    logger.info(f"  y shape: {y.shape}")
    logger.info(f"  Distribuição do target:")
    logger.info(f"    Classe 0 (normal): {(y == 0).sum():,} ({(y == 0).sum() / len(y) * 100:.2f}%)")
    logger.info(f"    Classe 1 (fraude): {(y == 1).sum():,} ({(y == 1).sum() / len(y) * 100:.2f}%)")
    
    return X, y


def create_train_test_split(X, y, test_size=0.2, random_state=42):
    """
    Cria split treino/teste estratificado
    
    Args:
        X: Features
        y: Target
        test_size: Proporção do teste (padrão 20%)
        random_state: Seed para reprodutibilidade
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    logger.info(f"Criando split treino/teste ({int((1-test_size)*100)}% / {int(test_size*100)}%)...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y  # Mantém proporção de classes
    )
    
    logger.info(f"  Treino: {len(X_train):,} amostras")
    logger.info(f"    Classe 0: {(y_train == 0).sum():,}")
    logger.info(f"    Classe 1: {(y_train == 1).sum():,}")
    
    logger.info(f"  Teste: {len(X_test):,} amostras")
    logger.info(f"    Classe 0: {(y_test == 0).sum():,}")
    logger.info(f"    Classe 1: {(y_test == 1).sum():,}")
    
    return X_train, X_test, y_train, y_test


def save_ml_datasets(X_train, X_test, y_train, y_test, output_dir):
    """
    Salva datasets de ML em arquivos Parquet
    
    Args:
        X_train, X_test, y_train, y_test: Datasets
        output_dir: Diretório de saída
    """
    logger.info(f"Salvando datasets em: {output_dir}")
    
    ensure_dir(output_dir)
    
    # Salvar cada dataset
    files_saved = []
    
    X_train_path = os.path.join(output_dir, 'X_train.parquet')
    X_train.to_parquet(X_train_path, index=False, compression='snappy')
    files_saved.append(('X_train.parquet', os.path.getsize(X_train_path)))
    logger.info(f"  ✓ X_train.parquet ({format_size(files_saved[-1][1])})")
    
    X_test_path = os.path.join(output_dir, 'X_test.parquet')
    X_test.to_parquet(X_test_path, index=False, compression='snappy')
    files_saved.append(('X_test.parquet', os.path.getsize(X_test_path)))
    logger.info(f"  ✓ X_test.parquet ({format_size(files_saved[-1][1])})")
    
    y_train_path = os.path.join(output_dir, 'y_train.parquet')
    y_train.to_frame('Class').to_parquet(y_train_path, index=False, compression='snappy')
    files_saved.append(('y_train.parquet', os.path.getsize(y_train_path)))
    logger.info(f"  ✓ y_train.parquet ({format_size(files_saved[-1][1])})")
    
    y_test_path = os.path.join(output_dir, 'y_test.parquet')
    y_test.to_frame('Class').to_parquet(y_test_path, index=False, compression='snappy')
    files_saved.append(('y_test.parquet', os.path.getsize(y_test_path)))
    logger.info(f"  ✓ y_test.parquet ({format_size(files_saved[-1][1])})")
    
    return files_saved


def process_gold_ml_prep():
    """
    Processa a camada Gold - preparação de ML
    
    Returns:
        dict: Estatísticas do processamento
    """
    logger.info("=" * 80)
    logger.info("PROCESSAMENTO GOLD - Preparação ML")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Obter configurações
        silver_dir = os.getenv('SILVER_DIR', './silver')
        gold_dir = os.getenv('GOLD_DIR', './gold')
        
        input_file = os.path.join(silver_dir, 'features', 'transactions_features.parquet')
        output_dir = os.path.join(gold_dir, 'ml')
        
        # Carregar dados com features
        logger.info(f"Carregando dados de: {input_file}")
        validate_file_exists(input_file)
        df = pd.read_parquet(input_file)
        
        logger.info(f"  Carregadas {len(df):,} linhas com {len(df.columns)} colunas")
        
        # Preparar features
        X, y = prepare_ml_features(df)
        
        # Criar split treino/teste
        X_train, X_test, y_train, y_test = create_train_test_split(X, y)
        
        # Salvar datasets
        files_saved = save_ml_datasets(X_train, X_test, y_train, y_test, output_dir)
        
        # Estatísticas finais
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        total_size = sum(size for _, size in files_saved)
        
        stats = {
            'total_samples': len(df),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'num_features': len(X.columns),
            'fraud_rate_train': round((y_train == 1).sum() / len(y_train) * 100, 4),
            'fraud_rate_test': round((y_test == 1).sum() / len(y_test) * 100, 4),
            'output_dir': output_dir,
            'files_created': len(files_saved),
            'total_size': format_size(total_size),
            'duration_seconds': round(duration, 2)
        }
        
        logger.info("=" * 80)
        logger.info("PREPARAÇÃO ML CONCLUÍDA COM SUCESSO!")
        logger.info(f"Total de amostras: {stats['total_samples']:,}")
        logger.info(f"  Treino: {stats['train_samples']:,} ({stats['fraud_rate_train']}% fraude)")
        logger.info(f"  Teste: {stats['test_samples']:,} ({stats['fraud_rate_test']}% fraude)")
        logger.info(f"Features: {stats['num_features']}")
        logger.info(f"Arquivos criados: {stats['files_created']}")
        logger.info(f"Tamanho total: {stats['total_size']}")
        logger.info(f"Diretório: {output_dir}")
        logger.info(f"Tempo: {duration:.2f}s")
        logger.info("=" * 80)
        
        return stats
        
    except Exception as e:
        logger.error(f"ERRO no processamento Gold ML Prep: {e}")
        raise


if __name__ == "__main__":
    try:
        stats = process_gold_ml_prep()
        print(f"\n✅ Sucesso! Dataset ML preparado")
        print(f"   Treino: {stats['train_samples']:,} | Teste: {stats['test_samples']:,}")
        print(f"   Features: {stats['num_features']}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
