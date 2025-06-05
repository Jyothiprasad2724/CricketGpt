from fastapi import APIRouter
import sqlite3
import pandas as pd

router = APIRouter()

@router.get("/odi-stats")
def get_odi_stats():
    conn = sqlite3.connect(r"CricketGpt\app\Database\cricket_stats.db")
    df = pd.read_sql_query("SELECT * FROM odi_stats", conn)
    return df.to_dict(orient="records")
