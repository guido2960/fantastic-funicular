# SISTEMA_BOVEDA_PRO/boveda_main.py
from flask import render_template, session, redirect, url_for
from SISTEMA_BOVEDA_PRO.database import get_db_connection

def mostrar_boveda():
    """
    Carga todas las fotos y notas de la base de datos 
    para mostrarlas en la interfaz principal.
    """
    if 'user_email' not in session: 
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    if not conn:
        return "Error de conexión con la base de datos", 500
        
    cur = conn.cursor()
    
    # Obtener fotos de la galería
    cur.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
    fotos = cur.fetchall()
    
    # Obtener notas de amor con formato de fecha
    cur.execute("""
        SELECT autor, contenido, TO_CHAR(fecha, 'DD/MM HH:MI AM'), categoria, id 
        FROM notas_amor 
        ORDER BY fecha DESC
    """)
    notas = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', fotos=fotos, notas=notas)
