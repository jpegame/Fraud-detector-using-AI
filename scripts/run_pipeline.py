from bronze_processing import run_bronze
from silver_processing import run_silver
from gold_processing import run_gold
from train_model import train_model

def main():
    print("=" * 50)
    print("INICIANDO PIPELINE DE DETECÇÃO DE FRAUDES")
    print("=" * 50)
    
    print("\n[1/4] Processando camada BRONZE...")
    run_bronze()
    
    print("\n[2/4] Processando camada SILVER...")
    silver_df = run_silver()
    
    print("\n[3/4] Processando camada GOLD...")
    run_gold(silver_df)
    
    print("\n[4/4] Treinando modelo de ML...")
    train_model()
    
    print("\n" + "=" * 50)
    print("PIPELINE CONCLUIDO COM SUCESSO!")
    print("=" * 50)

if __name__ == "__main__":
    main()
