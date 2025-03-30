import sqlite3
import pandas as pd
import os

DB_PATH = "/app/result_json/data.sqlite"
CSV_PATH = "/app/result_json/output.csv"


def init_db():
    print("🔄 Creazione del database SQLite...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dati (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            switch TEXT,
            vswitch TEXT,
            pidx TEXT,
            sp TEXT,
            speed TEXT,
            speed_sup TEXT,
            ctx TEXT,
            ctx_name TEXT,
            pn TEXT,
            state TEXT,
            status TEXT,
            wwpn TEXT,
            alias TEXT,
            role TEXT,
            zone TEXT,
            note TEXT
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Database creato con successo!")

if __name__ == "__main__":
    init_db()

