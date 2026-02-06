from flask import Flask, render_template, request

app = Flask(__name__)

# AQUÍ ELIGES EL CÓDIGO (Pon algo que ella sepa, como su fecha)
# Por ejemplo: "030226" o una palabra especial
CODIGO_SECRETO = "amor123" 

@app.route('/')
def login():
    # Esta es la primera pantalla que ella verá
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada = request.form.get('codigo')
    if entrada == CODIGO_SECRETO:
        # Si es correcto, la lleva a las fotos
        return render_template('index.html')
    else:
        # Si falla, le da un aviso tierno
        return "Ese no es el código, mi vida. Intenta con nuestra fecha especial. ❤️", 403

if _name_ == '_main_':
    app.run(debug=True)
