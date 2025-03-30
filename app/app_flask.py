from flask import Flask, jsonify, render_template, request, Response
from datetime import datetime
import sqlite3, os

app = Flask(__name__)
DB_PATH = "/app/result_json/data.sqlite"
CSV_PATH = "/app/result_json/output.csv"

def get_db_connection():
    """Crea una connessione al database SQLite e imposta il factory dei risultati."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Risultati come dizionari
        return conn
    except sqlite3.Error as e:
        print("❌ Errore di connessione:", e)
        return None

@app.route('/')
def index():
    last_update = get_last_update()
    return render_template("index.html", last_update=last_update)

def get_last_update():
    """Restituisce la data di ultima modifica del file CSV."""
    if os.path.exists(CSV_PATH):
        timestamp = os.path.getmtime(CSV_PATH)
        return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M:%S")
    return "Il file non esiste."

@app.route("/api/last-update")
def last_update():
    return jsonify({"last_update": get_last_update()})

@app.route('/data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()

    draw = request.args.get('draw', type=int, default=1)
    start = request.args.get('start', type=int, default=0)
    length = request.args.get('length', type=int, default=50)

    print("🟢 Parametri ricevuti:", request.args)  # DEBUG

    columns = ["id", "switch", "vswitch", "pidx", "sp", "speed", "speed_sup", "ctx",
               "ctx_name", "pn", "state", "status", "wwpn", "alias", "role", "zone", "note"]

    # **Gestione della ricerca avanzata**
    base_query = "FROM dati WHERE 1=1"
    params = []

    for i, col in enumerate(columns):
        search_value = request.args.get(f'columns[{i}][search][value]', '')

        if search_value:
            base_query += f" AND {col} LIKE ?"
            params.append(f"%{search_value}%")

    # **Gestione dell'ordinamento**
    order_column_index = request.args.get('order[0][column]', type=int, default=0)
    order_dir = request.args.get('order[0][dir]', default='asc')

    order_column = columns[order_column_index] if 0 <= order_column_index < len(columns) else "id"
    order_direction = "ASC" if order_dir == "asc" else "DESC"

    # **Conta il totale dei record senza filtri**
    cursor.execute("SELECT COUNT(*) FROM dati")
    total_records = cursor.fetchone()[0]

    # **Conta il totale dei record filtrati**
    filtered_query = f"SELECT COUNT(*) {base_query}"
    cursor.execute(filtered_query, params)
    filtered_records = cursor.fetchone()[0]

    # **Recupera solo i dati per la pagina corrente con sorting**
    data_query = f"""
        SELECT id, switch, vswitch, pidx, sp, speed, speed_sup, ctx, ctx_name, pn, state, status,
               wwpn, alias, role, zone, note
        {base_query}
        ORDER BY {order_column} {order_direction}
        LIMIT ? OFFSET ?
    """
    params.extend([length, start])
    cursor.execute(data_query, params)
    rows = cursor.fetchall()
    conn.close()

    data = [dict(row) for row in rows]
    return jsonify({
        "draw": draw,
        "recordsTotal": total_records,   # ✅ Numero totale di record nel database
        "recordsFiltered": filtered_records,  # ✅ Numero di record filtrati
        "data": data
    })

@app.route('/api/export', methods=['GET'])
def export_filtered_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = "SELECT * FROM dati WHERE 1=1"
    params = []
    columns = ["id", "switch", "vswitch", "pidx", "sp", "speed", "speed_sup", "ctx", "ctx_name", "pn", "state", "status", "wwpn", "alias", "role", "zone", "note"]

    # **Recuperiamo i parametri dei filtri dalla richiesta**
    for i, col in enumerate(columns):
        search_value = request.args.get(f'columns[{i}][search][value]', '').strip()
        if search_value:
            base_query += f" AND {col} LIKE ?"
            params.append(f"%{search_value}%")

    # **Eseguiamo la query filtrata**
    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    conn.close()

    # **Formato di esportazione**
    file_format = request.args.get('format', 'csv')

    if file_format == 'csv':
        def generate():
            yield ','.join(columns) + '\n'
            for row in rows:
                yield ','.join(str(row[col]) if row[col] is not None else '' for col in columns) + '\n'

        return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=export.csv"})

    elif file_format == 'excel':
        import io
        import xlsxwriter

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # **Scriviamo i dati**
        worksheet.write_row(0, 0, columns)
        for row_idx, row in enumerate(rows, start=1):
            worksheet.write_row(row_idx, 0, [row[col] if row[col] is not None else '' for col in columns])

        workbook.close()
        output.seek(0)

        return Response(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        headers={"Content-Disposition": "attachment; filename=export.xlsx"})

    return jsonify({"error": "Formato non supportato"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
