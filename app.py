import os
import hashlib
import psycopg2
import cloudinary
import cloudinary.uploader
import requests  # Para las notificaciones de Telegram
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(_name_, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'llave_secreta_para_sesiones_2601')

# --- 1. CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config( 
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
    api_key = os.environ.get('CLOUDINARY_API_KEY'), 
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

# --- 2. SEGURIDAD, HERRAMIENTAS Y NOTIFICACIONES ---
USUARIO_ACCESO = "maydaycookingamor@gmail.com" 
CLAVE_ACCESO = "cariño241125"
PIN_ADMIN = "2601" 

def avisar_boveda(evento, detalle=""):
    """Función para que el Norte reciba alertas en Telegram"""
    token = "8666843380:AAHg4pZhiaz62orVcQUw1cdLSaZX5-Ijqt0"
    chat_id = "7595418604" # ID de Telegram de Abel
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    ahora = datetime.now().strftime('%H:%M')
    mensaje = (
        f"🔐 [Bóveda Digital]\n"
        f"────────────────\n"
        f"🔹 Evento: {evento}\n"
        f"📝 Detalle: {detalle}\n"
        f"⏰ Hora: {ahora}"
    )
    try:
        requests.post(url, data={'chat_id': chat_id, 'text': mensaje, 'parse_mode': 'Markdown'}, timeout=5)
    except Exception as e:
        print(f"Error de red en Telegram: {e}")

def get_db_connection():
    """Conexión adaptada para la URL Externa de Render"""
    url = os.environ.get('DATABASE_URL')
    if not url:
        print("❌ Error: No se detectó DATABASE_URL")
        return None
    try:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def obtener_huella(request):
    huella_cruda = f"{request.user_agent.string}{request.remote_addr}"
    return hashlib.sha256(huella_cruda.encode()).hexdigest()

