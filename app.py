import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_)

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Usa siempre minúsculas para evitar errores al escribir en el celular
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "2411" 

# --- CONFIGURACIÓN DE RUTAS UNIVERSALES ---
# 'os.getcwd()' funciona en cualquier servidor (Windows, Linux, Render)
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')
# Ruta para las fotos: 'static/uploads/fotos'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'fotos')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear las carpetas de fotos automáticamente si no existen
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def inicializar_db():
    """Crea la tabla si no existe al arrancar el servidor"""
    try:
        with sqlite3.connect(DB_PATH) as con:
            con.execute('''CREATE TABLE IF NOT EXISTS galeria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                archivo TEXT NOT NULL,
                mensaje TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
    except Exception as e:
        print(f"Error al iniciar DB: {e}")

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    # Obtenemos los datos del formulario
    entrada_uno = request.form.get('codigo', '').lower().strip()
    entrada_dos = request.form.get('codigo_amuleto', '').strip()

    # Validación exacta
    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        try:
            with sqlite3.connect(DB_PATH) as con:
                cursor = con.cursor()
                cursor.execute('SELECT archivo, mensaje FROM galeria ORDER BY id DESC')
                fotos_db = cursor.fetchall()
            return render_template('index.html', fotos=fotos_db, nombre="Mayda")
        except:
            # Si la base de datos falla, cargamos la página vacía pero entramos
            return render_template('index.html', fotos=[], nombre="Mayda")
    else:
        return "🔐 Código incorrecto. Inténtalo de nuevo, amor.", 403

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo and archivo.filename != '':
        nombre_archivo = archivo.filename
        ruta_completa = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo.save(ruta_completa)
        
        try:
            with sqlite3.connect(DB_PATH) as con:
                con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', 
                            (nombre_archivo, mensaje))
        except Exception as e:
            print(f"Error al guardar en DB: {e}")
            
    return redirect(url_for('login'))

if _name_ == '_main_':
    inicializar_db()
    # Configuración para que el servidor encuentre el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
