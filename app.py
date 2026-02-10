import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# CONFIGURACIÓN DE SEGURIDAD PARA MAYDA ❤️
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "2411" # Tu amuleto [cite: 2026-01-27]

# CORRECCIÓN PARA RENDER: Usamos os.getcwd() en lugar de _file_
BASE_DIR = os.getcwd() 
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'fotos')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que las carpetas existan
if not os.path.exists(UPLOAD_FOLDER):
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
        # Aquí pasamos el nombre de tu prometida
        return render_template('index.html', fotos=fotos, nombre="Mayda")
    else:
        return "🔐 Acceso denegado. Inténtalo de nuevo, amor.", 403

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo and archivo.filename != '':
        nombre_archivo = archivo.filename
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', 
                        (nombre_archivo, mensaje))
            
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
