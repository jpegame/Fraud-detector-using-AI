"""
Valida os dados da camada Bronze
Verifica integridade, contagens e estrutura dos arquivos
"""

import json
import os
import sys

# Adicionar diretório scripts ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import setup_logger, count_lines, validate_file_exists

# Configurar logger
logger = setup_logger('validate_bronze')


def validate_json_line(line, line_number, source):
    """
    Valida uma linha JSON
    
    Args:
        line: Linha do arquivo
        line_number: Número da linha
        source: Fonte dos dados (mysql/mongo)
        
    Returns:
        dict ou None se inválido
    """
    try:
        data = json.loads(line)
        
        # Verificar campos obrigatórios de metadata
        required_metadata = ['_extracted_at', '_source']
        for field in required_metadata:
            if field not in data:
                logger.warning(f"Linha {line_number}: campo '{field}' ausente")
                return None
        
        # Verificar se _source bate com o esperado
        if data['_source'] != source:
            logger.warning(f"Linha {line_number}: _source esperado '{source}', encontrado '{data['_source']}'")
        
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Linha {line_number}: JSON inválido - {e}")
        return None


def validate_bronze_file(filepath, source):
    """
    Valida um arquivo Bronze
    
    Args:
        filepath: Caminho do arquivo
        source: Fonte esperada (mysql/mongo)
        
    Returns:
        dict: Estatísticas de validação
    """
    logger.info(f"Validando arquivo: {filepath}")
    
    # Verificar se arquivo existe
    validate_file_exists(filepath)
    
    total_lines = 0
    valid_lines = 0
    invalid_lines = 0
    sample_data = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            
            if not line:
                invalid_lines += 1
                continue
            
            data = validate_json_line(line, line_number, source)
            
            if data:
                valid_lines += 1
                # Guardar primeira linha como sample
                if sample_data is None:
                    sample_data = data
            else:
                invalid_lines += 1
    
    # Calcular estatísticas
    file_size = os.path.getsize(filepath)
    validity_rate = (valid_lines / total_lines * 100) if total_lines > 0 else 0
    
    stats = {
        'file': filepath,
        'source': source,
        'total_lines': total_lines,
        'valid_lines': valid_lines,
        'invalid_lines': invalid_lines,
        'validity_rate': round(validity_rate, 2),
        'file_size_mb': round(file_size / (1024 * 1024), 2),
        'sample_fields': list(sample_data.keys()) if sample_data else []
    }
    
    logger.info(f"  Total de linhas: {total_lines:,}")
    logger.info(f"  Linhas válidas: {valid_lines:,}")
    logger.info(f"  Linhas inválidas: {invalid_lines:,}")
    logger.info(f"  Taxa de validade: {validity_rate:.2f}%")
    logger.info(f"  Tamanho: {stats['file_size_mb']:.2f} MB")
    
    return stats


def validate_all_bronze():
    """
    Valida todos os arquivos Bronze
    
    Returns:
        dict: Estatísticas consolidadas
    """
    logger.info("=" * 80)
    logger.info("VALIDAÇÃO DA CAMADA BRONZE")
    logger.info("=" * 80)
    
    bronze_dir = os.getenv('BRONZE_DIR', './bronze')
    
    files_to_validate = [
        {
            'path': os.path.join(bronze_dir, 'mysql', 'credit_card1.txt'),
            'source': 'mysql'
        },
        {
            'path': os.path.join(bronze_dir, 'mongo', 'credit_card2.txt'),
            'source': 'mongodb'
        }
    ]
    
    results = []
    total_valid = 0
    total_invalid = 0
    
    for file_info in files_to_validate:
        filepath = file_info['path']
        source = file_info['source']
        
        if not os.path.exists(filepath):
            logger.warning(f"Arquivo não encontrado: {filepath}")
            continue
        
        try:
            stats = validate_bronze_file(filepath, source)
            results.append(stats)
            total_valid += stats['valid_lines']
            total_invalid += stats['invalid_lines']
        except Exception as e:
            logger.error(f"Erro ao validar {filepath}: {e}")
    
    # Resumo final
    logger.info("=" * 80)
    logger.info("RESUMO DA VALIDAÇÃO")
    logger.info("=" * 80)
    logger.info(f"Arquivos validados: {len(results)}")
    logger.info(f"Total de linhas válidas: {total_valid:,}")
    logger.info(f"Total de linhas inválidas: {total_invalid:,}")
    
    if total_invalid > 0:
        logger.warning(f"⚠️  Atenção: {total_invalid} linhas inválidas encontradas!")
    else:
        logger.info("✅ Todos os dados estão válidos!")
    
    logger.info("=" * 80)
    
    return {
        'files_validated': len(results),
        'total_valid_lines': total_valid,
        'total_invalid_lines': total_invalid,
        'results': results
    }


if __name__ == "__main__":
    try:
        stats = validate_all_bronze()
        
        if stats['total_invalid_lines'] > 0:
            print(f"\n⚠️  Validação concluída com {stats['total_invalid_lines']} linhas inválidas")
            sys.exit(1)
        else:
            print(f"\n✅ Validação concluída! {stats['total_valid_lines']:,} linhas válidas")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Erro na validação: {e}")
        sys.exit(1)
