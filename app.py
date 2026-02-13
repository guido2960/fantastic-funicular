import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- 1. CONFIGURACIÓN DE LA NUBE (Blindada) ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

# --- 2. SEGURIDAD DE NUESTRA HISTORIA ---
# Incluimos los accesos que definimos sin tocar tu estructura
USUARIO_ACCESO = "maydaycooking@amor.com" 
CLAVE_ACCESO = "260126" # Tu fecha de compromiso (El Amuleto)
DB_PATH = os.path.join(os.getcwd(), 'base_datos_pro.db')

def inicializar_db():
    """Crea el cofre de recuerdos si no existe"""
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        con.commit()

# --- 3. RUTAS DE ACCESO ---

@app.route('/')
def login():
    # Tu saludo personalizado
    return render_template('login.html', saludo="¡Feliz San Valentín, mi Mayda! ❤️ Ingresa nuestra cuenta y clave para entrar a la Bóveda Privada. ¡Te amo! 🥰")

@app.route('/verificar', methods=['POST'])
def verificar():
    # Conectamos con los nombres que usa tu HTML
    entrada_email = request.form.get('correo', '').strip()
    entrada_clave = request.form.get('clave', '').strip()

    if entrada_email == USUARIO_ACCESO and entrada_clave == CLAVE_ACCESO:
        inicializar_db()
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
            fotos_db = cursor.fetchall()
        return render_template('index.html', fotos=fotos_db, nombre="Mayda")
    
    return "🔐 Acceso denegado. ¡Revisa bien los datos, amor!", 403

# --- 4. GESTIÓN DE RECUERDOS (Tu código intacto) ---

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario', '') 
    if archivo and archivo.filename != '':
        res = cloudinary.uploader.upload(archivo)
        url_nube = res['secure_url'] 
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', (url_nube, mensaje))
            con.commit()
    return redirect(url_for('login')) 

@app.route('/eliminar/<int:foto_id>', methods=['POST'])
def eliminar(foto_id):
    with sqlite3.connect(DB_PATH) as con:
        con.execute('DELETE FROM galeria WHERE id = ?', (foto_id,))
        con.commit()
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_db()
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
