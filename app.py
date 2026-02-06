from flask import Flask, render_template, request

app = Flask(_name_)

# Definimos una única contraseña
CODIGO_SECRETO = "amor123"

@app.route('/')
def login():
    # Esta es la página que verá Mayda al principio
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    # Captura lo que escriban en el formulario
    entrada = request.form.get('codigo')
    
    # Compara con tu única contraseña
    if entrada == CODIGO_SECRETO:
        return render_template('index.html')
    else:
        # Si se equivoca, regresa al login (puedes cambiar este mensaje)
        return "Código incorrecto. Intenta de nuevo.", 403

if _name_ == '_main_':
    app.run(debug=True)
