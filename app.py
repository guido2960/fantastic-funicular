import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- CONFIGURACIÓN ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)
DB_PATH = os.path.join(os.getcwd(), 'base_datos_pro.db')

def inicializar_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        con.commit()

# --- RUTAS ---
@app.route('/')
def login():
    return render_template('login.html', saludo="Hola Mayda ❤️‍🩹")

@app.route('/verificar', methods=['POST'])
def verificar():
    # Usa tus códigos: amor123 y 241125
    inicializar_db()
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
        fotos_db = cursor.fetchall()
    return render_template('index.html', fotos=fotos_db, nombre="Mayda")

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    if archivo:
        res = cloudinary.uploader.upload(archivo)
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', (res['secure_url'], "Escribe algo lindo..."))
            con.commit()
    return redirect(url_for('login'))

# NUEVA RUTA PARA INTERACTUAR EN CADA FOTO
@app.route('/comentar', methods=['POST'])
def comentar():
    foto_id = request.form.get('foto_id')
    nuevo_mensaje = request.form.get('nuevo_mensaje')
    with sqlite3.connect(DB_PATH) as con:
        con.execute('UPDATE galeria SET mensaje = ? WHERE id = ?', (nuevo_mensaje, foto_id))
        con.commit()
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
