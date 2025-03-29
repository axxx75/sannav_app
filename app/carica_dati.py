import sqlite3
import csv

DB_PATH = "/app/result_json/data.sqlite"
CSV_PATH = "/app/result_json/output.csv"

def carica_dati():
    print("🔄 Caricamento dati nel database SQLite...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Legge l'intestazione del CSV

        for row in reader:
            cursor.execute("""
                INSERT INTO dati (switch, vswitch, pidx, sp, speed, speed_sup, ctx, ctx_name, pn, state, status, wwpn, alias, role, zone, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)  # Inserisce solo le prime 5 colonne

    conn.commit()
    conn.close()
    print("✅ Dati caricati con successo!")

if __name__ == "__main__":
    carica_dati()

