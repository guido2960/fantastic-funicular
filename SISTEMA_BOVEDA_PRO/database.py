# SISTEMA_BOVEDA_PRO/database.py
import os
import psycopg2

def get_db_connection():
    """Establece la conexión con la base de datos PostgreSQL"""
    url = os.environ.get('DATABASE_URL')
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def inicializar_db():
    """Crea las tablas necesarias si no existen (Galeria, Notas, Seguridad)"""
    conn = get_db_connection()
    if conn:
        print("🛠️ Verificando y creando tablas...")
        cur = conn.cursor()
        
        # Tabla para las fotos de la galería
        cur.execute('''CREATE TABLE IF NOT EXISTS galeria (
            id SERIAL PRIMARY KEY, 
            archivo TEXT NOT NULL, 
            mensaje TEXT, 
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Tabla para tus notas de amor
        cur.execute('''CREATE TABLE IF NOT EXISTS notas_amor (
            id SERIAL PRIMARY KEY, 
            contenido TEXT NOT NULL, 
            autor TEXT NOT NULL, 
            categoria TEXT DEFAULT 'General', 
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Tablas de control y dispositivos
        cur.execute('''CREATE TABLE IF NOT EXISTS control_seguridad (
            id SERIAL PRIMARY KEY, 
            session_version INTEGER DEFAULT 1
        )''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS autorizaciones (
            id SERIAL PRIMARY KEY, 
            dispositivo_id TEXT UNIQUE, 
            nombre_equipo TEXT, 
            autorizado BOOLEAN DEFAULT FALSE, 
            es_admin BOOLEAN DEFAULT FALSE
        )''')
        
        # Insertar registro inicial de seguridad si no existe
        cur.execute("INSERT INTO control_seguridad (id, session_version) SELECT 1, 1 WHERE NOT EXISTS (SELECT 1 FROM control_seguridad WHERE id = 1)")
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Base de datos lista.")
