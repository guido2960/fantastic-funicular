import os
import psycopg2  # CAMBIO: Usamos PostgreSQL para que no se borre nada
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
USUARIO_ACCESO = "maydaycookingamor@gmail.com" 
CLAVE_ACCESO = "cariño241125" # Tu fecha de compromiso (El Amuleto)

def get_db_connection():
    # Conexión a la base de datos "recuerdos" que te aprobaron
    url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(url)

def inicializar_db():
    """Crea el cofre de recuerdos eterno si no existe"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS galeria (
        id SERIAL PRIMARY KEY,
        archivo TEXT NOT NULL,
        mensaje TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    cur.close()
    conn.close()

# --- 3. RUTAS DE ACCESO ---

@app.route('/')
def login():
    return render_template('login.html', saludo="¡Feliz San Valentín,Mi Mayda!he construido este refugio digital para que solo nosotros seamos testigos de nuestra historia. ¡te amo!🥰")

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_email = request.form.get('correo', '').strip()
    entrada_clave = request.form.get('clave', '').strip()

    if entrada_email == USUARIO_ACCESO and entrada_clave == CLAVE_ACCESO:
        inicializar_db()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
        fotos_db = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', fotos=fotos_db, nombre="Mayda")
    
    return "🔐 Acceso denegado. ¡Revisa bien los datos, amor!", 403

# --- 4. GESTIÓN DE RECUERDOS (Conectado a la Nueva Base) ---

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario', '') 
    if archivo and archivo.filename != '':
        res = cloudinary.uploader.upload(archivo)
        url_nube = res['secure_url'] 
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO galeria (archivo, mensaje) VALUES (%s, %s)', (url_nube, mensaje))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('login')) 

@app.route('/eliminar/<int:foto_id>', methods=['POST'])
def eliminar(foto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM galeria WHERE id = %s', (foto_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_db()
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
