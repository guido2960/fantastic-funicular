import os  # Corregido: import en minúscula
import psycopg2
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'llave_secreta_para_sesiones_2601')

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
PIN_ADMIN = "2601" 

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    # Agregamos un try básico para que la app no muera si la URL falla un segundo
    try:
        return psycopg2.connect(url)
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def inicializar_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        # Tus tablas originales
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
        # NUEVA TABLA: Control Maestro de Sesiones
        cur.execute('''CREATE TABLE IF NOT EXISTS control_seguridad (
            id SERIAL PRIMARY KEY,
            session_version INTEGER DEFAULT 1
        )''')
        # Insertar versión inicial si no existe
        cur.execute("INSERT INTO control_seguridad (id, session_version) SELECT 1, 1 WHERE NOT EXISTS (SELECT 1 FROM control_seguridad WHERE id = 1)")
        
        conn.commit()
        cur.close()
        conn.close()

# --- 3. RUTAS DE ACCESO Y SEGURIDAD ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_email = request.form.get('correo', '').strip()
    entrada_clave = request.form.get('clave', '').strip()
    
    if entrada_email == USUARIO_ACCESO and entrada_clave == CLAVE_ACCESO:
        # EXPERIENCIA: Alerta de IP
        user_ip = request.remote_addr
        print(f"✅ ALERTA: Acceso de {entrada_email} desde IP: {user_ip} - ¡Ya entró, tranquilo!")

        # Obtener versión de sesión actual
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT session_version FROM control_seguridad WHERE id = 1')
        row = cur.fetchone()
        version = row[0] if row else 1
        cur.close()
        conn.close()

        # EXPERIENCIA: Prioridad Maestro
        session['user_email'] = entrada_email
        session['session_version'] = version
        return redirect(url_for('boveda'))
    
    return "🔐 Acceso denegado, intenta de nuevo.", 403

# EXPERIENCIA: Latido de Seguridad (Polling)
@app.route('/check_session')
def check_session():
    if 'user_email' not in session:
        return jsonify({"status": "expired"}), 401
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT session_version FROM control_seguridad WHERE id = 1')
    version_actual = cur.fetchone()[0]
    cur.close()
    conn.close()

    if session.get('session_version') != version_actual:
        session.clear()
        return jsonify({"status": "expired"}), 401
    return jsonify({"status": "ok"}), 200

# EXPERIENCIA: El Interruptor Maestro (Cierre Global)
@app.route('/cierre_global', methods=['POST'])
def cierre_global():
    pin_ingresado = request.form.get('pin_admin')
    if pin_ingresado == PIN_ADMIN:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE control_seguridad SET session_version = session_version + 1 WHERE id = 1')
        conn.commit()
        cur.close()
        conn.close()
        session.clear() 
        print("🚨 CIERRE GLOBAL EJECUTADO: Todos los dispositivos expulsados.")
        return redirect(url_for('login'))
    return "PIN Incorrecto", 403

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/boveda')
def boveda():
    # Verificación de sesión
    if 'user_email' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
    fotos_db = cur.fetchall()
    cur.execute("SELECT autor, contenido, TO_CHAR(fecha, 'DD/MM HH:MI AM'), categoria, id FROM notas_amor ORDER BY fecha DESC")
    notas_db = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', fotos=fotos_db, notas=notas_db)

# --- 4. GESTIÓN DE NOTAS ---

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
