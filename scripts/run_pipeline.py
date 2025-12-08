"""
Pipeline ETL Completo - Fraud Detection
Executa todas as etapas do pipeline: Bronze → Silver → Gold
"""

import os
import sys
from datetime import datetime

# Adicionar diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger

# Importar módulos do pipeline
from bronze_mysql import extract_mysql_to_bronze
from bronze_mongo import extract_mongo_to_bronze
from validate_bronze import validate_all_bronze
from silver_clean import process_silver_clean
from silver_features import process_silver_features
from gold_aggregations import process_gold_aggregations
from gold_ml_prep import process_gold_ml_prep

# Configurar logger
logger = setup_logger('run_pipeline')


def print_banner(text):
    """Imprime um banner formatado"""
    print("\n" + "=" * 100)
    print(f"  {text}")
    print("=" * 100 + "\n")


def run_pipeline(skip_bronze=False, skip_silver=False, skip_gold=False):
    """
    Executa o pipeline ETL completo
    
    Args:
        skip_bronze: Se True, pula extração Bronze
        skip_silver: Se True, pula processamento Silver
        skip_gold: Se True, pula processamento Gold
        
    Returns:
        dict: Estatísticas de todas as etapas
    """
    pipeline_start = datetime.now()
    results = {}
    
    logger.info("=" * 100)
    logger.info("INICIANDO PIPELINE ETL COMPLETO - FRAUD DETECTION")
    logger.info("=" * 100)
    logger.info(f"Início: {pipeline_start.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    try:
        # ========== CAMADA BRONZE ==========
        if not skip_bronze:
            print_banner("ETAPA 1/7 - Extração MySQL → Bronze")
            try:
                stats_mysql = extract_mysql_to_bronze()
                results['bronze_mysql'] = stats_mysql
                logger.info("✅ MySQL → Bronze concluído")
            except Exception as e:
                logger.error(f"❌ ERRO em MySQL → Bronze: {e}")
                raise
            
            print_banner("ETAPA 2/7 - Extração MongoDB → Bronze")
            try:
                stats_mongo = extract_mongo_to_bronze()
                results['bronze_mongo'] = stats_mongo
                logger.info("✅ MongoDB → Bronze concluído")
            except Exception as e:
                logger.error(f"❌ ERRO em MongoDB → Bronze: {e}")
                raise
            
            print_banner("ETAPA 3/7 - Validação da Camada Bronze")
            try:
                stats_validate = validate_all_bronze()
                results['validate_bronze'] = stats_validate
                
                if stats_validate['total_invalid_lines'] > 0:
                    logger.warning(f"⚠️  {stats_validate['total_invalid_lines']} linhas inválidas encontradas")
                else:
                    logger.info("✅ Validação Bronze concluída - todos os dados válidos")
            except Exception as e:
                logger.error(f"❌ ERRO na validação Bronze: {e}")
                raise
        else:
            logger.info("⏭️  Pulando extração Bronze (skip_bronze=True)")
        
        # ========== CAMADA SILVER ==========
        if not skip_silver:
            print_banner("ETAPA 4/7 - Processamento Silver - Limpeza")
            try:
                stats_clean = process_silver_clean()
                results['silver_clean'] = stats_clean
                logger.info("✅ Silver Clean concluído")
            except Exception as e:
                logger.error(f"❌ ERRO em Silver Clean: {e}")
                raise
            
            print_banner("ETAPA 5/7 - Processamento Silver - Features")
            try:
                stats_features = process_silver_features()
                results['silver_features'] = stats_features
                logger.info("✅ Silver Features concluído")
            except Exception as e:
                logger.error(f"❌ ERRO em Silver Features: {e}")
                raise
        else:
            logger.info("⏭️  Pulando processamento Silver (skip_silver=True)")
        
        # ========== CAMADA GOLD ==========
        if not skip_gold:
            print_banner("ETAPA 6/7 - Processamento Gold - Agregações")
            try:
                stats_agg = process_gold_aggregations()
                results['gold_aggregations'] = stats_agg
                logger.info("✅ Gold Aggregations concluído")
            except Exception as e:
                logger.error(f"❌ ERRO em Gold Aggregations: {e}")
                raise
            
            print_banner("ETAPA 7/7 - Processamento Gold - ML Preparation")
            try:
                stats_ml = process_gold_ml_prep()
                results['gold_ml'] = stats_ml
                logger.info("✅ Gold ML Prep concluído")
            except Exception as e:
                logger.error(f"❌ ERRO em Gold ML Prep: {e}")
                raise
        else:
            logger.info("⏭️  Pulando processamento Gold (skip_gold=True)")
        
        # ========== RESUMO FINAL ==========
        pipeline_end = datetime.now()
        total_duration = (pipeline_end - pipeline_start).total_seconds()
        
        print_banner("PIPELINE CONCLUÍDO COM SUCESSO! 🎉")
        
        logger.info("=" * 100)
        logger.info("RESUMO DO PIPELINE")
        logger.info("=" * 100)
        logger.info(f"Início: {pipeline_start.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Fim: {pipeline_end.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duração total: {total_duration:.2f}s ({total_duration/60:.2f} minutos)")
        logger.info("")
        
        # Estatísticas por camada
        if 'bronze_mysql' in results:
            logger.info(f"📊 BRONZE - MySQL: {results['bronze_mysql']['rows_extracted']:,} linhas")
        if 'bronze_mongo' in results:
            logger.info(f"📊 BRONZE - MongoDB: {results['bronze_mongo']['documents_extracted']:,} documentos")
        if 'silver_clean' in results:
            logger.info(f"📊 SILVER - Clean: {results['silver_clean']['combined_rows']:,} linhas ({results['silver_clean']['fraud_rate_pct']}% fraude)")
        if 'silver_features' in results:
            logger.info(f"📊 SILVER - Features: {results['silver_features']['new_features']} novas features criadas")
        if 'gold_aggregations' in results:
            logger.info(f"📊 GOLD - Analytics: {results['gold_aggregations']['tables_created']} tabelas SQLite criadas")
        if 'gold_ml' in results:
            logger.info(f"📊 GOLD - ML: {results['gold_ml']['num_features']} features, {results['gold_ml']['train_samples']:,} treino, {results['gold_ml']['test_samples']:,} teste")
        
        logger.info("")
        logger.info("=" * 100)
        logger.info("✅ TODOS OS DADOS FORAM PROCESSADOS COM SUCESSO!")
        logger.info("=" * 100)
        
        results['pipeline_duration_seconds'] = total_duration
        results['pipeline_start'] = pipeline_start.isoformat()
        results['pipeline_end'] = pipeline_end.isoformat()
        
        return results
        
    except Exception as e:
        pipeline_end = datetime.now()
        total_duration = (pipeline_end - pipeline_start).total_seconds()
        
        logger.error("=" * 100)
        logger.error("❌ PIPELINE FALHOU!")
        logger.error(f"Erro: {e}")
        logger.error(f"Duração até falha: {total_duration:.2f}s")
        logger.error("=" * 100)
        
        raise


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pipeline ETL Completo - Fraud Detection')
    parser.add_argument('--skip-bronze', action='store_true', help='Pula extração Bronze')
    parser.add_argument('--skip-silver', action='store_true', help='Pula processamento Silver')
    parser.add_argument('--skip-gold', action='store_true', help='Pula processamento Gold')
    
    args = parser.parse_args()
    
    try:
        print_banner("🚀 PIPELINE ETL - FRAUD DETECTION")
        print("Iniciando processamento completo...")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = run_pipeline(
            skip_bronze=args.skip_bronze,
            skip_silver=args.skip_silver,
            skip_gold=args.skip_gold
        )
        
        print("\n" + "=" * 100)
        print("✅ PIPELINE EXECUTADO COM SUCESSO!")
        print(f"⏱️  Tempo total: {results['pipeline_duration_seconds']:.2f}s ({results['pipeline_duration_seconds']/60:.2f} min)")
        print("=" * 100 + "\n")
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 100)
        print(f"❌ ERRO NA EXECUÇÃO DO PIPELINE: {e}")
        print("=" * 100 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
