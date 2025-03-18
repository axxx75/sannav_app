import os
import shutil
from datetime import datetime

# Definisci le variabili
src_file = "/var/www/localhost/htdocs/result_json/output.csv.gz"
dst_dir = "/mnt/bk"

# Crea la directory di destinazione se non esiste
if not os.path.exists(dst_dir):
    os.makedirs(dst_dir)

# Ottieni il timestamp corrente
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Estendi il nome del file con il timestamp
filename, file_extension = os.path.splitext(os.path.basename(src_file))
dst_filename = f"{timestamp}_{filename}{file_extension}"

# Copia il file nella directory di destinazione
try:
    shutil.copy(src_file, os.path.join(dst_dir, dst_filename))
    print(f"File {src_file} copiato con successo in {dst_dir} come {dst_filename}")
except Exception as e:
    print(f"Errore durante la copia del file: {str(e)}")
