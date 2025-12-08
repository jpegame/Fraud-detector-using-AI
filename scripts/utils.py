"""
Utilidades compartilhadas para o pipeline ETL
Funções para conexões, logging e validações
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
from pymongo import MongoClient

# Carregar variáveis de ambiente
load_dotenv()


def setup_logger(name):
    """
    Configura logger para um módulo específico
    
    Args:
        name: Nome do módulo/script
        
    Returns:
        Logger configurado
    """
    logs_dir = os.getenv('LOGS_DIR', './logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Handler para arquivo
    log_file = os.path.join(logs_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_mysql_connection(retry_count=None, retry_delay=None):
    """
    Cria conexão com MySQL com retry automático
    
    Args:
        retry_count: Número de tentativas (padrão do .env)
        retry_delay: Delay entre tentativas em segundos (padrão do .env)
        
    Returns:
        Conexão MySQL
        
    Raises:
        Exception: Se não conseguir conectar após todas as tentativas
    """
    import time
    
    logger = setup_logger('mysql_connection')
    
    if retry_count is None:
        retry_count = int(os.getenv('DB_RETRY_COUNT', 10))
    if retry_delay is None:
        retry_delay = int(os.getenv('DB_RETRY_DELAY', 3))
    
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DATABASE')
    
    logger.info(f"Connecting to MySQL: {host}:{port}/{database}")
    
    for attempt in range(1, retry_count + 1):
        try:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            logger.info(f"MySQL connection successful (attempt {attempt})")
            return conn
        except Exception as e:
            logger.warning(f"MySQL connection failed (attempt {attempt}/{retry_count}): {e}")
            if attempt < retry_count:
                time.sleep(retry_delay)
    
    raise Exception(f"Failed to connect to MySQL after {retry_count} attempts")


def get_mongo_connection():
    """
    Cria conexão com MongoDB
    
    Returns:
        MongoClient
        
    Raises:
        Exception: Se não conseguir conectar
    """
    logger = setup_logger('mongo_connection')
    
    uri = os.getenv('MONGO_URI')
    
    if not uri:
        raise ValueError("MONGO_URI not found in environment variables")
    
    logger.info("Connecting to MongoDB...")
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Testar conexão
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return client
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise


def validate_file_exists(filepath):
    """
    Valida se um arquivo existe
    
    Args:
        filepath: Caminho do arquivo
        
    Raises:
        FileNotFoundError: Se arquivo não existir
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")


def count_lines(filepath):
    """
    Conta linhas em um arquivo
    
    Args:
        filepath: Caminho do arquivo
        
    Returns:
        Número de linhas
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def get_timestamp():
    """
    Retorna timestamp ISO format
    
    Returns:
        String timestamp UTC
    """
    return datetime.utcnow().isoformat()


def ensure_dir(directory):
    """
    Garante que um diretório existe, criando se necessário
    
    Args:
        directory: Caminho do diretório
    """
    os.makedirs(directory, exist_ok=True)


def format_size(bytes_size):
    """
    Formata tamanho em bytes para formato legível
    
    Args:
        bytes_size: Tamanho em bytes
        
    Returns:
        String formatada (ex: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"
