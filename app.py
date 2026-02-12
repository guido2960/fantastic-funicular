import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- 1. CONEXIÓN CON LA NUBE (CLOUDINARY) ---
# Ahora usamos os.environ.get para leer lo que configuraste en el panel de Render
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

# --- 2. CONFIGURACIÓN DE SEGURIDAD ---
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "241125"

# IMPORTANTE: En Render, la DB debe estar en /opt/render/project/src/ o usar una DB externa.
# Por ahora, usemos una ruta local persistente si es posible:
DB_PATH = os.path.join(os.getcwd(), 'base_datos_pro.db')

def inicializar_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        con.commit()

# --- 3. RUTAS DE LA APLICACIÓN ---

@app.route('/')
def login():
    return render_template('login.html', saludo="Hola Mayda ❤️‍🩹")

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_uno = request.form.get('codigo', '').strip()
    entrada_dos = request.form.get('codigo_amuleto', '').strip()

    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        inicializar_db()
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
            fotos_db = cursor.fetchall()
        # Asegúrate de que index.html reciba 'fotos'
        return render_template('index.html', fotos=fotos_db, nombre="Mayda")
    return "🔐 Código incorrecto, amor. Inténtalo de nuevo.", 403

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo and archivo.filename != '':
        # Cambiamos res['url'] por res['secure_url'] para que use HTTPS siempre
        res = cloudinary.uploader.upload(archivo)
        url_nube = res['secure_url'] 
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', (url_nube, mensaje))
            con.commit()
            
    # Pequeño tip: después de subir, redirigir a una ruta que recargue la galería 
    # o podrías tener problemas al ver la foto nueva de inmediato.
    return redirect(url_for('login')) 

@app.route('/eliminar/<int:foto_id>', methods=['POST'])
def eliminar(foto_id):
    with sqlite3.connect(DB_PATH) as con:
        con.execute('DELETE FROM galeria WHERE id = ?', (foto_id,))
        con.commit()
    return redirect(url_for('login'))

# --- 4. ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    inicializar_db()
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
