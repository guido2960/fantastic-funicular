# SISTEMA_BOVEDA_PRO/seguridad.py
import hashlib
from flask import request, render_template
from SISTEMA_BOVEDA_PRO.acceso import get_db_connection

def obtener_huella(request):
    """Genera una firma única basada en el dispositivo y la IP"""
    huella_cruda = f"{request.user_agent.string}{request.remote_addr}"
    return hashlib.sha256(huella_cruda.encode()).hexdigest()

def portero_seguridad_logic():
    """Lógica que decide si el dispositivo tiene permiso o va a sala de espera"""
    rutas_libres = ['login', 'verificar', 'static', 'registro_jefe', 'check_autorizacion', 'sala_espera', 'reinstalar']
    
    if request.endpoint in rutas_libres or request.path.startswith('/static'):
        return None

    huella = obtener_huella(request)
    conn = get_db_connection()
    if not conn: 
        return None 
    
    cur = conn.cursor()
    cur.execute("SELECT autorizado, es_admin FROM autorizaciones WHERE dispositivo_id = %s", (huella,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    # Si no está registrado o no tiene permisos, se le manda a esperar
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
