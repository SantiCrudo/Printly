import shutil
import smtplib
from datetime import datetime
import os

# Ajusta el threshold si querés probar (ej: 0.1 para que alerte con > 10%)
THRESHOLD = 0.8 
MOCK_LOG_FILE = "storage/emails_mock.log"

def _log_email(subject: str, to: str, body: str):
    os.makedirs(os.path.dirname(MOCK_LOG_FILE), exist_ok=True)
    with open(MOCK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write("-" * 50 + "\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"To: {to}\n")
        f.write(f"Subject: {subject}\n")
        f.write("Body:\n")
        f.write(body + "\n")
        f.write("-" * 50 + "\n\n")
    print(f"[*] ALERTA ENVIADA A {to}: {subject}")

def check_disk_space():
    # '/' es la raíz en linux/mac. En Windows podés chequear 'C:\\'
    # Como este script se va a dockerizar o correr en Ubuntu, chequear "/"
    path = "/"
    if os.name == 'nt':
        path = "C:\\"
        
    total, used, free = shutil.disk_usage(path)
    percent_used = used / total

    print(f"Uso de disco en {path}: {percent_used:.2%}")

    if percent_used > THRESHOLD:
        msg = f"¡Alerta CRÍTICA!\n\nEl uso del disco ha superado el límite.\nUso actual: {percent_used:.2%}\nPor favor libere espacio inmediatamente o limpie la carpeta storage/."
        _log_email("ALERTA: Disco casi lleno", "admin@printly.ar", msg)
    else:
        print("Disco en estado normal. No se requiere acción.")

if __name__ == "__main__":
    check_disk_space()
