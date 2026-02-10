import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

# Asegúrate de que sean DOS guiones bajos: _name_
app = Flask(_name_)

# CONFIGURACIÓN DE SEGURIDAD
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "2411"

# RUTAS PARA RENDER
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'fotos')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def inicializar_db():
    """Crea la tabla de recuerdos si no existe"""
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        con.commit()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_uno = request.form.get('codigo', '').strip()
    entrada_dos = request.form.get('codigo_amuleto', '').strip()

    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        inicializar_db()  # Verificamos la tabla al entrar
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, mensaje FROM galeria ORDER BY id DESC')
            fotos_db = cursor.fetchall()
        return render_template('index.html', fotos=fotos_db, nombre="Mayda")
    else:
        return "🔐 Código incorrecto. Inténtalo de nuevo.", 403

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo and archivo.filename != '':
        inicializar_db()  # FUERZA la creación de la tabla antes de guardar
        
        nombre_archivo = archivo.filename
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', 
                        (nombre_archivo, mensaje))
            con.commit()
            
    return redirect(url_for('login'))

if _name_ == '_main_':
    inicializar_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
