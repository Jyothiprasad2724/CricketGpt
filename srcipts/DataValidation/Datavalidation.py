import sqlite3
import pandas as pd 

conn = sqlite3.connect(r"CricketGpt\app\Database\cricket_stats.db")
df = pd.read_sql_query("select * from odi_stats LIMIT 10",conn)
print(df)