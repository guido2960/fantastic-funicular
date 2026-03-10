import os
import hashlib
import psycopg2
import cloudinary
import cloudinary.uploader
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__, static_folder='static', static_url_path='/static')
# Clave para cifrar las sesiones de usuario
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'llave_secreta_para_sesiones_2601')

# --- 0. NOTIFICACIONES DE LA BÓVEDA ---
def avisar_boveda(evento, detalle=""):
    # Token de tu bot de Telegram
    token = "8666843380:AAHg4pZhiaz62orVcQUw1cdLSaZX5-Ijqt0"
    # Recuerda poner tu ID real aquí (puedes obtenerlo de @userinfobot)
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', 'TU_ID_AQUI') 
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    ahora = datetime.now().strftime('%H:%M')
    
    mensaje = (
        f"🔐 *[Bóveda Digital]*\n"
        f"────────────────\n"
        f"🔹 *Evento:* {evento}\n"
    )
    if detalle:
        mensaje += f"📝 *Detalle:* {detalle}\n"
    mensaje += f"⏰ *Hora:* {ahora}"
    
    try:
        requests.post(url, data={'chat_id': chat_id, 'text': mensaje, 'parse_mode': 'Markdown'}, timeout=5)
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

# --- 1. CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

# --- 2. SEGURIDAD Y HERRAMIENTAS ---
USUARIO_ACCESO = "maydaycookingamor@gmail.com" 
CLAVE_ACCESO = "cariño241125"
PIN_ADMIN = "2601" 

def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"❌ Error de conexión DB: {e}")
        return None

def obtener_huella(request):
    # Genera un ID único para cada dispositivo (PC, Móvil, etc)
    huella_cruda = f"{request.user_agent.string}{request.remote_addr}"
    return hashlib.sha256(huella_cruda.encode()).hexdigest()

