from flask import Flask, request, jsonify
from flask_cors import CORS
from Controlador.controller import Controller
from Controlador.controller import GeneradorPaginas

app = Flask(__name__)
CORS(app)
controller = Controller()

@app.route('/simular', methods=['POST'])
def simular():
    data = request.get_json()
    algoritmo = data.get('algoritmo')
    frames = int(data.get('frames'))
    secuencia_str = data.get('secuencia', '').strip()
    if not secuencia_str:
        return jsonify({'error': 'No se proporcionó una secuencia de páginas.'}), 400
    try:
        secuencia = [int(x) for x in secuencia_str.split(',') if x.strip() != '']
    except ValueError:
        return jsonify({'error': 'Secuencia de páginas inválida.'}), 400
    estado = controller.crear_simulacion(frames, algoritmo, secuencia)
    return jsonify(estado)

@app.route('/avanzar', methods=['POST'])
def avanzar():
    estado = controller.avanzar()
    return jsonify(estado)

@app.route('/retroceder', methods=['POST'])
def retroceder():
    estado = controller.retroceder()
    return jsonify(estado)

@app.route('/estado', methods=['GET'])
def estado():
    return jsonify(controller.get_estado())

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    estado = controller.reiniciar()
    return jsonify(estado)

@app.route('/generar_paginas')
def generar_paginas():
    cantidad = int(request.args.get('cantidad', 15))
    minimo = int(request.args.get('minimo', 0))
    maximo = int(request.args.get('maximo', 9))
    generador = GeneradorPaginas(minimo, maximo)
    paginas = list(generador.generar(cantidad))
    return jsonify({'paginas': paginas})

if __name__ == '__main__':
    import os
    # Detectar si está en Codespaces
    in_codespaces = 'CODESPACES' in os.environ or 'CODESPACE_NAME' in os.environ
    port = int(os.environ.get('PORT', 5000))
    if in_codespaces:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        app.run(debug=True)
    # python /workspaces/Alogritmos-de-Remplazo-de-pagina/api_server.py
