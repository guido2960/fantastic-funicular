import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_)

# --- 1. CONFIGURACIÓN DE LA NUBE (Blindada) ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

# --- 2. SEGURIDAD DE NUESTRA HISTORIA ---
# Cambiamos lo feo por "Acceso" y "Legado"
USUARIO_ACCESO = "maydaycooking@amor.com" 
CLAVE_LEGADO = "260126" # Tu fecha de compromiso (El Amuleto)
DB_PATH = os.path.join(os.getcwd(), 'boveda_eterna.db') # Nombre más bonito

def inicializar_boveda():
    """Crea el cofre de recuerdos con nombre positivo"""
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS recuerdos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,
            detalle TEXT,
            momento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        con.commit()

# --- 3. RUTAS DE ACCESO ---

@app.route('/')
def portal():
    # Saludo con tu esencia Abel
    mensaje_bienvenida = "¡Feliz San Valentín, mi Mayda! ❤️ Pon la cuenta y la clave pues amor, para que entres a nuestra Bóveda. ¡Te amo! 🥰"
    return render_template('login.html', saludo=mensaje_bienvenida)

@app.route('/entrar', methods=['POST'])
def verificar_acceso():
    # Todo con nombres claros y profesionales
    correo = request.form.get('correo', '').strip()
    clave = request.form.get('clave', '').strip()

    if correo == USUARIO_ACCESO and clave == CLAVE_LEGADO:
        inicializar_boveda()
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, detalle, id FROM recuerdos ORDER BY id DESC')
            recuerdos_db = cursor.fetchall()
        return render_template('index.html', recuerdos=recuerdos_db, nombre="Mayda")
    
    return "🔐 Acceso denegado. ¡Revisa bien los datos, mi amor mayda!", 403

# --- 4. GESTIÓN DE RECUERDOS ---

@app.route('/guardar', methods=['POST'])
def guardar_recuerdo():
    archivo = request.files.get('foto_usuario')
    detalle = request.form.get('detalle_usuario', '') 
    if archivo and archivo.filename != '':
        res = cloudinary.uploader.upload(archivo)
        url_nube = res['secure_url'] 
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO recuerdos (archivo, detalle) VALUES (?, ?)', (url_nube, detalle))
            con.commit()
    return redirect(url_for('portal')) 

if _name_ == '_main_':
    inicializar_boveda()
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