def inicializar_db():
    conn = get_db_connection()
    if conn:
        print("🛠️ Inicializando tablas...")
        try:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS galeria (
                id SERIAL PRIMARY KEY, archivo TEXT NOT NULL, mensaje TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS notas_amor (
                id SERIAL PRIMARY KEY, contenido TEXT NOT NULL, autor TEXT NOT NULL, categoria TEXT DEFAULT 'General', fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS control_seguridad (
                id SERIAL PRIMARY KEY, session_version INTEGER DEFAULT 1
            )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS autorizaciones (
                id SERIAL PRIMARY KEY, dispositivo_id TEXT UNIQUE, nombre_equipo TEXT, autorizado BOOLEAN DEFAULT FALSE, es_admin BOOLEAN DEFAULT FALSE
            )''')
            cur.execute("INSERT INTO control_seguridad (id, session_version) SELECT 1, 1 WHERE NOT EXISTS (SELECT 1 FROM control_seguridad WHERE id = 1)")
            conn.commit()
            cur.close()
            print("✅ Tablas verificadas/creadas.")
        except Exception as e:
            print(f"⚠️ Error en inicialización: {e}")
        finally:
            conn.close()

inicializar_db()

# --- 3. EL PORTERO (CORREGIDO PARA EVITAR EL ERROR 502) ---
@app.before_request
def portero_seguridad():
    rutas_libres = ['login', 'verificar', 'static', 'registro_jefe', 'check_autorizacion', 'sala_espera', 'reinstalar', 'cerrar_todo']
    if request.endpoint in rutas_libres or (request.path and request.path.startswith('/static')):
        return

    # CORRECCIÓN CLAVE: Si ya hay sesión iniciada, NO revisamos la base de datos.
    # Esto evita el lag y el error 502 al saltar del Login al Intro.
    if 'user_email' in session:
        return

    huella = obtener_huella(request)
    conn = get_db_connection()
    if not conn: 
        return 
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT autorizado, es_admin FROM autorizaciones WHERE dispositivo_id = %s", (huella,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        if not usuario or (not usuario[0] and not usuario[1]):
            if not usuario:
                agente = request.user_agent.platform or "Desconocido"
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO autorizaciones (dispositivo_id, nombre_equipo) VALUES (%s, %s) ON CONFLICT DO NOTHING", (huella, agente))
                conn.commit()
                cur.close()
                conn.close()
            return render_template('sala_espera.html')
    except Exception as e:
        print(f"Error en portero: {e}")

# --- 4. RUTAS DE MANDO (DASHBOARD Y CONTROL) ---
@app.route('/reinstalar')
def reinstalar():
    inicializar_db()
    avisar_boveda("Sistema", "Se ha refrescado la base de datos.")
    return "Base de datos refrescada correctamente."

@app.route('/norte-maestro')
def registro_jefe():
    huella = obtener_huella(request)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO autorizaciones (dispositivo_id, nombre_equipo, autorizado, es_admin)
        VALUES (%s, 'Mando Principal (Norte)', True, True)
        ON CONFLICT (dispositivo_id) DO UPDATE SET es_admin = True, autorizado = True
    """, (huella,))
    conn.commit()
    cur.close()
    conn.close()
    avisar_boveda("Acceso Maestro", "El Norte ha tomado el control total del panel.")
    return redirect(url_for('dashboard_norte'))

@app.route('/dashboard-norte')
def dashboard_norte():
    huella = obtener_huella(request)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT es_admin FROM autorizaciones WHERE dispositivo_id = %s", (huella,))
    es_jefe = cur.fetchone()
    if not es_jefe or not es_jefe[0]:
        cur.close()
        conn.close()
        return "Acceso Denegado", 403

    cur.execute("SELECT COUNT(*) FROM galeria")
    total_fotos = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM notas_amor")
    total_notas = cur.fetchone()[0]

    cur.execute("SELECT id, nombre_equipo, autorizado FROM autorizaciones WHERE es_admin = False")
    lista = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('dashboard.html', total_multimedia=total_fotos, total_notas=total_notas, lista=lista)

@app.route('/cerrar-todo')
def cerrar_todo():
    session.clear()
    avisar_boveda("⚠️ BOTÓN DE PÁNICO", "Se ha cerrado la sesión.")
    return redirect(url_for('login'))

@app.route('/autorizar_dispositivo/<int:id>')
def autorizar_dispositivo(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE autorizaciones SET autorizado = True WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    avisar_boveda("Seguridad", f"Se ha autorizado manualmente al dispositivo con ID: {id}")
    return redirect(url_for('dashboard_norte'))

# --- 5. RUTAS DE LA EXPERIENCIA ---
@app.route('/intro')
def intro():
    if 'user_email' not in session: 
        return redirect(url_for('login'))
    return render_template('intro.html')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_email = request.form.get('correo', '').strip()
    entrada_clave = request.form.get('clave', '').strip()
    if entrada_email == USUARIO_ACCESO and entrada_clave == CLAVE_ACCESO:
        session['user_email'] = entrada_email
        
        # AUTO-AUTORIZACIÓN: Para que al poner la clave, no te bloquee después.
        try:
            huella = obtener_huella(request)
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO autorizaciones (dispositivo_id, nombre_equipo, autorizado)
                    VALUES (%s, %s, True)
                    ON CONFLICT (dispositivo_id) DO UPDATE SET autorizado = True
                """, (huella, f"Acceso Validado ({request.user_agent.platform})"))
                conn.commit()
                cur.close()
                conn.close()
        except:
            pass

        avisar_boveda("Login", "Mayda o Abel han entrado.")
        return redirect(url_for('intro'))
    
    avisar_boveda("⚠️ Intento Fallido", f"Correo: {entrada_email}")
    return "🔐 Acceso denegado.", 403

@app.route('/boveda')
def boveda():
    if 'user_email' not in session: 
        return redirect(url_for('login'))
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
        avisar_boveda("Nota Nueva", f"Se ha escrito un mensaje.")
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

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario', '') 
    if archivo:
        res = cloudinary.uploader.upload(archivo)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO galeria (archivo, mensaje) VALUES (%s, %s)', (res['secure_url'], mensaje))
        conn.commit()
        cur.close()
        conn.close()
        avisar_boveda("Recuerdo Nuevo", "Se ha subido una foto.")
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

# --- 7. EL ARREGLO FINAL ---
if _name_ == '_main_':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
