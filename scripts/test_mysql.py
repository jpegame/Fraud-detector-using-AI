import pandas as pd
from db import get_mysql_engine

engine = get_mysql_engine()
print(type(engine))

df = pd.read_sql("SELECT 1", engine)
print(df)
