import os
import sqlite3
import cloudinary
import cloudinary.uploader  # Solo añadimos esta herramienta
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- CONFIGURACIÓN CLOUDINARY (Tu almacén seguro) ---
cloudinary.config( 
  cloud_name = "dvmz2v0zvr", 
  api_key = "297853115656242", 
  api_secret = "TU_API_SECRET_AQUÍ" # Coloca el que viste con el ojo
)

# CONFIGURACIÓN DE SEGURIDAD (Se mantiene igual)
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "241125"

# RUTAS DE ARCHIVOS
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')

# Ya no necesitamos UPLOAD_FOLDER porque la nube es nuestra carpeta

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
    saludo_personalizado = "Hola Mayda ❤️‍🩹"
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
        # INCLUSIÓN SUAVE: En lugar de guardar en el disco de Render, 
        # lo mandamos a Cloudinary y guardamos ese link.
        resultado = cloudinary.uploader.upload(archivo)
        url_foto = resultado['url'] 
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', (url_foto, mensaje))
            con.commit()
    return redirect(url_for('login'))

@app.route('/eliminar/<int:foto_id>', methods=['POST'])
def eliminar(foto_id):
    with sqlite3.connect(DB_PATH) as con:
        con.execute('DELETE FROM galeria WHERE id = ?', (foto_id,))
        con.commit()
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
