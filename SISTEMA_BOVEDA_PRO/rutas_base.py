# SISTEMA_BOVEDA_PRO/rutas_base.py
from flask import render_template, redirect, url_for, session, request
from SISTEMA_BOVEDA_PRO import acceso

def mostrar_login():
    """Muestra la página inicial de login"""
    return render_template('login.html')

def ejecutar_verificacion():
    """Comprueba si el correo y la clave coinciden con las llaves maestras"""
    entrada_email = request.form.get('correo', '').strip()
    entrada_clave = request.form.get('clave', '').strip()
    
    # Usamos las constantes de acceso.py
    if entrada_email == acceso.USUARIO_ACCESO and entrada_clave == acceso.CLAVE_ACCESO:
        session['user_email'] = entrada_email
        return redirect(url_for('intro'))
    
    return "🔐 Acceso denegado.", 403

def mostrar_intro():
    """Muestra la pantalla de introducción si hay sesión activa"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('intro.html')
