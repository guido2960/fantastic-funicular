import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(_name_)

# --- CONFIGURACIÓN DE CLOUDINARY ---
# Usa los datos que encontraste en tu Dashboard
cloudinary.config( 
  cloud_name = "dvmz2v0zvr", 
  api_key = "297853115656242", 
  api_secret = "TU_API_SECRET_REAL" # <--- PEGA AQUÍ EL QUE VISTE CON EL OJO
)

# CONFIGURACIÓN DE SEGURIDAD
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "241125"

# RUTA DE BASE DE DATOS
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')

def inicializar_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,  -- Aquí ahora guardaremos la URL de la nube
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        con.commit()

@app.route('/')
def login():
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
        # PASO CLAVE: Subir a Cloudinary en lugar de guardar localmente
        resultado = cloudinary.uploader.upload(archivo)
        url_nube = resultado['url'] # Esta URL es eterna
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', (url_nube, mensaje))
            con.commit()
    # Cambié el redirect a 'login' por una respuesta simple o podrías redirigir según tu flujo
    return "✅ Recuerdo guardado para siempre. Regresa y refresca la página."

@app.route('/eliminar/<int:foto_id>', methods=['POST'])
def eliminar(foto_id):
    with sqlite3.connect(DB_PATH) as con:
        # En la nube no es estrictamente necesario borrar el archivo físico 
        # de inmediato, pero eliminamos el registro de tu base de datos.
        con.execute('DELETE FROM galeria WHERE id = ?', (foto_id,))
        con.commit()
    return redirect(url_for('login'))

if _name_ == '_main_':
    inicializar_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
