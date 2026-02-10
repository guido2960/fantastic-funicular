import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD (Tus llaves) ---
CODIGO_PUERTA = "eresmilugarseguro23"
CODIGO_AMULETO = "241125" 

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.getcwd()
DB_PATH = os.path.join(BASE_DIR, 'base_datos_pro.db')
# Esto asegura que las fotos se guarden en la carpeta correcta
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'fotos')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def inicializar_db():
    """Crea la tabla si no existe para evitar errores en el celular"""
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
    # El celular a veces envía espacios extra, .strip() los limpia
    entrada_uno = request.form.get('codigo', '').strip()
    entrada_dos = request.form.get('codigo_amuleto', '').strip()

    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        inicializar_db()
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, mensaje FROM galeria ORDER BY id DESC')
            fotos_db = cursor.fetchall()
        # Esto carga la página principal con tus fotos
        return render_template('index.html', fotos=fotos_db, nombre="Mayda")
    else:
        return "🔐 Código incorrecto. Inténtalo de nuevo.", 403

@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo and archivo.filename != '':
        nombre_archivo = archivo.filename
        # Esta línea es la que garantiza que la foto del celular se guarde
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
        
        with sqlite3.connect(DB_PATH) as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', 
                        (nombre_archivo, mensaje))
            con.commit()
            
    return redirect(url_for('login'))

if __name__ == '__main__':
    inicializar_db()
    # Esto permite que el celular se conecte al servidor de Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
