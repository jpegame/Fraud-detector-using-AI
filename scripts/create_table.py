"""
Cria a tabela transactions no MySQL
Execute este script ANTES de importar os dados
"""

import os
import sys
import mysql.connector
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("=" * 80)
print("CRIANDO TABELA 'transactions' NO MYSQL")
print("=" * 80)

try:
    # Conectar ao MySQL
    print(f"Conectando ao MySQL...")
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    
    cursor = conn.cursor()
    print(f"✅ Conectado ao MySQL!")
    
    # Criar tabela
    print(f"Criando tabela 'transactions'...")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        Time DOUBLE,
        V1 DOUBLE,
        V2 DOUBLE,
        V3 DOUBLE,
        V4 DOUBLE,
        V5 DOUBLE,
        V6 DOUBLE,
        V7 DOUBLE,
        V8 DOUBLE,
        V9 DOUBLE,
        V10 DOUBLE,
        V11 DOUBLE,
        V12 DOUBLE,
        V13 DOUBLE,
        V14 DOUBLE,
        V15 DOUBLE,
        V16 DOUBLE,
        V17 DOUBLE,
        V18 DOUBLE,
        V19 DOUBLE,
        V20 DOUBLE,
        V21 DOUBLE,
        V22 DOUBLE,
        V23 DOUBLE,
        V24 DOUBLE,
        V25 DOUBLE,
        V26 DOUBLE,
        V27 DOUBLE,
        V28 DOUBLE,
        Amount DOUBLE,
        Class INT
    )
    """
    
    cursor.execute(create_table_sql)
    print(f"✅ Tabela 'transactions' criada com sucesso!")
    
    # Verificar se a tabela foi criada
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\nTabelas existentes no database '{os.getenv('MYSQL_DATABASE')}':")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Fechar conexões
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ TABELA CRIADA COM SUCESSO!")
    print("Agora você pode rodar: python scripts/import_csv.py")
    print("=" * 80)
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ ERRO ao criar tabela: {e}")
    print("\nVerifique:")
    print("  1. MySQL está rodando? (docker ps)")
    print("  2. Senha correta no .env?")
    print("  3. Database existe? (creditdb)")
    sys.exit(1)
