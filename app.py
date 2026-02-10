import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_)

# CONFIGURACIÓN DE SEGURIDAD
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "2411"

# CONFIGURACIÓN DE RUTAS PARA RENDER
BASE_DIR = os.path.abspath(os.path.dirname(_file_))
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/fotos')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que la carpeta de fotos exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def inicializar_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_uno = request.form.get('codigo')
    entrada_dos = request.form.get('codigo_amuleto') 

    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, mensaje FROM galeria ORDER BY id DESC')
            fotos = cursor.fetchall()
        return render_template('index.html', fotos=fotos)
    else:
        return "🔐 Acceso denegado. Revisa tus códigos.", 403

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo and archivo.filename != '':
        nombre_archivo = archivo.filename
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo)
        archivo.save(ruta_guardado)
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', 
                        (nombre_archivo, mensaje))
            
    return redirect(url_for('login'))

if _name_ == '_main_':
    inicializar_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
