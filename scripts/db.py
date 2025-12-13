import os
from sqlalchemy import create_engine

def get_mysql_engine():
    return create_engine(
        f"mysql+mysqlconnector://root:{os.getenv('MYSQL_ROOT_PASSWORD')}@"
        f"{os.getenv('MYSQL_HOST', 'mysql')}/"
        f"{os.getenv('MYSQL_DATABASE')}"
    )

def get_sqlite_engine():
    return create_engine("sqlite:///data/gold.db")
