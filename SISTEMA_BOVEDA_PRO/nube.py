# SISTEMA_BOVEDA_PRO/nube.py
import os
import cloudinary
import cloudinary.uploader

# --- CONFIGURACIÓN DE LA NUBE ---
# Aquí conectamos con Cloudinary usando tus variables de entorno
cloudinary.config( 
  cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.environ.get('CLOUDINARY_API_KEY'), 
  api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
  secure = True
)

def subir_a_la_nube(archivo):
    """
    Recibe un archivo y lo sube a Cloudinary.
    Retorna la URL segura de la imagen.
    """
    try:
        resultado = cloudinary.uploader.upload(archivo)
        return resultado['secure_url']
    except Exception as e:
        print(f"❌ Error al subir a Cloudinary: {e}")
        return None
