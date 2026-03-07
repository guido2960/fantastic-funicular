# SISTEMA_BOVEDA_PRO/autorizar.py
from flask import redirect, url_for
from SISTEMA_BOVEDA_PRO.database import get_db_connection

def aprobar_dispositivo(id):
    """
    Cambia el estado de un dispositivo a 'autorizado' en la base de datos.
    Se usa desde el panel de administración.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE autorizaciones SET autorizado = True WHERE id = %s", (id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Error al autorizar: {e}")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('panel_admin'))
