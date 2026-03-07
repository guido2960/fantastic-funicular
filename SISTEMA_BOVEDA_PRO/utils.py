# SISTEMA_BOVEDA_PRO/utils.py

def formatear_respuesta(mensaje, exito=True):
    """Genera un mensaje estandarizado para la consola o interfaz"""
    prefijo = "✅" if exito else "❌"
    return f"{prefijo} {mensaje}"

def limpiar_texto(texto):
    """Elimina espacios innecesarios de las entradas del usuario"""
    return texto.strip() if texto else ""
