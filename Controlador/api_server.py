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
    secuencia = [int(x) for x in data.get('secuencia').split(',')]
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
    app.run(debug=True)
