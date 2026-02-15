import os
import psycopg2
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- 1. CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

# --- 2. SEGURIDAD ---
USUARIO_ACCESO = "maydaycookingamor@gmail.com" 
CLAVE_ACCESO = "cariño241125"

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(url)

def inicializar_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Tabla para fotos
    cur.execute('''CREATE TABLE IF NOT EXISTS galeria (
        id SERIAL PRIMARY KEY,
        archivo TEXT NOT NULL,
        mensaje TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Tabla para notas (Añadida la columna 'categoria' para evitar el Error 500)
    cur.execute('''CREATE TABLE IF NOT EXISTS notas_amor (
        id SERIAL PRIMARY KEY,
        contenido TEXT NOT NULL,
        autor TEXT NOT NULL,
        categoria TEXT DEFAULT 'General',
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    cur.close()
    conn.close()

# --- 3. RUTAS ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_email = request.form.get('correo', '').strip()
    entrada_clave = request.form.get('clave', '').strip()

    if entrada_email == USUARIO_ACCESO and entrada_clave == CLAVE_ACCESO:
        inicializar_db()
        conn = get_db_connection()
        cur = conn.cursor()
        # Traer fotos
        cur.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
        fotos_db = cur.fetchall()
        # Traer notas con el formato de fecha y autor
        cur.execute("SELECT autor, contenido, TO_CHAR(fecha, 'DD/MM HH:MI AM'), categoria FROM notas_amor ORDER BY fecha ASC")
        notas_db = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', fotos=fotos_db, notas=notas_db)
    
    return "🔐 Acceso denegado, intenta de nuevo.", 403

# --- 4. GUARDAR NOTAS (EL CHAT CORREGIDO) ---

@app.route('/nueva_nota', methods=['POST'])
def nueva_nota():
    autor = request.form.get('autor_nombre')
    contenido = request.form.get('contenido_nota')

    # Lógica para asignar categoría según el autor
    if autor and ("Abel" in autor or "Norte" in autor):
        categoria = "Norte"
    else:
        categoria = "May"

    if contenido and autor:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # AGREGAMOS 'categoria' en el INSERT para que la DB no de error
            cur.execute(
                'INSERT INTO notas_amor (autor, contenido, categoria) VALUES (%s, %s, %s)', 
                (autor, contenido, categoria)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error al guardar nota: {e}")
            return f"Error en el servidor: {e}", 500
    
    return redirect(url_for('login')) 

# --- 5. GESTIÓN DE FOTOS ---

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

if __name__ == '__main__':
    inicializar_db()
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0
