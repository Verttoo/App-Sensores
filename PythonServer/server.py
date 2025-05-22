from flask import Flask, jsonify, request
import threading
import time

app = Flask(__name__)

# Variáveis para armazenar os dados recebidos do Wokwi
data = {
    "temperatura": None,
    "presenca": None,
    "nivel_oleo": None,
    "porta": None # Adicionei 'porta' conforme seu exemplo, ajuste se não existir
}

# Lock para acesso seguro à variável 'data' se houver múltiplas requisições (boa prática)
data_lock = threading.Lock()

# Não precisamos mais da simulação interna, o Wokwi será a fonte dos dados
# def gerar_dados_simulados():
# global data
# while True:
# # Simula uma temperatura entre 20 e 35 graus Celsius
# data['temperatura'] = round(random.uniform(20.0, 150.0), 1)
# # Simula a presença (0 = ninguém, 1 = alguém detectado)
# data['presenca'] = round(random.randint(0, 10)) # No seu exemplo original era 0-10
# # Simula nível de óleo entre 0% e 100%
# data['nivel_oleo'] = random.randint(0, 100)
#         
# print(f"Simulado: {data}")
# time.sleep(30)  # Atualiza os dados a cada 30 segundos (era 60)

@app.route('/dados', methods=['GET'])
def get_dados():
    with data_lock:
        return jsonify(data)

@app.route('/wokwi_data', methods=['POST'])
def receive_wokwi_data():
    global data
    try:
        received_json = request.get_json()
        if not received_json:
            return jsonify({"status": "erro", "mensagem": "Nenhum dado JSON recebido"}), 400

        print(f"Dados recebidos do Wokwi: {received_json}")

        with data_lock:
            # Atualiza os dados com o que foi recebido, validando as chaves
            if 'temperatura' in received_json:
                data['temperatura'] = received_json.get('temperatura')
            if 'presenca' in received_json:
                data['presenca'] = received_json.get('presenca')
            if 'nivel_oleo' in received_json:
                data['nivel_oleo'] = received_json.get('nivel_oleo')
            if 'porta' in received_json: # Se você tiver o sensor de porta
                data['porta'] = received_json.get('porta')
            
            # Adicione mais campos aqui se necessário

        return jsonify({"status": "sucesso", "mensagem": "Dados recebidos"}), 200
    except Exception as e:
        print(f"Erro ao processar dados do Wokwi: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# Não inicia mais a thread de simulação
# thread = threading.Thread(target=gerar_dados_simulados)
# thread.daemon = True
# thread.start()

if __name__ == '__main__':
    # Use '0.0.0.0' para tornar o servidor acessível na sua rede local
    # O ESP32 no Wokwi precisará do IP da sua máquina que está rodando este script
    app.run(host='0.0.0.0', port=5000, debug=True) # debug=True é útil para desenvolvimento