def inicializar_db():
    conn = get_db_connection()
    if conn:
        print("🛠️ Verificando infraestructura de datos...")
        cur = conn.cursor()
        # Galería para tus videos de skate y fotos
        cur.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id SERIAL PRIMARY KEY, archivo TEXT NOT NULL, mensaje TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Notas y mensajes privados
        cur.execute('''CREATE TABLE IF NOT EXISTS notas_amor (
            id SERIAL PRIMARY KEY, contenido TEXT NOT NULL, autor TEXT NOT NULL, categoria TEXT DEFAULT 'General', fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        # Control de acceso por dispositivo
        cur.execute('''CREATE TABLE IF NOT EXISTS autorizaciones (
            id SERIAL PRIMARY KEY, dispositivo_id TEXT UNIQUE, nombre_equipo TEXT, autorizado BOOLEAN DEFAULT FALSE, es_admin BOOLEAN DEFAULT FALSE
        )''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Sistema listo para operar.")

# Ejecutamos la inicialización al arrancar
inicializar_db()

# --- 3. EL PORTERO (MIDDLEWARE DE SEGURIDAD) ---
@app.before_request
def portero_seguridad():
    # Rutas que no necesitan estar autorizadas para cargar
    rutas_libres = ['login', 'verificar', 'static', 'registro_jefe', 'sala_espera', 'reinstalar']
    if request.endpoint in rutas_libres or request.path.startswith('/static'):
        return

    huella = obtener_huella(request)
    conn = get_db_connection()
    if not conn: return 
    
    cur = conn.cursor()
    cur.execute("SELECT autorizado, es_admin FROM autorizaciones WHERE dispositivo_id = %s", (huella,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if not usuario or (not usuario[0] and not usuario[1]):
        if not usuario:
            # Si es la primera vez que entra este dispositivo, lo registramos como "bloqueado"
            agente = request.user_agent.platform or "Desconocido"
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO autorizaciones (dispositivo_id, nombre_equipo) VALUES (%s, %s) ON CONFLICT DO NOTHING", (huella, agente))
            conn.commit()
            cur.close()
            conn.close()
            avisar_boveda("🚨 Alerta de Acceso", f"Nuevo dispositivo intentando entrar: {agente}")
        return render_template('sala_espera.html')

# --- 4. RUTAS DE MANDO (ADMINISTRACIÓN) ---

@app.route('/norte-maestro')
def registro_jefe():
    # Esta ruta te da permisos de Admin a TI automáticamente al visitarla
    huella = obtener_huella(request)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO autorizaciones (dispositivo_id, nombre_equipo, autorizado, es_admin)
        VALUES (%s, 'Mando Principal (Abel)', True, True)
        ON CONFLICT (dispositivo_id) DO UPDATE SET es_admin = True, autorizado = True
    """, (huella,))
    conn.commit()
    cur.close()
    conn.close()
    avisar_boveda("Admin Online", "Has tomado el mando desde tu dispositivo actual.")
    return redirect(url_for('dashboard_norte'))

@app.route('/dashboard-norte')
def dashboard_norte():
    # Tu panel de control privado
    huella = obtener_huella(request)
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT es_admin FROM autorizaciones WHERE dispositivo_id = %s", (huella,))
    es_jefe = cur.fetchone()
    if not es_jefe or not es_jefe[0]:
        cur.close()
        conn.close()
        return "Acceso Denegado", 403

    # Obtener métricas reales para el dashboard.html
    cur.execute("SELECT COUNT(*) FROM galeria")
    total_fotos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM notas_amor")
    total_notas = cur.fetchone()[0]
    cur.execute("SELECT id, nombre_equipo, autorizado FROM autorizaciones WHERE es_admin = False")
    dispositivos = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('dashboard.html', fotos=total_fotos, notas=total_notas, lista=dispositivos)

@app.route('/autorizar_dispositivo/<int:id>')
def autorizar_dispositivo(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE autorizaciones SET autorizado = True WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    avisar_boveda("Autorización", f"Dispositivo ID {id} ha sido permitido.")
    return redirect(url_for('dashboard_norte'))

# --- 5. RUTAS DE LA EXPERIENCIA ---

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    email = request.form.get('correo', '').strip()
    clave = request.form.get('clave', '').strip()
    if email == USUARIO_ACCESO and clave == CLAVE_ACCESO:
        session['user_email'] = email
        avisar_boveda("Acceso Exitoso", "Se han validado las credenciales de entrada.")
        return render_template('intro.html')
    
    avisar_boveda("⚠️ Fallo de Login", f"Intento con: {email}")
    return "🔐 Acceso denegado.", 403

@app.route('/boveda')
def boveda():
    if 'user_email' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
    fotos = cur.fetchall()
    cur.execute("SELECT autor, contenido, TO_CHAR(fecha, 'DD/MM HH:MI AM'), categoria, id FROM notas_amor ORDER BY fecha DESC")
    notas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', fotos=fotos, notas=notas)

# --- 6. GESTIÓN DE CONTENIDO ---

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario', '') 
    if archivo:
        # Subida directa a Cloudinary
        res = cloudinary.uploader.upload(archivo)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO galeria (archivo, mensaje) VALUES (%s, %s)', (res['secure_url'], mensaje))
        conn.commit()
        cur.close()
        conn.close()
        avisar_boveda("Nuevo Contenido", f"Se añadió un recuerdo: {mensaje}")
    return redirect(url_for('boveda'))

@app.route('/nueva_nota', methods=['POST'])
def nueva_nota():
    autor = request.form.get('autor_nombre')
    contenido = request.form.get('contenido_nota')
    if contenido and autor:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO notas_amor (autor, contenido) VALUES (%s, %s)', (autor, contenido))
        conn.commit()
        cur.close()
        conn.close()
        avisar_boveda("Nota Creada", f"De {autor}: {contenido[:25]}...")
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

# --- 7. ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    # Render asigna el puerto dinámicamente
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
