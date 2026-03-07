import os
import cloudinary
import cloudinary.uploader
from SISTEMA_BOVEDA_PRO.acceso import get_db_connection

# --- CONFIGURACIÓN CLOUDINARY ---
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

def inicializar_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id SERIAL PRIMARY KEY, archivo TEXT NOT NULL, mensaje TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS notas_amor (
            id SERIAL PRIMARY KEY, contenido TEXT NOT NULL, autor TEXT NOT NULL, categoria TEXT DEFAULT 'General', fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS control_seguridad (
            id SERIAL PRIMARY KEY, session_version INTEGER DEFAULT 1
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS autorizaciones (
            id SERIAL PRIMARY KEY, dispositivo_id TEXT UNIQUE, nombre_equipo TEXT, autorizado BOOLEAN DEFAULT FALSE, es_admin BOOLEAN DEFAULT FALSE
        )''')
        cur.execute("INSERT INTO control_seguridad (id, session_version) SELECT 1, 1 WHERE NOT EXISTS (SELECT 1 FROM control_seguridad WHERE id = 1)")
        conn.commit()
        cur.close()
        conn.close()
