from flask import Flask, render_template, request

app = Flask(__name__)

CODIGO_SECRETO = "amor123"

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    entrada = request.form.get('codigo')
    if entrada == CODIGO_SECRETO:
        return render_template('index.html')
    else:
        return "Código incorrecto, intenta de nuevo.", 403

if __name__ == '__main__':
    app.run(debug=True)
