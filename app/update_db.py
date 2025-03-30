import sqlite3
import csv

DB_PATH = "/app/result_json/data.sqlite"
CSV_PATH = "/app/result_json/output.csv"

def ricarica_dati():
    print("🔄 Ricaricamento dati nel database SQLite...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Rimuove la tabella se esiste già
    cursor.execute("DROP TABLE IF EXISTS dati")

    # Ricrea la tabella
    cursor.execute("""
        CREATE TABLE dati (
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
        )
    """)

    # Legge e inserisce i dati dal CSV
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Legge l'intestazione del CSV

        for row in reader:
            cursor.execute("""
                INSERT INTO dati (switch, vswitch, pidx, sp, speed, speed_sup, ctx, ctx_name, pn, state, status, wwpn, alias, role, zone, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)

    conn.commit()
    conn.close()
    print("✅ Database ricaricato con successo!")

if __name__ == "__main__":
    ricarica_dati()
