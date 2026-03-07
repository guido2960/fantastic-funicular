import os
import hashlib
import psycopg2
from flask import request, render_template, session, redirect, url_for

# --- 1. CREDENCIALES ---
USUARIO_ACCESO = "maydaycookingamor@gmail.com" 
CLAVE_ACCESO = "cariño241125"
PIN_ADMIN = "2601" 

# --- 2. HERRAMIENTAS DE SEGURIDAD ---
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def obtener_huella(request):
    huella_cruda = f"{request.user_agent.string}{request.remote_addr}"
    return hashlib.sha256(huella_cruda.encode()).hexdigest()

# --- 3. LÓGICA DEL PORTERO ---
def portero_seguridad_logic():
    rutas_libres = ['login', 'verificar', 'static', 'registro_jefe', 'check_autorizacion', 'sala_espera', 'reinstalar']
    if request.endpoint in rutas_libres or request.path.startswith('/static'):
        return None

    huella = obtener_huella(request)
    conn = get_db_connection()
    if not conn: return 
    
    cur = conn.cursor()
    cur.execute("SELECT autorizado, es_admin FROM autorizaciones WHERE dispositivo_id = %s", (huella,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if not usuario or (not usuario[0] and not usuario[1]):
        if not usuario:
            agente = request.user_agent.platform or "Desconocido"
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO autorizaciones (dispositivo_id, nombre_equipo) VALUES (%s, %s) ON CONFLICT DO NOTHING", (huella, agente))
            conn.commit()
            cur.close()
            conn.close()
        return render_template('sala_espera.html')
    return None
