import os
from flask import Flask, render_template, session, redirect, url_for
from SISTEMA_BOVEDA_PRO.database import get_db_connection

app = Flask(_name_, static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'llave_secreta_2601')

# --- ESTO ES LO QUE CONECTA LA FUNCIÓN CON LA URL ---
@app.route('/boveda')
def mostrar_boveda():
    """Carga todas las fotos y notas de la base de datos para mostrarlas en la interfaz principal."""
    if 'user_email' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        return "Error de conexión con la base de datos", 500

    cur = conn.cursor()
    
    # Obtener fotos
    cur.execute("SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC")
    fotos = cur.fetchall()

    # Obtener notas
    cur.execute("""
        SELECT autor, contenido, TO_CHAR(fecha, 'DD/MM HH:MI AM'), categoria, id 
        FROM notas_amor 
        ORDER BY fecha DESC
    """)
    notas = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', fotos=fotos, notas=notas)

# --- EL MOTOR QUE ENCIENDE TODO ---
if _name_ == '_main_':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
