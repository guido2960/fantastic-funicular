# SISTEMA_BOVEDA_PRO/admin.py
from flask import render_template, redirect, url_for
from SISTEMA_BOVEDA_PRO.database import get_db_connection, inicializar_db
from SISTEMA_BOVEDA_PRO.seguridad import obtener_huella

def reinstalar_sistema():
    """Refresca las tablas de la base de datos desde cero"""
    inicializar_db()
    return "Base de datos refrescada correctamente."

def registrar_mando_principal(request):
    """Activa el control total (Norte Maestro) para el dispositivo actual"""
    huella = obtener_huella(request)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO autorizaciones (dispositivo_id, nombre_equipo, autorizado, es_admin)
        VALUES (%s, 'Mando Principal (Norte)', True, True)
        ON CONFLICT (dispositivo_id) DO UPDATE SET es_admin = True, autorizado = True
    """, (huella,))
    conn.commit()
    cur.close()
    conn.close()
    return "<h1>¡Identificado!</h1><p>Control total activado.</p><a href='/boveda'>Ir a la Bóveda</a>"

def obtener_panel_admin(request):
    """Obtiene la lista de dispositivos que piden acceso"""
    huella = obtener_huella(request)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT es_admin FROM autorizaciones WHERE dispositivo_id = %s", (huella,))
    es_jefe = cur.fetchone()
    
    if not es_jefe or not es_jefe[0]:
        cur.close()
        conn.close()
        return None # Esto indicará Acceso Denegado
        
    cur.execute("SELECT id, nombre_equipo, autorizado FROM autorizaciones WHERE es_admin = False")
    lista = cur.fetchall()
    cur.close()
    conn.close()
    return lista
