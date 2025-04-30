# server_simulado.py
from flask import Flask, jsonify
import threading
import time
import random

app = Flask(__name__)

# Variáveis para armazenar os dados simulados
data = {
    "temperatura": None,
    "nivel_agua": None,
    "nivel_oleo": None,
    "porta": None
}

def gerar_dados_simulados():
    global data
    while True:
        # Simula uma temperatura entre 20 e 35 graus Celsius
        data['temperatura'] = round(random.uniform(89, 90), 1)
        # Simula a presença (0 = ninguém, 1 = alguém detectado)
        data['nivel_agua'] = round(random.randint(80, 100))
        # Simula nível de óleo entre 0% e 100%
        data['nivel_oleo'] = random.randint(60, 100)

        data['bateria'] = random.randint(60, 100)
       
        print(f"Simulado: {data}")
        time.sleep(1)  # Atualiza os dados a cada 60 segundos

@app.route('/dados', methods=['GET'])
def get_dados():
    return jsonify(data)

# Inicia a thread de simulação
thread = threading.Thread(target=gerar_dados_simulados)
thread.daemon = True
thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


    