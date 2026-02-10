import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# TUS DOS LLAVES (La puerta y el amuleto)
CODIGO_PUERTA = "amor123"
CODIGO_AMULETO = "2411" # Este es tu código del amuleto [cite: 2026-01-27]

app.config['UPLOAD_FOLDER'] = 'static/uploads/fotos'

def inicializar_db():
    # Creamos la base de datos de élite
    with sqlite3.connect('base_datos_pro.db') as con:
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
    # Recibimos ambos códigos de tu formulario
    entrada_uno = request.form.get('codigo')
    entrada_dos = request.form.get('codigo_amuleto') 

    # VERIFICACIÓN: Si ambos códigos son correctos
    if entrada_uno == CODIGO_PUERTA and entrada_dos == CODIGO_AMULETO:
        # Aquí INCLUIMOS la lectura de la galería
        with sqlite3.connect('base_datos_pro.db') as con:
            cursor = con.cursor()
            cursor.execute('SELECT archivo, mensaje FROM galeria ORDER BY fecha DESC')
            fotos = cursor.fetchall()
        
        # Entramos al index.html pasando los datos de las fotos
        return render_template('index.html', fotos=fotos)
    else:
        return "Código incorrecto, intenta de nuevo.", 403

# Esta ruta es nueva, sirve para INCLUIR fotos desde tu celular o PC
@app.route('/subir', methods=['POST'])
def subir():
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario')
    
    if archivo:
        nombre_archivo = archivo.filename
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
        
        with sqlite3.connect('base_datos_pro.db') as con:
            con.execute('INSERT INTO galeria (archivo, mensaje) VALUES (?, ?)', 
                        (nombre_archivo, mensaje))
            
    return redirect(url_for('login')) # Regresa al inicio por seguridad

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)
