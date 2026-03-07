# SISTEMA_BOVEDA_PRO/galeria.py
from flask import request, redirect, url_for
from SISTEMA_BOVEDA_PRO.database import get_db_connection
from SISTEMA_BOVEDA_PRO.nube import subir_a_la_nube

def ejecutar_subida():
    """Captura la foto del formulario, la sube a la nube y guarda la URL en la DB"""
    archivo = request.files.get('foto_usuario')
    mensaje = request.form.get('mensaje_usuario', '') 
    
    if archivo:
        # Usamos la función que creamos en nube.py
        url_segura = subir_a_la_nube(archivo)
        
        if url_segura:
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    'INSERT INTO galeria (archivo, mensaje) VALUES (%s, %s)', 
                    (url_segura, mensaje)
                )
                conn.commit()
            except Exception as e:
                print(f"❌ Error al guardar en DB: {e}")
            finally:
                cur.close()
                conn.close()
                
    return redirect(url_for('boveda'))

def eliminar_foto(id):
    """Borra el registro de la foto de la base de datos"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM galeria WHERE id = %s', (id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Error al eliminar foto: {e}")
    finally:
        cur.close()
        conn.close()
        
    return redirect(url_for('boveda'))
