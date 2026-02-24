import os
import psycopg2
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_, static_folder='static', static_url_path='/static')

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
    cur.execute('''CREATE TABLE IF NOT EXISTS galeria (
        id SERIAL PRIMARY KEY,
        archivo TEXT NOT NULL,
        mensaje TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
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

# --- 3. RUTAS DE ACCESO ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_email = request.form.get('correo', '').strip()
    entrada_clave = request.form.get('clave', '').strip()
    if entrada_email == USUARIO_ACCESO and entrada_clave == CLAVE_ACCESO:
        return redirect(url_for('boveda'))
    return "🔐 Acceso denegado, intenta de nuevo.", 403

@app.route('/boveda')
def boveda():
    inicializar_db()
    conn = get_db_connection()
    cur = conn.cursor()
    # Fotos
    cur.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
    fotos_db = cur.fetchall()
    
    # Notas: Ahora incluimos el ID al final (índice 4) para que funcionen los botones
    cur.execute("SELECT autor, contenido, TO_CHAR(fecha, 'DD/MM HH:MI AM'), categoria, id FROM notas_amor ORDER BY fecha DESC")
    notas_db = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('index.html', fotos=fotos_db, notas=notas_db)

# --- 4. GESTIÓN DE NOTAS (NUEVO: EDITAR Y ELIMINAR) ---

@app.route('/nueva_nota', methods=['POST'])
def nueva_nota():
    autor = request.form.get('autor_nombre')
    contenido = request.form.get('contenido_nota')
    modo = request.form.get('modo_nota', 'General')
    if contenido and autor:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO notas_amor (autor, contenido, categoria) VALUES (%s, %s, %s)', (autor, contenido, modo))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('boveda')) 

@app.route('/editar_nota/<int:id>', methods=['POST'])
def editar_nota(id):
    nuevo_contenido = request.form.get('contenido_editado')
    if nuevo_contenido:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE notas_amor SET contenido = %s WHERE id = %s', (nuevo_contenido, id))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('boveda'))

@app.route('/eliminar_nota/<int:id>', methods=['POST'])
def eliminar_nota(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM notas_amor WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('boveda'))

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
    return redirect(url_for('boveda')) 

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM galeria WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('boveda'))

@app.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    nuevo_mensaje = request.form.get('mensaje_editado')
    if nuevo_mensaje:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE galeria SET mensaje = %s WHERE id = %s', (nuevo_mensaje, id))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('boveda'))

# --- 6. EJECUCIÓN ---

if __name__ == '__main__':
    inicializar_db()
    puerto = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=puerto)
