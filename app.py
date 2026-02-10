import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# CONFIGURACIÓN DE SEGURIDAD
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "241125"

# RUTAS DE ARCHIVOS
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'fotos')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def inicializar_db():
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
    # Aquí configuramos tu saludo especial
    saludo_personalizado = "Hola amorcito Mayda 🫂❤️‍🩹"
    return render_template('login.html', saludo=saludo_personalizado)

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada_uno = request.form.get('codigo', '').strip()
    entrada_dos = request.form.get('codigo_amuleto', '').strip()

    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        inicializar_db()
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
            fotos_db = cursor.fetchall()
        return render_template('index.html', fotos=fotos_db, nombre="Mayda")
    else:
        return "🔐 Código incorrecto. Inténtalo de nuevo.", 403

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    if archivo and archivo.filename != '':
        nombre_archivo = archivo.filename
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', (nombre_archivo, mensaje))
            con.commit()
    return redirect(url_for('login'))

@app.route('/eliminar/<int:foto_id>', methods=['POST'])
def eliminar(foto_id):
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute('SELECT archivo FROM galeria WHERE id = ?', (foto_id,))
        foto = cursor.fetchone()
        if foto:
            ruta_foto = os.path.join(app.config['UPLOAD_FOLDER'], foto[0])
            if os.path.exists(ruta_foto):
                os.remove(ruta_foto)
            con.execute('DELETE FROM galeria WHERE id = ?', (foto_id,))
            con.commit()
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
