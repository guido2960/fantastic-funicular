import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- 1. CONEXIÓN CON LA NUBE (CLOUDINARY) ---
# Aquí es donde el cerebro se conecta con la bóveda eterna
cloudinary.config( 
  cloud_name = "dvmz2v0zvr", 
  api_key = "297853115656242", 
  api_secret = "PEGA_AQUI_TU_CODIGO_QN_SIN_ESPACIOS" 
)

# --- 2. CONFIGURACIÓN DE SEGURIDAD ---
# Los códigos que protegen tu compromiso con Mayda
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "241125"
DB_PATH = os.path.join(os.getcwd(), 'base_datos_pro.db')

def inicializar_db():
    """Crea la base de datos si no existe"""
    with sqlite3.connect(DB_PATH) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            archivo TEXT NOT NULL,
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        con.commit()

# --- 3. RUTAS DE LA APLICACIÓN ---

@app.route('/')
def login():
    """Pantalla de entrada para Mayda"""
    return render_template('login.html', saludo="Hola Mayda ❤️‍🩹")

@app.route('/verificar', methods=['POST'])
def verificar():
    """Verifica el acceso con tus códigos especiales"""
    entrada_uno = request.form.get('codigo', '').strip()
    entrada_dos = request.form.get('codigo_amuleto', '').strip()

    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        inicializar_db()
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            # Traemos las fotos de la base de datos
            cursor.execute('SELECT archivo, mensaje, id FROM galeria ORDER BY id DESC')
            fotos_db = cursor.fetchall()
        return render_template('index.html', fotos=fotos_db, nombre="Mayda")
    return "🔐 Código incorrecto, amor. Inténtalo de nuevo.", 403

@app.route('/subir', methods=['POST'])
def subir():
    """Sube la foto a la nube y guarda el link en la base de datos"""
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo and archivo.filename != '':
        # Integración suave: Subida directa a Cloudinary
        res = cloudinary.uploader.upload(archivo)
        url_nube = res['url'] # El link eterno
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', (url_nube, mensaje))
            con.commit()
            
    return redirect(url_for('login'))

@app.route('/eliminar/<int:foto_id>', methods=['POST'])
def eliminar(foto_id):
    """Borra el recuerdo de la lista"""
    with sqlite3.connect(DB_PATH) as con:
        con.execute('DELETE FROM galeria WHERE id = ?', (foto_id,))
        con.commit()
    return redirect(url_for('login'))

# --- 4. ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    inicializar_db()
    # Render asignará el puerto automáticamente
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
