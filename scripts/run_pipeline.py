from silver_processing import run_silver
from gold_processing import run_gold

def main():
    silver_df = run_silver()
    run_gold(silver_df)

if __name__ == "__main__":
    main()
