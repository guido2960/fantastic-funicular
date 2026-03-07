# SISTEMA_BOVEDA_PRO/notas.py
from flask import request, redirect, url_for
from SISTEMA_BOVEDA_PRO.database import get_db_connection

def crear_nota():
    """Captura los datos del formulario y guarda una nueva nota de amor"""
    autor = request.form.get('autor_nombre')
    contenido = request.form.get('contenido_nota')
    modo = request.form.get('modo_nota', 'General')
    
    if contenido and autor:
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO notas_amor (autor, contenido, categoria) VALUES (%s, %s, %s)', 
                (autor, contenido, modo)
            )
            conn.commit()
        except Exception as e:
            print(f"❌ Error al guardar nota: {e}")
        finally:
            cur.close()
            conn.close()
            
    return redirect(url_for('boveda'))

def borrar_nota(id):
    """Elimina una nota específica usando su ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM notas_amor WHERE id = %s', (id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Error al eliminar nota: {e}")
    finally:
        cur.close()
        conn.close()
        
    return redirect(url_for('boveda'))
