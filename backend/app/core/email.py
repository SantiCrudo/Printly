import os
from datetime import datetime

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
    print(f"[*] MOCK EMAIL SENT TO {to}: {subject}")

def send_verification_email(to_email: str, token: str, subdominio: str):
    # En desarrollo local la URL del front suele ser localhost, pero usamos el mock URL
    link = f"http://localhost:5173/verificar/{token}"
    body = f"Hola,\nPara verificar tu cuenta en Printly ({subdominio}), hace click en este link:\n{link}\nSi no solicitaste esto, ignora el mensaje."
    _log_email("Verifica tu cuenta de Printly", to_email, body)

def send_status_update_email(to_email: str, nombre: str, codigo_pedido: str, nuevo_estado: str, subdominio: str):
    estados_print = {
        'en_cola': 'ha sido ingresado a la cola de impresión',
        'imprimiendo': 'se está imprimiendo',
        'listo': 'ya está LISTO para retirar',
        'entregado': 'fue entregado con éxito'
    }
    
    estado_texto = estados_print.get(nuevo_estado)
    if not estado_texto:
        return # Solo mandamos para estados relevantes
        
    body = f"Hola {nombre},\nTu pedido {codigo_pedido} en {subdominio} {estado_texto}.\nGracias por usar Printly!"
    _log_email(f"Actualización de Pedido: {codigo_pedido}", to_email, body)
