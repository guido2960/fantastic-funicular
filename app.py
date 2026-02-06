@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Mueve la lógica de verificación aquí
        entrada = request.form.get('codigo')
        if entrada == CODIGO_SECRET0:
            return render_template('index.html')
        else:
            return "Ese no es el código...", 403
    return render_template('login.html
